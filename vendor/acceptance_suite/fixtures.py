"""Fixtures for the public version record acceptance suite.

One golden record that should pass every check, and one known-bad per check,
each derived from the golden by a single mutation so the check under test is
isolated. A check that fails the golden, or passes its known-bad, is not
credited. That is the discipline established by the QA regression suite on
13 September 2026 and it is why these exist before any address does.

Requirement 8 carries three known-bad states rather than one, per DM.
"""

import copy
from model import RecordState, VersionEntry
from checks import Spec

# The date the record itself is established. A parameter, not a fact: no record
# exists yet. Every publication-to-record date in the golden is this date,
# because that is what first publication truthfully looks like.
RECORD_ESTABLISHED = "2026-09-20"

SPEC = Spec(
    lineage=["v1", "v1.1", "v2", "v3"],
    expected_current="v3",
    record_established_on=RECORD_ESTABLISHED,
)


def _golden():
    return RecordState(
        http_status=200,
        body_is_generic_host_response=False,
        requires_auth=False,
        unauthenticated_status=200,
        entries=[
            VersionEntry(
                version="v1",
                instrument_date="2026-05-19",
                published_to_record=RECORD_ESTABLISHED,
                reason=None,  # first issue, not a transition
                revision_class="whole_integer",
                superseded_by="v1.1",
                superseded_from="2026-05-28",
                entry_url="/charter/v1",
                content_digest="sha256:aaa",
                entry_resolves=True,
                retrieved_digest="sha256:aaa",
            ),
            VersionEntry(
                version="v1.1",
                instrument_date="2026-05-28",
                published_to_record=RECORD_ESTABLISHED,
                reason="Section 7 handover changed from date-triggered to milestone-gated.",
                revision_class="minor_decimal",
                superseded_by="v2",
                superseded_from="2026-07-29",
                entry_url="/charter/v1.1",
                content_digest="sha256:bbb",
                entry_resolves=True,
                retrieved_digest="sha256:bbb",
            ),
            VersionEntry(
                version="v2",
                instrument_date="2026-07-29",
                published_to_record=RECORD_ESTABLISHED,
                reason="Custodian company named; group implementation licence recorded; "
                       "Section 8 instrument supplied; four-layer numbering adopted.",
                revision_class="whole_integer",
                superseded_by="v3",
                superseded_from="2026-07-29",
                entry_url="/charter/v2",
                content_digest="sha256:ccc",
                entry_resolves=True,
                retrieved_digest="sha256:ccc",
            ),
            VersionEntry(
                version="v3",
                instrument_date="2026-07-29",
                published_to_record=RECORD_ESTABLISHED,
                reason="Section 7.6 extended with the transition-conflict discipline, the "
                       "enforcement statement and the constitutional cross-reference.",
                revision_class="whole_integer",
                is_current=True,
                entry_url="/charter/v3",
                content_digest="sha256:ddd",
                entry_resolves=True,
                retrieved_digest="sha256:ddd",
            ),
        ],
        prior_state_retrievable=True,
        prior_entry_bytes_mutable=False,
        change_events_dated=True,
        baseline_versions=["v1", "v1.1", "v2", "v3"],
        missing_since_baseline=[],
        digest_mismatches=[],
    )


GOLDEN = _golden()


def _mut(fn):
    st = _golden()
    fn(st)
    return st


def _dead(st):
    st.http_status = 404
    st.body_is_generic_host_response = True


def _no_current(st):
    for e in st.entries:
        e.is_current = False


def _wrong_current(st):
    for e in st.entries:
        e.is_current = (e.version == "v1.1")


def _current_only(st):
    st.entries = [e for e in st.entries if e.is_current]


def _drop_reason(st):
    st.by_version("v2").reason = None


def _flat_list(st):
    for e in st.entries:
        e.revision_class = None


def _silent_drop(st):
    # v2 present but unmarked: absence of a supersession statement, which is
    # exactly how a version goes quiet without anyone saying so.
    e = st.by_version("v2")
    e.superseded_by = None
    e.superseded_from = None


def _auth_required(st):
    st.requires_auth = True
    st.unauthenticated_status = 302


def _overwrite_no_history(st):
    st.prior_state_retrievable = False
    st.prior_entry_bytes_mutable = True


def _history_but_mutable(st):
    st.prior_state_retrievable = True
    st.prior_entry_bytes_mutable = True


def _history_undated(st):
    st.change_events_dated = False


def _no_pub_date(st):
    st.by_version("v2").published_to_record = None


def _entry_gone(st):
    # The index still lists v2; the archive entry has gone. Checks 2 to 6 all
    # pass on this state, which is exactly why check 10 exists.
    st.by_version("v2").entry_resolves = False
    st.by_version("v2").retrieved_digest = None


def _entry_substituted(st):
    # The entry resolves, and serves different bytes from the ones recorded.
    st.by_version("v2").retrieved_digest = "sha256:SUBSTITUTED"


def _entries_never_fetched(st):
    # The index asserts digests and nothing was retrieved to check them
    # against. An assertion, not an observation.
    for e in st.entries:
        e.entry_resolves = None
        e.retrieved_digest = None


def _empty_record(st):
    # The page resolves and lists nothing. Found on 14 September by running the
    # live adapter against a dead server: checks 4, 5, 6 and 9 all passed
    # vacuously, because all() over an empty list is True. A check that passes
    # on an empty record is not a control.
    st.entries = []


def _no_baseline(st):
    # No accepted baseline. Neither alteration nor removal is detectable.
    st.baseline_versions = None


def _version_removed_since_baseline(st):
    # v0 was present when the baseline was accepted and is now listed nowhere.
    # It is OUTSIDE spec.lineage, so check 3 cannot see it, and it is absent
    # from the index, so check 8's digest comparison cannot see it either.
    # This is DM's second false pass of 14 September 2026.
    st.baseline_versions = ["v0", "v1", "v1.1", "v2", "v3"]
    st.missing_since_baseline = ["v0"]


def _malformed_date(st):
    # DM's third false pass: dates were compared as strings, and "not-a-date"
    # sorts lexically after any 2026 date, so an earliest-permitted-date test
    # passed on garbage.
    st.by_version("v2").published_to_record = "not-a-date"


def _malformed_instrument_date(st):
    st.by_version("v2").instrument_date = "29/07/2026"


def _published_before_instrument(st):
    st.by_version("v2").published_to_record = "2026-07-01"
    st.by_version("v2").instrument_date = "2026-07-29"


def _backfilled_july(st):
    # The trap: v2 and v3 rendered as though they were publicly published on
    # their instrument date. The record did not exist in July.
    st.by_version("v2").published_to_record = "2026-07-29"
    st.by_version("v3").published_to_record = "2026-07-29"


# check name fragment -> list of (fixture name, RecordState) that MUST fail it
KNOWN_BAD = {
    "1 resolves": [("dead url", _mut(_dead))],
    # every content check must also reject an empty record
    "_empty": [("empty record", _mut(_empty_record))],
    "2 current version": [
        ("no version marked current", _mut(_no_current)),
        ("wrong current version", _mut(_wrong_current)),
    ],
    "3 prior versions": [("current version only", _mut(_current_only))],
    "4 amendment reasons": [("missing amendment reason", _mut(_drop_reason))],
    "5 version semantics": [("flat list, no revision class", _mut(_flat_list))],
    "6 supersession": [("version silently dropped", _mut(_silent_drop))],
    "7 unauthenticated": [("authentication required", _mut(_auth_required))],
    "8 no silent revision": [
        ("overwritten, no prior version retained", _mut(_overwrite_no_history)),
        ("history present but bytes replaceable", _mut(_history_but_mutable)),
        ("history present but changes undated", _mut(_history_undated)),
    ],
    "10 entries retrievable": [
        ("archive entry gone, index unchanged", _mut(_entry_gone)),
        ("entries never fetched", _mut(_entries_never_fetched)),
    ],
    # Deliberately NOT given the gone-entry fixture: a missing entry is check
    # 10's failure, not check 11's. Check 11 asks whether what IS served
    # matches what was recorded. Listing the gone-entry here would demand that
    # one check report two different defects, which is the coupling this suite
    # separates everywhere else.
    "11 entry digests match": [
        ("entry resolves but serves other bytes", _mut(_entry_substituted)),
        ("entries never fetched", _mut(_entries_never_fetched)),
    ],
    "9 date consistency": [
        ("missing publication date", _mut(_no_pub_date)),
        ("backfilled to July", _mut(_backfilled_july)),
        ("publication date is not a date", _mut(_malformed_date)),
        ("instrument date is not ISO", _mut(_malformed_instrument_date)),
        ("published before the instrument is dated", _mut(_published_before_instrument)),
    ],
    "12 membership retained": [
        ("no accepted baseline", _mut(_no_baseline)),
        ("version removed, outside configured lineage", _mut(_version_removed_since_baseline)),
    ],
}
