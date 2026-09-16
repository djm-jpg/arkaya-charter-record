"""Runner for the public version record acceptance suite.

A check is CREDITED only where it passes the golden fixture and fails every one
of its matched known-bad fixtures. Passing a live endpoint is recorded but is
never evidence on its own, which is the rule the QA regression suite established
on 13 September 2026.

    python3 run_acceptance.py
    PUBLIC_VERSION_RECORD_URL=https://…  python3 run_acceptance.py
"""

import os
import sys

from checks import ALL_CHECKS, Spec
from fixtures import GOLDEN, KNOWN_BAD, SPEC


class SpecError(Exception):
    """The live spec is not fully specified and fallback was not authorised."""


def live_spec():
    """The spec for the LIVE run, parameterised.

    Found while building the prototype, 14 September 2026: the live run used the
    fixture SPEC, whose lineage, expected current version and establishment date
    are constants chosen for the fixtures. Pointed at a real record with a
    different establishment date, check 9 failed on a configuration mismatch
    rather than on anything about the record. The fixtures keep their own spec;
    the live run takes its own.
    """
    missing = [k for k in ("PVR_LINEAGE", "PVR_EXPECTED_CURRENT", "PVR_ESTABLISHED")
               if not os.environ.get(k)]
    if missing and os.environ.get("PVR_ALLOW_FIXTURE_SPEC") != "1":
        # DM, 14 September 2026: printing a fallback improves visibility, but a
        # consequential run should not silently measure a real record against
        # constants chosen for the fixtures. Falling back is now an opt-in.
        raise SpecError(
            "live run requires explicit spec parameters; unset: " + ", ".join(missing)
            + ". Set them, or set PVR_ALLOW_FIXTURE_SPEC=1 to explore against the "
              "fixture defaults, which are not a description of any real record.")
    used_fallback = bool(missing)
    return Spec(
        lineage=[v.strip() for v in os.environ["PVR_LINEAGE"].split(",")]
        if os.environ.get("PVR_LINEAGE") else SPEC.lineage,
        expected_current=os.environ.get("PVR_EXPECTED_CURRENT", SPEC.expected_current),
        record_established_on=os.environ.get("PVR_ESTABLISHED", SPEC.record_established_on),
    ), used_fallback


def _name(check):
    return check(GOLDEN, SPEC).check


def run_fixtures():
    print("=" * 78)
    print("FIXTURE RUN  ·  a check is credited only if it passes the golden")
    print("               record and fails every matched known-bad state")
    print("=" * 78)

    credited, uncredited = [], []
    for check in ALL_CHECKS:
        name = _name(check)
        g = check(GOLDEN, SPEC)
        bads = list(KNOWN_BAD.get(name, []))
        # Every content check must also reject an empty record. Vacuous pass
        # found 14 September 2026; see fixtures._empty_record.
        if name.split()[0] in {"3", "4", "5", "6", "9", "10", "11"}:
            bads += KNOWN_BAD["_empty"]
        print(f"\n{name}")
        print(f"    golden                                    "
              f"{'PASS' if g.passed else 'FAIL  <-- must pass'}  {g.detail}".rstrip())

        ok = g.passed and bool(bads)
        if not bads:
            print("    no known-bad fixture                       NOT CREDITED")
        for label, st in bads:
            r = check(st, SPEC)
            verdict = "correctly rejected" if not r.passed else "FALSE PASS  <-- must fail"
            print(f"    {label:<42}{verdict}"
                  + (f"  ({r.detail})" if not r.passed and r.detail else ""))
            if r.passed:
                ok = False
        (credited if ok else uncredited).append(name)

    print("\n" + "-" * 78)
    print(f"CREDITED   {len(credited)}/{len(ALL_CHECKS)}")
    for n in credited:
        print(f"    {n}")
    if uncredited:
        print("NOT CREDITED")
        for n in uncredited:
            print(f"    {n}")
    print("-" * 78)
    return credited, uncredited


def run_live(credited):
    url = os.environ.get("PUBLIC_VERSION_RECORD_URL")
    print("\n" + "=" * 78)
    print("LIVE RUN")
    print("=" * 78)
    if not url:
        print("  SKIPPED. PUBLIC_VERSION_RECORD_URL is not set.")
        print("  No instrument presently specifies an address for the public version")
        print("  record, so there is nothing to point this at. The suite above stands")
        print("  on its own: every check is proved against known-bad states first.")
        return None

    import live
    # The baseline store is read BEFORE anything else in the live run. If it is
    # unreadable the run stops here: continuing would silently downgrade to a
    # first observation, which is how a corrupted store let an altered archive
    # be accepted on 14 September 2026.
    try:
        live._load_raw()
    except live.BaselineError as e:
        print(f"  ABORTED. {e}")
        print("  The baseline store is unusable. This is not a first run.")
        print("  Repair it, or delete it deliberately to re-establish a baseline,")
        print("  knowing that re-establishing accepts the archive as it stands now.")
        return "baseline-error"
    try:
        spec, used_fallback = live_spec()
    except SpecError as e:
        print(f"  ABORTED. {e}")
        return "spec-error"
    control = os.environ.get("PVR_CONTROL_URL")
    st = live.fetch(url, control)
    print(f"  target   {url}")
    print(f"  spec     lineage={','.join(spec.lineage)}  current={spec.expected_current}  "
          f"record established {spec.record_established_on}"
          + ("   [FIXTURE DEFAULTS, explicitly permitted: not a real record's spec]"
             if used_fallback else ""))
    print(f"  control  {control or '(none set: generic-response test not run)'}")
    print()
    failures = 0
    for check in ALL_CHECKS:
        name = _name(check)
        r = check(st, spec)
        tag = "" if name in credited else "   [check not credited]"
        print(f"  {r}{tag}")
        if not r.passed:
            failures += 1
    # The preservation checks decide whether the accepted baseline may advance.
    # A run that failed any of them must not become the new baseline, or a
    # second run against an altered record passes. That was the defect found
    # on 14 September 2026.
    PRESERVATION = {"8", "10", "11", "12"}
    clean = all(check(st, spec).passed for check in ALL_CHECKS
                if _name(check).split()[0] in PRESERVATION)
    try:
        note = live.record_observation(st, clean)
    except live.BaselineError as e:
        print(f"\n  baseline  NOT WRITTEN: {e}")
        return "baseline-error"
    print(f"\n  baseline  {note}")
    if getattr(st, "_mutability_observed", None) is False:
        print("  NOTE  no accepted baseline existed: alteration and removal could")
        print("        not be detected on this run. Re-run to compare.")
    if st.digest_mismatches or st.missing_since_baseline:
        print("  NOTE  the accepted baseline is HELD. It will keep failing until the")
        print("        change is investigated, or accepted with PVR_ACCEPT_BASELINE=1.")
    return failures


if __name__ == "__main__":
    credited, uncredited = run_fixtures()
    failures = run_live(credited)
    if uncredited:
        sys.exit(2)
    if failures == "baseline-error":
        sys.exit(3)
    if failures == "spec-error":
        sys.exit(4)
    sys.exit(0 if failures in (None, 0) else 1)
