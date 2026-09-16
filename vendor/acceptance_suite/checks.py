"""Acceptance checks for the public version record.

Eight from DM's requirements of 13 September 2026, plus one ninth derived from
his instruction not to backfill publication dates. The ninth is marked as an
addition and is not treated as ratified.

Each check is a function of (RecordState, Spec) returning a Result. No check
reads the network; the live adapter builds the RecordState.
"""

from dataclasses import dataclass, field
from model import Result


@dataclass
class Spec:
    """Parameters, so no address or lineage is hard-coded into the control."""

    # The lineage the record must expose, oldest first.
    lineage: list = field(default_factory=lambda: ["v1", "v1.1", "v2", "v3"])
    expected_current: str = "v3"
    # The date the record itself was established. No version may claim to have
    # been published to this record before this date.
    record_established_on: str = None  # ISO date, e.g. "2026-09-20"


def _cls_from_version(v):
    """A version string's own shape says which class it is. v1.1 is a minor
    decimal revision; v1, v2, v3 are whole integers. The record must DECLARE
    the class; this function only says what the declaration should be."""
    return "minor_decimal" if "." in v.lstrip("v") else "whole_integer"


# --- 1 ----------------------------------------------------------------------
def check_resolves(st, spec):
    """Resolves at the address required, unauthenticated, with the record's own
    body. Known-bad: the 8 September state, 404 byte-identical to a control."""
    if st.http_status != 200:
        return Result("1 resolves", False, f"HTTP {st.http_status}")
    if st.body_is_generic_host_response:
        return Result("1 resolves", False, "body is the host's generic response, not the record")
    return Result("1 resolves", True)


# --- 2 ----------------------------------------------------------------------
def check_current_version_identified(st, spec):
    """Exactly one version is marked current and it is the expected one."""
    cur = st.current()
    if len(cur) == 0:
        return Result("2 current version", False, "no version marked current")
    if len(cur) > 1:
        return Result("2 current version", False,
                      "more than one marked current: " + ", ".join(e.version for e in cur))
    if cur[0].version != spec.expected_current:
        return Result("2 current version", False,
                      f"current is {cur[0].version}, expected {spec.expected_current}")
    return Result("2 current version", True, cur[0].version)


# --- 3 ----------------------------------------------------------------------
def check_prior_versions_exposed(st, spec):
    """Every version in the lineage is present, each with its instrument date."""
    missing = [v for v in spec.lineage if st.by_version(v) is None]
    if missing:
        return Result("3 prior versions", False, "absent: " + ", ".join(missing))
    undated = [e.version for e in st.entries if not e.instrument_date]
    if undated:
        return Result("3 prior versions", False, "no instrument date: " + ", ".join(undated))
    return Result("3 prior versions", True, f"{len(spec.lineage)} versions")


# --- 4 ----------------------------------------------------------------------
def check_amendment_reasons(st, spec):
    """A reason against every transition, not only the latest. The first issue
    is not a transition and is exempt."""
    if not st.entries:
        return Result("4 amendment reasons", False, "no entries; nothing to test")
    first = spec.lineage[0]
    bad = [e.version for e in st.entries
           if e.version != first and not (e.reason or "").strip()]
    if bad:
        return Result("4 amendment reasons", False, "no reason: " + ", ".join(bad))
    return Result("4 amendment reasons", True)


# --- 5 ----------------------------------------------------------------------
def check_version_semantics(st, spec):
    """Whole-integer and minor-decimal revisions are distinguishable on the
    record itself. A flat list that renders v1.1 and v2 as equivalent steps
    fails, which is the point: §9 draws the distinction."""
    if not st.entries:
        return Result("5 version semantics", False, "no entries; nothing to test")
    undeclared = [e.version for e in st.entries if not e.revision_class]
    if undeclared:
        return Result("5 version semantics", False,
                      "class not declared: " + ", ".join(undeclared))
    wrong = [f"{e.version} declared {e.revision_class}" for e in st.entries
             if e.revision_class != _cls_from_version(e.version)]
    if wrong:
        return Result("5 version semantics", False, "; ".join(wrong))
    return Result("5 version semantics", True)


# --- 6 ----------------------------------------------------------------------
def check_supersession_explicit(st, spec):
    """Every non-current version says which version superseded it and from when.
    Absence from the list is not a statement of supersession."""
    bad = []
    if not st.entries:
        return Result("6 supersession", False, "no entries; nothing to test")
    for e in st.entries:
        if e.is_current:
            continue
        if not e.superseded_by or not e.superseded_from:
            bad.append(e.version)
    if bad:
        return Result("6 supersession", False, "not marked superseded: " + ", ".join(bad))
    return Result("6 supersession", True)


# --- 7 ----------------------------------------------------------------------
def check_unauthenticated_retrieval(st, spec):
    """Retrievable by a counterparty with no relationship to Arkaya. This is the
    requirement an internal register can never satisfy, however complete."""
    if st.requires_auth:
        return Result("7 unauthenticated", False, "authentication required")
    if st.unauthenticated_status not in (None, 200):
        return Result("7 unauthenticated", False,
                      f"unauthenticated fetch returned {st.unauthenticated_status}")
    return Result("7 unauthenticated", True)


# --- 8 ----------------------------------------------------------------------
def check_no_silent_revision(st, spec):
    """The §9 prohibition, tested as a property of the record's storage rather
    than of anything the record asserts about itself.

    Three ways to fail, all of which DM named:
      - the current page is overwritten and no prior version is retained;
      - prior versions are retrievable but their bytes can be silently replaced;
      - changes happen without a dated change event.
    """
    fails = []
    if not st.prior_state_retrievable:
        fails.append("no prior state retained")
    if st.prior_entry_bytes_mutable:
        fails.append("prior entries can be replaced in place")
    if not st.change_events_dated:
        fails.append("changes not dated")
    if fails:
        return Result("8 no silent revision", False, "; ".join(fails))
    return Result("8 no silent revision", True)


# --- 9 (addition, not ratified) ---------------------------------------------
def _parse_date(v):
    """ISO date or nothing. String comparison on dates is how 'not-a-date'
    passed an earliest-permitted-date test on 14 September 2026: lexically it
    sorts after any 2026 date."""
    from datetime import date
    if not isinstance(v, str):
        return None
    try:
        return date.fromisoformat(v)
    except ValueError:
        return None


def check_date_consistency(st, spec):
    """DATE CONSISTENCY. Not historical truth.

    ADDITION to DM's eight, from his instruction not to backfill publication
    dates, and renamed on his correction of 14 September 2026.

    What this establishes: every date is a well-formed ISO date; no version
    claims to have been published to the record before the record existed; and
    no version claims publication before the instrument itself is dated.

    What it does NOT establish: that any stated date is true. A record can pass
    every limb here and still state dates that never happened. Truth needs a
    witness, not a format check.
    """
    if not st.entries:
        return Result("9 date consistency", False, "no entries; nothing to test")
    if not spec.record_established_on:
        return Result("9 date consistency", False,
                      "spec.record_established_on not set; cannot test")
    established = _parse_date(spec.record_established_on)
    if established is None:
        return Result("9 date consistency", False,
                      f"spec.record_established_on is not an ISO date: {spec.record_established_on!r}")

    missing, malformed, early, inverted = [], [], [], []
    for e in st.entries:
        for label, raw in (("instrument_date", e.instrument_date),
                           ("published_to_record", e.published_to_record)):
            if not raw:
                missing.append(f"{e.version}.{label}")
            elif _parse_date(raw) is None:
                malformed.append(f"{e.version}.{label}={raw!r}")
        pub, inst = _parse_date(e.published_to_record), _parse_date(e.instrument_date)
        if pub and pub < established:
            early.append(f"{e.version} claims {e.published_to_record}")
        if pub and inst and pub < inst:
            inverted.append(f"{e.version} published {e.published_to_record} before instrument {e.instrument_date}")

    if missing:
        return Result("9 date consistency", False, "absent: " + ", ".join(missing))
    if malformed:
        return Result("9 date consistency", False, "not an ISO date: " + ", ".join(malformed))
    if early:
        return Result("9 date consistency", False,
                      "before the record existed: " + "; ".join(early))
    if inverted:
        return Result("9 date consistency", False, "; ".join(inverted))
    return Result("9 date consistency", True, f"{len(st.entries)} entries")


# --- 10 (availability) ------------------------------------------------------
def check_entries_retrievable(st, spec):
    """AVAILABILITY. Every archive entry actually resolves.

    Added 14 September 2026. The index listing a version says the record claims
    to hold it; only fetching the entry says it is still there. Checks 2 to 6
    read the index and would all pass while every archive entry 404s.
    """
    if not st.entries:
        return Result("10 entries retrievable", False, "no entries")
    nourl = [e.version for e in st.entries if not e.entry_url]
    if nourl:
        return Result("10 entries retrievable", False,
                      "no entry URL: " + ", ".join(nourl))
    unattempted = [e.version for e in st.entries if e.entry_resolves is None]
    if unattempted:
        return Result("10 entries retrievable", False,
                      "not fetched: " + ", ".join(unattempted))
    gone = [e.version for e in st.entries if e.entry_resolves is False]
    if gone:
        return Result("10 entries retrievable", False, "does not resolve: " + ", ".join(gone))
    return Result("10 entries retrievable", True, f"{len(st.entries)} entries")


# --- 11 (identity) ----------------------------------------------------------
def check_entry_digests_match(st, spec):
    """IDENTITY. Retrieved bytes match the digest the record states for them.

    Separate from check 10 on the same principle that separates content from
    storage: an entry that resolves but serves different bytes is a different
    failure from an entry that has gone, and one result that could mean either
    cannot say which.
    """
    fetched = [e for e in st.entries if e.entry_resolves]
    if not fetched:
        return Result("11 entry digests match", False, "nothing retrieved to compare")
    nodigest = [e.version for e in fetched if not e.content_digest]
    if nodigest:
        return Result("11 entry digests match", False,
                      "no digest recorded: " + ", ".join(nodigest))
    missing = [e.version for e in fetched if not e.retrieved_digest]
    if missing:
        return Result("11 entry digests match", False,
                      "retrieved digest not computed: " + ", ".join(missing))
    bad = [f"{e.version}" for e in fetched if e.retrieved_digest != e.content_digest]
    if bad:
        return Result("11 entry digests match", False, "digest mismatch: " + ", ".join(bad))
    return Result("11 entry digests match", True, f"{len(fetched)} entries")


# --- 12 (completeness, between observations) --------------------------------
def check_membership_retained(st, spec):
    """COMPLETENESS, between observations. Every version present when the
    baseline was accepted is still listed now.

    Added 14 September 2026. Check 3 tests membership against the CONFIGURED
    lineage, so a version outside that lineage could be removed from index and
    archive together and escape every check. Check 8 compared digests only for
    versions still present, so it could not see a removal either. This check
    compares previous and current membership explicitly and depends on no
    configured expectation.

    A retained earlier inventory is enough for this. Chaining and external
    witnessing add assurance; they are not prerequisites for detecting removal
    between two observations you made yourself.
    """
    if st.baseline_versions is None:
        return Result("12 membership retained", False,
                      "no prior inventory; removal cannot be detected on a first observation")
    if st.missing_since_baseline:
        return Result("12 membership retained", False,
                      "present at baseline, absent now: " + ", ".join(st.missing_since_baseline))
    return Result("12 membership retained", True,
                  f"{len(st.baseline_versions)} versions still listed")


ALL_CHECKS = [
    check_resolves,
    check_current_version_identified,
    check_prior_versions_exposed,
    check_amendment_reasons,
    check_version_semantics,
    check_supersession_explicit,
    check_unauthenticated_retrieval,
    check_no_silent_revision,
    check_date_consistency,
    check_entries_retrievable,
    check_entry_digests_match,
    check_membership_retained,
]
