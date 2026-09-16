"""Live adapter: builds the same RecordState from a real endpoint.

The address is a parameter and is never hard-coded. Per DM, 14 September 2026,
the address must not acquire constitutional significance unless an instrument
already specifies one, and none does.

    PUBLIC_VERSION_RECORD_URL=https://example/…/charter  python3 run_acceptance.py

HONEST LIMIT ON REQUIREMENT 8. Whether prior entries can be silently replaced is
a property of the record over time and cannot be established by one fetch. This
adapter therefore does two things and distinguishes them:

  - it reads whatever immutability mechanism the record declares (version-
    addressed entries carrying digests, and an external anchor for those
    digests), which is an ASSERTION;
  - it compares the digests it sees against a stored snapshot from an earlier
    run, which is an OBSERVATION.

With no prior snapshot, the mutability limb of check 8 is reported as not yet
observed rather than passed. A record cannot prove it has never been silently
revised on the day it is created; it earns that over time, which is the correct
result and not a defect in the test.
"""

import json
import os
import urllib.request
import urllib.error

from model import RecordState, VersionEntry

SNAPSHOT = os.environ.get("PVR_SNAPSHOT", "pvr_snapshot.json")
INDEX_SUFFIX = os.environ.get("PVR_INDEX_SUFFIX", "/index.json")


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)
    except Exception as e:  # DNS failure, TLS failure, refused connection
        return 0, str(e).encode(), {}


def fetch(base_url, control_url=None):
    """Build a RecordState from the endpoint. control_url, if given, is any other
    path on the same host: a body byte-identical to the control is the host's
    generic response, not the record. That is the 8 September signature."""
    status, body, _ = _get(base_url)

    generic = False
    if control_url:
        c_status, c_body, _ = _get(control_url)
        generic = (body == c_body and len(body) > 0)

    st = RecordState(
        http_status=status,
        body_is_generic_host_response=generic,
        unauthenticated_status=status,
        requires_auth=status in (401, 403) or (300 <= status < 400),
    )
    if status != 200:
        return st

    i_status, i_body, _ = _get(base_url.rstrip("/") + INDEX_SUFFIX)
    if i_status != 200:
        # No machine-readable index. Checks 2 to 6 and 9 cannot be evaluated and
        # will fail on absent entries, which is the correct outcome: a record a
        # machine cannot read is not a control.
        return st

    try:
        idx = json.loads(i_body.decode("utf-8"))
    except Exception:
        return st

    for e in idx.get("versions", []):
        st.entries.append(VersionEntry(
            version=e.get("version"),
            instrument_date=e.get("instrument_date"),
            published_to_record=e.get("published_to_record"),
            reason=e.get("reason"),
            revision_class=e.get("revision_class"),
            is_current=bool(e.get("is_current")),
            superseded_by=e.get("superseded_by"),
            superseded_from=e.get("superseded_from"),
            entry_url=e.get("entry_url"),
            content_digest=e.get("content_digest"),
        ))

    # Fetch every archive entry. The index listing a version says the record
    # CLAIMS to hold it; only fetching says it is still there and still serves
    # the recorded bytes. Checks 2 to 6 would all pass while every entry 404s.
    import hashlib
    from urllib.parse import urljoin
    for e in st.entries:
        if not e.entry_url:
            continue
        e_status, e_body, _ = _get(urljoin(base_url, e.entry_url))
        e.entry_resolves = (e_status == 200)
        if e.entry_resolves:
            e.retrieved_digest = "sha256:" + hashlib.sha256(e_body).hexdigest()

    st.change_events_dated = all(
        e.published_to_record for e in st.entries
    ) and bool(idx.get("change_log_dated", False))

    # Assertion limb: are entries version-addressed, digested, and anchored?
    digested = st.entries and all(e.entry_url and e.content_digest for e in st.entries)
    anchored = bool(idx.get("external_anchor"))
    st.prior_state_retrievable = bool(digested)

    # Comparison is against the ACCEPTED BASELINE, never against the last thing
    # seen. Before 14 September 2026 every fetch overwrote the stored digests,
    # including a fetch that had just detected an alteration, so running the
    # suite twice against an altered record made it pass. That is fixed by
    # never writing the baseline here: the runner calls record_observation()
    # after the checks, and only a clean run advances it.
    base = _load_baseline()
    if base is None:
        st.baseline_versions = None
        st.prior_entry_bytes_mutable = True
        st._mutability_observed = False
    else:
        st.baseline_versions = sorted(base)
        present = {e.version for e in st.entries}
        st.missing_since_baseline = sorted(v for v in base if v not in present)
        st.digest_mismatches = sorted(
            v for v, d in base.items()
            if st.by_version(v) and st.by_version(v).content_digest != d)
        st.prior_entry_bytes_mutable = bool(st.digest_mismatches)
        st._mutability_observed = True

    return st


def record_observation(st, clean):
    """Write the observation log, and advance the accepted baseline ONLY on a
    clean run.

    `clean` is the runner's verdict on the preservation checks (8, 10, 11, 12).
    A run that failed any of them leaves the baseline where it was, so the next
    run compares against the same accepted state and fails again. Accepting a
    changed archive is then a deliberate act, not a consequence of running the
    test a second time: set PVR_ACCEPT_BASELINE=1.
    """
    import datetime
    snap = _load_raw()
    # What was accepted BEFORE this observation. Every write below is checked
    # against it: no code path may narrow an established baseline except an
    # explicit operator acceptance. See _assert_baseline_not_weakened.
    before = dict((snap.get("accepted") or {}).get("versions") or {})
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    seen = {e.version: e.content_digest for e in st.entries if e.content_digest}

    snap.setdefault("observations", [])
    snap["observations"].append({
        "at": now, "clean": bool(clean),
        "versions": sorted(seen),
        "digest_mismatches": st.digest_mismatches,
        "missing_since_baseline": st.missing_since_baseline,
    })
    snap["observations"] = snap["observations"][-50:]

    snap["schema"] = SCHEMA
    accepted = snap.get("accepted")
    forced = os.environ.get("PVR_ACCEPT_BASELINE") == "1"

    if not seen:
        # Nothing digestible was observed. Two cases, and conflating them is how
        # v6 lost an established baseline to nothing worse than an empty index:
        # this branch popped 'accepted' unconditionally, so serving no versions
        # reset the store and the next altered archive became the new baseline.
        if accepted is None:
            # Never accepted anything. INITIALISING is the honest state, and it
            # is declared rather than inferred from an empty accepted block.
            snap.pop("accepted", None)
            snap["state"] = STATE_INITIALISING
            _save_raw(snap)
            return ("baseline NOT established: no entry digests were observed; "
                    "store left initialising")
        # An established baseline exists. An empty or failed observation is a
        # finding about the RECORD, never a reason to forget what was accepted.
        snap["state"] = STATE_ESTABLISHED
        _save_raw(snap, before=before)
        return ("baseline HELD: no entry digests were observed; "
                "the existing accepted baseline is preserved")

    if accepted is None:
        snap["accepted"] = {"versions": seen, "at": now, "reason": "first observation"}
        note = "baseline established"
    elif forced:
        snap["accepted"] = {"versions": seen, "at": now, "reason": "PVR_ACCEPT_BASELINE=1"}
        note = "baseline replaced by explicit operator acceptance"
    elif clean:
        # A clean run may add versions published since the baseline; it may not
        # drop or alter one, because then it would not have been clean.
        merged = dict(accepted.get("versions", {}))
        merged.update(seen)
        snap["accepted"] = {"versions": merged, "at": now, "reason": "clean observation"}
        note = "baseline advanced"
    else:
        note = "baseline HELD: observation was not clean"

    snap["state"] = STATE_ESTABLISHED
    _save_raw(snap, before=None if forced else before)
    return note


class BaselineError(Exception):
    """The baseline store is unusable. Never downgraded to 'no baseline'.

    Found 14 September 2026, twice. First: a corrupted file was caught by a bare
    except and returned as {}, so an altered archive was accepted as a first
    observation. Then: valid-JSON forms such as {}, {"accepted": null} and an
    empty versions map still read as 'no baseline', so the comparison history
    could be erased without any error at all.

    Only a GENUINELY ABSENT FILE means first run. An existing store must carry a
    valid non-empty accepted baseline, or the explicit INITIALISING state below.
    """


SCHEMA = "pvr-baseline/1"
STATE_INITIALISING = "initialising"   # store exists; nothing accepted yet
STATE_ESTABLISHED = "established"     # store carries an accepted baseline


def _load_raw():
    """Return the stored dict, or {} if the file genuinely does not exist.

    Every other condition raises. There is deliberately no shape of existing
    file that quietly means 'start again': an operator who wants that deletes
    the file, which is a visible act.
    """
    if not os.path.exists(SNAPSHOT):
        return {}
    try:
        with open(SNAPSHOT, "rb") as f:
            raw = f.read()
    except OSError as e:
        raise BaselineError(f"baseline file {SNAPSHOT} exists but cannot be read: {e}")
    if not raw.strip():
        raise BaselineError(f"baseline file {SNAPSHOT} exists but is empty")
    try:
        d = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise BaselineError(f"baseline file {SNAPSHOT} is not valid JSON: {e}")
    if not isinstance(d, dict):
        raise BaselineError(f"baseline file {SNAPSHOT} is not an object: got {type(d).__name__}")

    if d.get("schema") != SCHEMA:
        raise BaselineError(
            f"baseline file {SNAPSHOT} is not a {SCHEMA} store "
            f"(schema={d.get('schema')!r}). An unrecognised store is not an empty one")

    state = d.get("state")
    if state not in (STATE_INITIALISING, STATE_ESTABLISHED):
        raise BaselineError(
            f"baseline file {SNAPSHOT} has state {state!r}; expected "
            f"{STATE_INITIALISING!r} or {STATE_ESTABLISHED!r}")

    acc = d.get("accepted")
    if state == STATE_ESTABLISHED:
        if not isinstance(acc, dict):
            raise BaselineError(
                f"baseline file {SNAPSHOT} is {STATE_ESTABLISHED} but 'accepted' is "
                f"{type(acc).__name__}; an established store must carry a baseline")
        versions = acc.get("versions")
        if not isinstance(versions, dict) or not versions:
            raise BaselineError(
                f"baseline file {SNAPSHOT} is {STATE_ESTABLISHED} but "
                f"'accepted.versions' is empty or not an object. An established store "
                f"with no versions would silently reset the comparison history")
        bad = [k for k, v in versions.items()
               if not isinstance(k, str) or not isinstance(v, str) or not v]
        if bad:
            raise BaselineError(
                f"baseline file {SNAPSHOT} has malformed version entries: {', '.join(map(repr, bad[:5]))}")
    else:
        if acc not in (None, {}):
            raise BaselineError(
                f"baseline file {SNAPSHOT} is {STATE_INITIALISING} but carries an "
                f"'accepted' block; that is contradictory")
    return d


def _load_baseline():
    """The accepted baseline: {version: digest}, or None.

    None means one of exactly two things: the file is genuinely absent, or the
    store is explicitly INITIALISING. It never means the store was unreadable,
    malformed, or carrying an empty accepted block; all of those raise.
    """
    d = _load_raw()
    if not d:
        return None                      # genuinely absent
    if d.get("state") == STATE_INITIALISING:
        return None                      # explicit, declared, not inferred
    return d["accepted"]["versions"]      # validated non-empty by _load_raw


def _assert_baseline_not_weakened(before, snap):
    """An established baseline may GROW. It may not shrink, it may not revert to
    initialising, and the accepted digest of a retained version may not change.

    The digest limb was added on DM's finding of 14 September 2026: the guard
    protected membership and state but not the accepted value for each retained
    version, so a direct write could silently rewrite what the record is being
    compared against. The normal path is protected anyway, because a changed
    digest makes check 8 fail and the run is not clean. This closes the guard
    itself rather than relying on that.

    This is a defensive invariant, not a check on the record. It exists because
    the defect it guards was introduced by a fix: on 14 September 2026 the
    initialisation branch popped 'accepted' whenever an observation saw no
    entries, so an empty index silently discarded the comparison history. Shape
    validation could not catch that; only an invariant across the transition
    can. An explicit operator acceptance (PVR_ACCEPT_BASELINE=1) passes
    before=None and is exempt, because that is a deliberate act.
    """
    if not before:
        return
    if snap.get("state") != STATE_ESTABLISHED:
        raise BaselineError(
            f"internal invariant: an established baseline of {len(before)} versions "
            f"would be reverted to {snap.get('state')!r}. Refusing to write")
    after = (snap.get("accepted") or {}).get("versions") or {}
    lost = sorted(v for v in before if v not in after)
    if lost:
        raise BaselineError(
            f"internal invariant: writing would drop accepted versions "
            f"{', '.join(lost)}. Refusing to write")
    changed = sorted(f"{v} {before[v]} -> {after[v]}" for v in before
                     if after.get(v) != before[v])
    if changed:
        raise BaselineError(
            f"internal invariant: writing would change the accepted digest of a "
            f"retained version: {'; '.join(changed)}. Refusing to write")


def _save_raw(snap, before=None):
    """Replace the store atomically, and never swallow a failure.

    Two defects fixed on 14 September 2026: a failed write was caught and
    ignored, so the adapter reported 'baseline established' when no file had
    been created; and the store was written in place, so an interrupted write
    could destroy the previous baseline. The temp file is created in the same
    directory so os.replace is a rename within one filesystem, which is atomic.
    """
    import tempfile
    _assert_baseline_not_weakened(before, snap)
    target = os.path.abspath(SNAPSHOT)
    d = os.path.dirname(target) or "."
    if not os.path.isdir(d):
        raise BaselineError(f"cannot write baseline: directory does not exist: {d}")
    body = json.dumps(snap, indent=2)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".pvr_baseline.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(body)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)
    except OSError as e:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise BaselineError(f"cannot write baseline to {target}: {e}")

    # Read back. A write that reports success and produced nothing readable is
    # the defect this guards against.
    try:
        with open(target) as f:
            back = json.load(f)
    except (OSError, ValueError) as e:
        raise BaselineError(f"baseline written to {target} but not readable back: {e}")
    if back.get("accepted") != snap.get("accepted"):
        raise BaselineError(f"baseline written to {target} does not read back as written")
