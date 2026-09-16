"""Fixed expectations, and independent readers for the evidence they apply to.

DM's finding 2, 16 September 2026: the packaging gate trusted the labels in
`results.json`. Setting a run's recorded exit status to 99 with a digest failure,
while leaving `as_expected` true, produced no complaint. Replacing a retained
transcript with unrelated text also passed, because the gate checked that the
file existed rather than what was in it.

The fix is that the expected outcomes live HERE, in code, imported by both the
verification harness and the gate, and the gate re-derives every outcome from the
retained transcript rather than reading the summary. A summary that disagrees
with its own transcript is then a finding, and a transcript that cannot be parsed
is a finding too.

Nothing in this module reads `results.json`.
"""

import hashlib
import os
import re

# The outcome every run MUST produce. A run that does not match is a failure of
# the verification, not a footnote in it.
#   exit      the runner's exit status
#   failed    the check numbers that must fail, exactly
#   baseline  a substring the baseline note must contain
EXPECTED = {
    "run01_first_observation":         dict(exit=1, failed={"8", "12"}, baseline="established"),
    "run02_baseline_established":      dict(exit=0, failed=set(),       baseline="advanced"),
    "run03_v1_mutation":               dict(exit=1, failed={"11"},      baseline="HELD"),
    "run03_v1_1_mutation":             dict(exit=1, failed={"11"},      baseline="HELD"),
    "run03_v2_mutation":               dict(exit=1, failed={"11"},      baseline="HELD"),
    "run03_v3_mutation":               dict(exit=1, failed={"11"},      baseline="HELD"),
    "run04a_object_removed":           dict(exit=1, failed={"10"},      baseline="HELD"),
    "run04b_entry_removed_from_index": dict(exit=1, failed={"3", "12"}, baseline="HELD"),
    "run05_after_restoration":         dict(exit=0, failed=set(),       baseline="advanced"),
    "run06_after_rebuild":             dict(exit=0, failed=set(),       baseline="advanced"),
}

# Every run above must be present. A verification missing a run is not a
# verification that happened to be shorter.
REQUIRED_RUNS = tuple(EXPECTED)

EXIT_RE = re.compile(r"^EXIT\s+(-?\d+)\s*$", re.M)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def tree(root):
    out = {}
    for dirpath, _, names in os.walk(root):
        for n in names:
            p = os.path.join(dirpath, n)
            out[os.path.relpath(p, root)] = sha(p)
    return out


class Unreadable(Exception):
    """The transcript is not a transcript of an acceptance run."""


def parse_transcript(text):
    """Read the outcome out of the transcript itself.

    Returns (exit_status, failing check numbers, baseline note). Raises
    Unreadable if the text does not carry the structure a run produces, which is
    what catches a transcript replaced by something else entirely.
    """
    m = EXIT_RE.search(text)
    if not m:
        raise Unreadable("no EXIT line in the transcript header")
    if "LIVE RUN" not in text:
        raise Unreadable("no LIVE RUN section in the transcript")
    live = text.split("LIVE RUN", 1)[1]
    checks = [l for l in live.splitlines()
              if l.strip().startswith(("PASS ", "FAIL "))]
    if not checks:
        raise Unreadable("no check results in the LIVE RUN section")
    failed = {l.strip().split("FAIL", 1)[1].strip().split()[0]
              for l in checks if l.strip().startswith("FAIL")}
    baseline = next((l.split("baseline", 1)[1].strip()
                     for l in live.splitlines() if l.strip().startswith("baseline")), None)
    if baseline is None:
        raise Unreadable("no baseline line in the LIVE RUN section")
    return int(m.group(1)), failed, baseline


def evaluate_run(label, transcript_text):
    """Compare a transcript against the fixed expectation. Returns a list of problems."""
    want = EXPECTED.get(label)
    if want is None:
        return [f"{label}: not a run this verification defines"]
    try:
        got_exit, got_failed, baseline = parse_transcript(transcript_text)
    except Unreadable as exc:
        return [f"{label}: transcript unreadable: {exc}"]
    problems = []
    if got_exit != want["exit"]:
        problems.append(f"{label}: transcript exit {got_exit}, expected {want['exit']}")
    if got_failed != want["failed"]:
        problems.append(f"{label}: transcript failing checks "
                        f"{sorted(got_failed) or 'none'}, expected "
                        f"{sorted(want['failed']) or 'none'}")
    if want["baseline"] not in baseline:
        problems.append(f"{label}: transcript baseline '{baseline}', expected to "
                        f"contain '{want['baseline']}'")
    return problems


def evaluate_rebuild(comparison, expected_change, release_tree):
    """Recompute the rebuild result from the retained trees.

    `comparison` is the retained run06_rebuild.json. The recorded `result.passed`
    is ignored entirely: the verdict is computed from `before` and `after`, and
    `before` must match the release as it stands on disk, or the comparison was
    made against something else.
    """
    problems = []
    before = comparison.get("before") or {}
    after = comparison.get("after") or {}
    if not before or not after:
        return ["rebuild: the retained comparison has no before/after trees"], False
    if before != release_tree:
        problems.append("rebuild: the comparison's 'before' tree is not the release on disk")
    changed = {p for p in before if before[p] != after.get(p)}
    unexpected = sorted(changed - set(expected_change))
    if unexpected:
        problems.append(f"rebuild: unexpected differences {unexpected}")
    if sorted(before) != sorted(after):
        problems.append("rebuild: the rebuilt set has different membership")
    pdfs = [p for p in before if p.endswith(".pdf")]
    if len(pdfs) != 4:
        problems.append(f"rebuild: {len(pdfs)} PDFs compared, expected 4")
    return problems, not problems
