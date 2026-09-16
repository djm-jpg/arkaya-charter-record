"""Model of a public version record, as §6 and §9 of the Schema Independence
Charter require one.

The tests run against this model, never against raw HTML. A fixture builds the
model directly; the live adapter builds the same model from an endpoint. That is
what lets the same eight checks be proved against known-bad fixtures first and
then pointed at a real address, per DM's instruction of 14 September 2026.

RATIFIED REQUIREMENT, DM 14 September 2026, stated functionally rather than as a
format:

    The public version record must expose a deterministic machine-readable
    representation sufficient to test version identity, publication date,
    amendment reason, supersession and integrity of prior entries.

Structured HTML satisfies this as readily as JSON. A human-readable page alone is
not a control. If the representation changes, only `live.py` changes; the checks
operate on this model and do not.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VersionEntry:
    """One version of the instrument, as the record carries it."""

    version: str
    # The date on the instrument's own cover. NOT a publication date.
    instrument_date: Optional[str] = None
    # The date this version was published TO THIS RECORD. These are different
    # fields and conflating them is the defect requirement 9 exists to catch.
    published_to_record: Optional[str] = None
    reason: Optional[str] = None
    revision_class: Optional[str] = None  # 'whole_integer' | 'minor_decimal'
    is_current: bool = False
    superseded_by: Optional[str] = None
    superseded_from: Optional[str] = None
    # Version-addressed retrieval of this entry, and the digest the record
    # states for it.
    entry_url: Optional[str] = None
    content_digest: Optional[str] = None

    # Result of actually fetching entry_url. These are observations, not
    # anything the index asserts, and they carry two different claims:
    #   entry_resolves      -> availability
    #   retrieved_digest    -> identity, when compared against content_digest
    # None means not attempted.
    entry_resolves: Optional[bool] = None
    retrieved_digest: Optional[str] = None


@dataclass
class RecordState:
    """What a probe of the record returns."""

    http_status: int = 200
    # True where the body is the host's generic response rather than the record:
    # the 8 September state, byte-identical to a control on the same host.
    body_is_generic_host_response: bool = False
    requires_auth: bool = False
    unauthenticated_status: Optional[int] = None

    entries: list = field(default_factory=list)

    # Requirement 8 probes. These are properties of the record's storage
    # discipline, not of anything the page asserts about itself.
    prior_state_retrievable: bool = False
    prior_entry_bytes_mutable: bool = True
    change_events_dated: bool = False

    # Comparison against the ACCEPTED baseline, which is a separate thing from
    # the last observation. A run that detects an alteration must not become
    # the new baseline; see live.record_observation.
    #   baseline_versions       -> versions present when the baseline was accepted
    #   missing_since_baseline  -> in the baseline, absent from the index now
    #   digest_mismatches       -> present, but serving different bytes
    # baseline_versions None means no accepted baseline exists yet, in which
    # case neither removal nor alteration can be detected at all.
    baseline_versions: Optional[list] = None
    missing_since_baseline: list = field(default_factory=list)
    digest_mismatches: list = field(default_factory=list)

    def by_version(self, v):
        for e in self.entries:
            if e.version == v:
                return e
        return None

    def current(self):
        return [e for e in self.entries if e.is_current]


@dataclass
class Result:
    check: str
    passed: bool
    detail: str = ""

    def __str__(self):
        return f"{'PASS' if self.passed else 'FAIL'}  {self.check}  {self.detail}".rstrip()
