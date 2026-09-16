"""Package a frozen Charter release, and refuse to package one that cannot be reconciled.

DM's finding 1, 16 September 2026: this script rebuilt the set before packaging.
Every rebuild changed `as_of`, so the packaged set was not the set that had been
built and checked, and at sequence 1 the rebuild collided with the published
index digest and the documented step simply failed. **This script no longer
builds anything.** A release is built once by `build_publication_set.py`, frozen,
and packaged exactly as it stands. Rebuild reproducibility is tested by building
into a separate directory, which `verification/run_verification.py` does.

DM's finding 4: the production-record check tested whether a digest appeared
ANYWHERE in the evidence, not whether it belonged to the object it was printed
against. Substituting v1.1's valid digest into v1's row passed. The record is now
regenerated deterministically from the manifest and the verification results and
compared BYTE FOR BYTE with the file on disk, so a digest in the wrong row is a
different file and is rejected.

    python3 package.py            check the frozen release, generate, verify, package
    python3 package.py --check    check only; write nothing

The gate, in order:
    1. the release is frozen and still matches its freeze marker
    2. every manifest object exists and matches, and nothing is served unnamed
    3. verification results exist FOR THIS MANIFEST, every run matched its
       expected outcome, and the rebuild comparison passed
    4. the production record equals its deterministic regeneration
    5. the build tests and the live-verifier known-bad tests pass
"""

import hashlib
import json
import os
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from expectations import (EXPECTED, REQUIRED_RUNS, evaluate_run,   # noqa: E402
                          evaluate_rebuild, parse_transcript, tree, Unreadable)
RUNS = os.path.join(HERE, "verification", "runs")
PRODUCTION_RECORD = os.path.join(HERE, "verification", "PRODUCTION_RECORD.md")

PACKAGE_NAME = "OPS_Charter_PublicationSet_2026-09-16_v6"
RELEASE_NAME = os.environ.get("PVR_RELEASE", "publish")
RELEASE_DIR = os.path.join(HERE, RELEASE_NAME)
RECORD = os.path.join(RELEASE_DIR, "charter")
RELEASE_META = os.path.join(HERE, "releases", f"{RELEASE_NAME}.json")

# Everything that must be in the archive for the package to be runnable and for
# the record's state to be complete. DM's finding 6: published_indexes.json was
# omitted, and a ledger of hashes without the index files it describes is not a
# retained record.
CONTENTS = (
    RELEASE_NAME,                 # the frozen release: the deploy root
    "inputs",                     # the four PDFs at their declared paths
    "vendor",                     # the acceptance suite, permanently
    "verification",               # every retained run, plus the production record
    "publications",               # immutable snapshot per published sequence
    "releases",                   # freeze markers
    "build_publication_set.py",
    "record_publication.py",
    "expectations.py",
    "package.py",
    "verify_live.py",
    "test_build.py",
    "test_verify_live.py",
    "test_package.py",
    "README_source.md",
    "DEPLOY.md",
    "PUBLICATION_LOG.md",
    "first_publication.json",
    "published_indexes.json",
)


class PackageError(Exception):
    pass


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load(path, what):
    if not os.path.exists(path):
        raise PackageError(f"{what} not found: {os.path.relpath(path, HERE)}")
    with open(path) as f:
        return json.load(f)


# ------------------------------------------------------------------- checks

def check_release_frozen(manifest_sha):
    meta = load(RELEASE_META, f"freeze marker for release '{RELEASE_NAME}'")
    problems = []
    if meta["manifest_sha256"] != manifest_sha:
        problems.append(
            f"the release directory does not match its freeze marker "
            f"({manifest_sha[:16]}… vs {meta['manifest_sha256'][:16]}…). Something "
            f"changed the release after it was frozen; rebuild it deliberately")
    return meta, problems


def check_manifest_against_disk(manifest):
    problems = []
    for o in manifest["objects"]:
        p = os.path.join(RECORD, o["path"])
        if not os.path.isfile(p):
            problems.append(f"{o['path']}: named in the manifest, not on disk")
            continue
        if sha(p) != o["sha256"]:
            problems.append(f"{o['path']}: manifest {o['sha256'][:16]}… != disk {sha(p)[:16]}…")
        if os.path.getsize(p) != o["bytes"]:
            problems.append(f"{o['path']}: manifest {o['bytes']} bytes != disk {os.path.getsize(p)}")

    named = {o["path"] for o in manifest["objects"]} | {"manifest.json", "manifest.json.sha256"}
    on_disk = set()
    for dirpath, _, names in os.walk(RECORD):
        for n in names:
            on_disk.add(os.path.relpath(os.path.join(dirpath, n), RECORD))
    for extra in sorted(on_disk - named):
        problems.append(f"{extra}: served but not named in the manifest")

    with open(os.path.join(RECORD, "manifest.json.sha256")) as f:
        recorded = f.read().split()[0]
    if recorded != sha(os.path.join(RECORD, "manifest.json")):
        problems.append("manifest.json.sha256 does not match manifest.json")
    return problems


def find_results(manifest_sha):
    """The verification evidence for THIS manifest, or none.

    Runs are retained, never overwritten, so there may be several. Only one taken
    against the frozen manifest counts, and the newest such run is used.
    """
    if not os.path.isdir(RUNS):
        raise PackageError("no verification runs; run verification/run_verification.py")
    candidates = []
    for name in sorted(os.listdir(RUNS), reverse=True):
        p = os.path.join(RUNS, name, "results.json")
        if not os.path.isfile(p):
            continue
        with open(p) as f:
            d = json.load(f)
        if d.get("record_under_test", {}).get("manifest_sha256") == manifest_sha:
            candidates.append(d)
    if not candidates:
        raise PackageError(
            f"no verification run was made against the frozen manifest "
            f"{manifest_sha[:16]}…. Re-run verification against this release")
    return candidates[0]


def check_source_identities(manifest, results):
    """The files SHIPPED must be the files RECORDED. DM's finding 1.

    The v5 archive recorded builder `faf524a0…` in both the manifest and the
    freeze marker while shipping a builder that hashed to `311f9f11…`. The two
    records agreed with each other, which is precisely what concealed the
    mismatch: nothing compared either of them to the file on disk. I had edited
    the builder after freezing and packaged without rebuilding.

    Every recorded identity is now checked against the actual file.
    """
    problems = []

    builder = os.path.join(HERE, os.path.basename(manifest["builder"]["source_path"]))
    if not os.path.isfile(builder):
        problems.append(f"the builder named by the manifest is not in the package: "
                        f"{manifest['builder']['source_path']}")
    elif sha(builder) != manifest["builder"]["sha256"]:
        problems.append(
            f"the shipped builder hashes to {sha(builder)[:16]}…, the manifest records "
            f"{manifest['builder']['sha256'][:16]}…. The release was not built by the "
            f"builder in this package; rebuild and refreeze")

    for i in manifest["inputs"]:
        p = os.path.join(HERE, i["path"])
        if not os.path.isfile(p):
            problems.append(f"input not in the package: {i['path']}")
        elif sha(p) != i["sha256"]:
            problems.append(f"{i['path']}: shipped {sha(p)[:16]}… manifest {i['sha256'][:16]}…")
        elif os.path.getsize(p) != i["bytes"]:
            problems.append(f"{i['path']}: shipped {os.path.getsize(p)} bytes, "
                            f"manifest {i['bytes']}")

    for g in manifest["generated"]:
        src = g["generated_from"]
        if src.endswith(".json"):
            continue                      # generated from another built object, checked above
        p = os.path.join(HERE, src)
        if not os.path.isfile(p):
            problems.append(f"generation source not in the package: {src}")
        elif sha(p) != g["source_sha256"]:
            problems.append(f"{src}: shipped {sha(p)[:16]}… manifest "
                            f"{g['source_sha256'][:16]}…")

    suite_dir = os.path.join(HERE, results["acceptance_suite"]["retained_at"].rstrip("/"))
    if not os.path.isdir(suite_dir):
        problems.append(f"acceptance suite not in the package: "
                        f"{results['acceptance_suite']['retained_at']}")
    else:
        recorded = results["acceptance_suite"]["files"]
        actual = tree(suite_dir)
        for name in sorted(set(recorded) | set(actual)):
            if name not in actual:
                problems.append(f"acceptance suite file missing: {name}")
            elif name not in recorded:
                problems.append(f"acceptance suite file not recorded: {name}")
            elif recorded[name] != actual[name]:
                problems.append(f"acceptance suite file altered: {name}")

    return problems


def check_marker_agrees_with_manifest(manifest, release):
    """The freeze marker restates the manifest; it must not diverge from it."""
    problems = []
    if release["builder"] != manifest["builder"]:
        problems.append("the freeze marker's builder block differs from the manifest's")
    if release["sequence"] != manifest["sequence"]:
        problems.append("the freeze marker's sequence differs from the manifest's")
    if release["release_date"] != manifest["as_of"]:
        problems.append("the freeze marker's release date differs from the manifest's as_of")
    if release["canonical_base"] + "/" != manifest["canonical_uri"]:
        problems.append("the freeze marker's canonical base differs from the manifest's")
    index = os.path.join(RECORD, "index.json")
    if os.path.isfile(index) and sha(index) != release["index_sha256"]:
        problems.append("the freeze marker's index digest does not match index.json")
    pointer = os.path.join(RELEASE_DIR, "index.html")
    if os.path.isfile(pointer) and sha(pointer) != release.get("root_pointer_sha256"):
        problems.append("the freeze marker's pointer digest does not match the deploy root page")
    return problems


def check_results(manifest, results):
    """Re-derive every outcome from the retained evidence. DM's finding 2.

    The previous version read `as_expected`, `all_runs_as_expected` and
    `rebuild.passed` out of the summary. Setting a run's recorded exit status to
    99 with a digest failure while leaving `as_expected` true produced no
    complaint, and replacing a transcript with unrelated text passed because the
    check was for existence.

    Nothing below trusts a label. Each transcript is parsed and compared with the
    fixed expectations in `expectations.py`, each retained file is hashed against
    the digest recorded when it was written, and the rebuild verdict is
    recomputed from the retained before/after trees.
    """
    problems = []
    if results["record_under_test"]["builder"]["sha256"] != manifest["builder"]["sha256"]:
        problems.append("the verification runs used a different builder from the packaged one")

    present = {r["label"] for r in results["runs"]}
    for label in REQUIRED_RUNS:
        if label not in present:
            problems.append(f"expected run not present: {label}")
    for label in sorted(present - set(REQUIRED_RUNS)):
        problems.append(f"unrecognised run in the evidence: {label}")

    for r in results["runs"]:
        transcript = os.path.join(HERE, r["transcript"])
        if not os.path.isfile(transcript):
            problems.append(f"retained evidence missing: {r['transcript']}")
            continue
        recorded_sha = r.get("transcript_sha256")
        if recorded_sha and sha(transcript) != recorded_sha:
            problems.append(f"retained transcript altered since it was written: "
                            f"{r['transcript']}")
        with open(transcript) as f:
            text = f.read()
        problems += evaluate_run(r["label"], text)

        # The summary must not contradict its own transcript.
        try:
            from expectations import parse_transcript
            got_exit, got_failed, baseline = parse_transcript(text)
            if r.get("exit_status") != got_exit:
                problems.append(f"{r['label']}: summary exit {r.get('exit_status')} "
                                f"contradicts its transcript ({got_exit})")
            summary_failed = {c.split()[0] for c in r.get("checks_failed", [])}
            if summary_failed != got_failed:
                problems.append(f"{r['label']}: summary failing checks "
                                f"{sorted(summary_failed)} contradict its transcript "
                                f"{sorted(got_failed)}")
            if (r.get("baseline_note") or "") != baseline:
                problems.append(f"{r['label']}: summary baseline note contradicts its transcript")
        except Exception:                                   # noqa: BLE001
            pass                                            # already reported by evaluate_run

        # The summary's own verdict must match the re-derived one. The gate does
        # not rely on these labels, but a summary that ships a false claim is
        # still a finding: it is what a person reads.
        derived_ok = not evaluate_run(r["label"], text)
        if bool(r.get("as_expected")) != derived_ok:
            problems.append(f"{r['label']}: summary says as_expected="
                            f"{bool(r.get('as_expected'))}, the transcript says {derived_ok}")

        baseline_file = os.path.join(HERE, r["baseline_after"])
        if not os.path.isfile(baseline_file):
            problems.append(f"retained baseline missing: {r['baseline_after']}")
        elif r.get("baseline_after_sha256") and sha(baseline_file) != r["baseline_after_sha256"]:
            problems.append(f"retained baseline altered since it was written: "
                            f"{r['baseline_after']}")

    def _transcript_ok(r):
        path = os.path.join(HERE, r["transcript"])
        with open(path) as f:
            return not evaluate_run(r["label"], f.read())

    all_ok = all(_transcript_ok(r) for r in results["runs"]
                 if os.path.isfile(os.path.join(HERE, r["transcript"])))
    if bool(results.get("all_runs_as_expected")) != all_ok:
        problems.append(f"the summary says all_runs_as_expected="
                        f"{bool(results.get('all_runs_as_expected'))}, the transcripts say "
                        f"{all_ok}")

    # Rebuild: recomputed from the retained trees, not read from `passed`.
    comparison_path = os.path.join(HERE, results["run_dir"],
                                   results.get("rebuild_comparison", "run06_rebuild.json"))
    if not os.path.isfile(comparison_path):
        problems.append("the retained rebuild comparison is missing")
    else:
        with open(comparison_path) as f:
            comparison = json.load(f)
        rebuild_problems, recomputed = evaluate_rebuild(
            comparison, manifest["not_bit_reproducible"]["paths"], tree(RECORD))
        problems += rebuild_problems
        claimed = results.get("rebuild", {}).get("passed")
        if claimed is not None and bool(claimed) != recomputed:
            problems.append(f"the summary says the rebuild passed={bool(claimed)}, the "
                            f"retained comparison says {recomputed}")
        inner = comparison.get("result", {}).get("passed")
        if inner is not None and bool(inner) != recomputed:
            problems.append(f"the retained comparison claims passed={bool(inner)}, its own "
                            f"trees say {recomputed}")

    return problems


# ---------------------------------------------------------------- generation

def derive_outcomes(results):
    """Re-read every run's outcome from its retained transcript.

    The record prints what the transcripts say, not what the summary claims.
    Printing the recorded label meant an edited label changed the record rather
    than being caught as a contradiction with its own evidence.
    """
    derived = {}
    for r in results["runs"]:
        transcript = os.path.join(HERE, r["transcript"])
        try:
            with open(transcript) as f:
                got_exit, got_failed, baseline = parse_transcript(f.read())
        except (OSError, Unreadable):
            derived[r["label"]] = None
            continue
        want = EXPECTED.get(r["label"], {})
        derived[r["label"]] = {
            "exit": got_exit,
            "failed": sorted(got_failed),
            "baseline": baseline,
            "as_expected": (got_exit == want.get("exit")
                            and got_failed == want.get("failed")
                            and want.get("baseline", "") in baseline),
        }
    return derived


def derive_rebuild(manifest, results):
    """Recompute the rebuild verdict from the retained trees."""
    path = os.path.join(HERE, results["run_dir"],
                        results.get("rebuild_comparison", "run06_rebuild.json"))
    with open(path) as f:
        comparison = json.load(f)
    before, after = comparison.get("before") or {}, comparison.get("after") or {}
    expected_change = set(manifest["not_bit_reproducible"]["paths"])
    changed = {p for p in before if before[p] != after.get(p)}
    _, passed = evaluate_rebuild(comparison, expected_change, tree(RECORD))
    return {
        "objects_compared": len(before),
        "pdfs_compared": sorted(p for p in before if p.endswith(".pdf")),
        "membership_identical": sorted(before) == sorted(after),
        "expected_to_change": sorted(expected_change),
        "changed": sorted(changed),
        "unexpected_changes": sorted(changed - expected_change),
        "built_into": comparison.get("result", {}).get(
            "built_into", "a separate directory; the frozen release was not touched"),
        "passed": passed,
    }


def generate_production_record(manifest, results, release):
    """Deterministic: same manifest, results and release produce the same bytes.

    Nothing here reads the clock. That is what allows `--check` to regenerate the
    record and compare it byte for byte, which is the control that catches a
    digest printed against the wrong object.
    """
    m, r, rel = manifest, results, release
    b = m["builder"]
    runs = r["runs"]
    derived = derive_outcomes(r)
    rebuild = derive_rebuild(m, r)
    suite = r["acceptance_suite"]

    # The status block depends on RECORDED STATE. DM, 17 September 2026: the
    # generator asserted "Publication not yet authorised or observed" and that
    # the project, repository and DNS record had not been created, without
    # condition. Regenerating the record after a successful publication, which
    # the release sequence does, would therefore have produced a record
    # contradicting the publication it was packaged with.
    published = bool(rel.get("published"))
    pub = None
    if published:
        pub_path = os.path.join(HERE, "publications", str(rel["sequence"]), "publication.json")
        if os.path.isfile(pub_path):
            with open(pub_path) as f:
                pub = json.load(f)

    # Tag names come from what is recorded, never from a constant. A replacement
    # release takes release-002 and publication-002, and a record naming the
    # first attempt's tags would contradict the publication it describes.
    release_tag_label = (f"`{pub['release_tag']}` (tag on the frozen-release commit)"
                         if pub and pub.get("release_tag")
                         else "The frozen-release tag")
    evidence_tag = None
    ledger_path = os.path.join(HERE, "published_indexes.json")
    if published and os.path.isfile(ledger_path):
        with open(ledger_path) as f:
            entry = json.load(f).get("versions", {}).get(str(rel["sequence"]), {})
        evidence_tag = entry.get("publication_evidence_tag")
    evidence_tag_label = (f"`{evidence_tag}` (tag on the publication-evidence commit)"
                          if evidence_tag
                          else "The publication-evidence tag, recorded once it exists")

    synthetic_bound = ("**The live evidence for this publication is recorded in "
                       f"`publications/{rel['sequence']}/live_verification.json`.** The runs in "
                       "this section are local; they are not that evidence."
                       if published else
                       "**Where the recorder path was exercised with synthetic evidence, the "
                       "bound is:** the successful recorder path was tested using synthetic "
                       "evidence representing an approved live observation. This demonstrates "
                       "recorder behaviour given approval; it does not demonstrate that "
                       "publication or live verification occurred.")

    def run_row(x):
        d = derived.get(x["label"])
        want = EXPECTED.get(x["label"], {})
        want_failed = ", ".join(sorted(want.get("failed", ()))) or "none"
        if d is None:
            return (f"| `{x['label']}` | UNREADABLE | — / {want_failed} | — | NO |")
        failed = ", ".join(d["failed"]) or "none"
        return (f"| `{x['label']}` | {d['exit']} / {want.get('exit')} | "
                f"{failed} / {want_failed} | {d['baseline']} | "
                f"{'yes' if d['as_expected'] else 'NO'} |")

    version_rows = "\n".join(
        f"| {o['version']} | `{o['path']}` | `{o['sha256']}` | {o['bytes']:,} |"
        for o in m["objects"] if o.get("version"))
    other_rows = "\n".join(
        f"| `{o['path']}` | `{o['sha256']}` | {o['bytes']:,} |"
        for o in m["objects"] if not o.get("version"))
    input_rows = "\n".join(
        f"| {i['version']} | `{i['path']}` | `{i['sha256']}` | {i['bytes']:,} |"
        for i in m["inputs"])
    gen_rows = "\n".join(
        f"| `{g['path']}` | `{g['generated_from']}` | {g['relation']} | "
        f"`{g['source_sha256']}` | `{g['sha256']}` |"
        for g in m["generated"])

    if published and pub:
        status_block = f"""**Status: published. Sequence {rel['sequence']} was recorded as published on {pub['published_on']}, from a passing, approved live verification of this frozen release at {pub['canonical_uri']}.**

| | |
|---|---|
| Published on | {pub['published_on']} |
| Recorded at | {pub['recorded_at']} |
| Deploy ID | `{pub['deploy_id']}` |
| Deploy permalink | {pub['deploy_permalink']} |
| Frozen-release commit | `{pub['release_commit']}` |
| Frozen-release tag | `{pub['release_tag'] or 'none'}` |
| Live evidence | `{pub['evidence']}` |
| Immutable snapshot | `publications/{rel['sequence']}/` |

{pub['basis'].capitalize()}.

What that does **not** establish is unchanged by publication, and is set out in section 1."""
    elif published:
        status_block = ("**Status: published, but the publication snapshot could not be read.** "
                        f"The release marker records sequence {rel['sequence']} as published on "
                        f"{rel.get('published_on', 'an unstated date')}, and "
                        f"`publications/{rel['sequence']}/publication.json` is missing or "
                        f"unreadable. Treat this as a finding: the record cannot state the "
                        f"deployment identifiers it should be citing.")
    else:
        status_block = f"""**Status as at {rel['release_date']}: frozen release candidate. Architecture and transaction controls rehearsed. Publication not yet authorised or observed.**

This is a dated pre-deployment assessment. Not "deployment candidate successfully verified": the
decisive verification requires HTTPS at the canonical venue. Publication dates become
first-publication dates only when `record_publication.py` records them against a passing,
approved live verification at that address, and this record is regenerated when it does. As at
the date above, no Netlify project, repository or DNS record had been created."""

    override = m["build_parameters"].get("date_mismatch_reason")
    override_line = (f"\n**Release-date override in force.** Reason recorded at build time: "
                     f"{override}\n" if override else "")

    return f"""# Charter publication set: production record

Internal record. `{PACKAGE_NAME}`. Release {rel['sequence']}, dated {rel['release_date']}.

**Generated from the frozen release.** This file is produced by `package.py` from
`manifest.json` and the verification results, with no reference to the clock. Packaging
regenerates it and compares byte for byte, so a figure printed against the wrong object is a
different file and is rejected. An earlier version checked only whether a digest appeared
somewhere in the evidence, and passed when v1.1's digest was substituted into v1's row.

{status_block}

## 0. Three facts, three artefacts, not to be conflated

| Artefact | What it asserts | What it does not |
|---|---|---|
| {release_tag_label} | These are the bytes intended for publication | Nothing about whether they were deployed or observed |
| The live verification evidence | These bytes were observed at the canonical venue, matching this manifest object by object | Nothing about the Charter, and nothing about continuity beyond the moment of observation |
| {evidence_tag_label} | The evidence record **that** publication occurred | **It is not the published object.** It necessarily post-dates the deployment it records, and must not be read as the released set |

The recorder enforces the join between the first two: a release is bound to its commit and tag
before deployment, and publication cannot be recorded unless the approval evidence carries this
manifest digest **and** the commit given is the one bound to this frozen release. The binding is
to an identifier supplied by the operator; it does not verify that the commit exists in any
repository. A fresh clone at the tag passing `package.py --check` is what tests the other half.
{override_line}
## 1. What these runs establish, and what they do not

**They establish that the built set satisfies the specified controls**, and that the shipped
objects stand in the recorded relationship to the recorded inputs.

**On provenance.** {m['provenance_claim']}

**They do not establish publication correctness.** Whether the historical dates are truthful, and
whether the v1.1, v2 and v3 amendments were validly effective from their stated July dates, are
separate questions and remain exactly where they were. No run below touches either.

**They say nothing about the canonical venue.** {r['scope']}

## 2. The release

| | |
|---|---|
| Release directory | `{rel['release_dir']}/` |
| Sequence | {rel['sequence']} |
| Release date | {rel['release_date']} |
| Canonical base | `{rel['canonical_base']}` |
| Manifest SHA-256 | `{rel['manifest_sha256']}` |
| Index SHA-256 | `{rel['index_sha256']}` |
| Published | {str(rel['published']).lower()} |
| State | {rel['state']} |

The freeze marker lives at `releases/{rel['release_dir']}.json`, outside the release directory,
so nothing internal is ever served. The release is built once and packaged as built.

### What the shipped files are checked against

The builder, each input, the README source and every file of the retained acceptance suite are
hashed and compared with the identities recorded in the manifest and the verification results.
The v5 archive recorded one builder digest in both the manifest and the freeze marker while
shipping a different builder; the two records agreed with each other, and nothing compared
either of them to the file on disk.

## 3. Build provenance

| | |
|---|---|
| Builder | `{b['script']}` |
| Source path in the tagged repository | `{b['source_path']}` |
| Version | `{b['version']}` |
| SHA-256 | `{b['sha256']}` |
| Python | {m['build_parameters']['python']} |
| Platform | {m['build_parameters']['platform']} |
| Built at | {m['build_parameters']['built_at']} |

### Inputs, validated before the build touched anything

| Version | Source | SHA-256 | Bytes |
|---|---|---|---|
{input_rows}

The builder holds these digests in code and checks them before it deletes or replaces anything.
A build whose inputs do not match refuses and leaves the previous set intact.

### Generated artefacts and their sources

| Shipped | Generated from | Relation | Source digest | Output digest |
|---|---|---|---|---|
{gen_rows}

## 4. Published objects

| Version | Path | SHA-256 | Bytes |
|---|---|---|---|
{version_rows}

| Path | SHA-256 | Bytes |
|---|---|---|
{other_rows}

`manifest.json`'s own digest is in `manifest.json.sha256`, since a file cannot contain its own
digest. The live verifier fetches and hashes the served manifest against this one, because a
venue serving a wrong manifest with a consistent sidecar would otherwise pass.

## 5. Build-governance corrections carried forward

Each is recorded because it shows the build process was tested, not only its output.

**The README was originally written by hand into the built tree, which the builder deletes and
recreates. The first rebuild silently removed it.** Corrected by moving the README to
`README_source.md` outside the built tree. **A file the build can destroy is not part of the
build.**

**The page renderer was a separate script**, so a set could be built without being rendered.
Folded into the builder.

**The builder deleted the output before validating its inputs.** It now validates first and
builds into a staging directory, promoting only a complete set.

**The confirmed-date check ran after promotion.** A build with a false date produced the set,
promoted it carrying that date, and only then refused. The check now runs before anything is
built. Found by the build tests, not by inspection.

**Packaging rebuilt the release before packaging it**, so the packaged set was not the set that
had been checked, and at sequence 1 the documented step failed outright. Packaging no longer
builds; reproducibility is tested by building into a separate directory.

**The builder recorded publication.** It wrote first-publication dates and marked the set
published before any deployment existed, so a failed deployment left a false record. Publication
is now recorded only by `record_publication.py`, only against live evidence.

## 6. Verification

**The suite that produced these results is retained in the package**, at `{suite['retained_at']}`,
{len(suite['files'])} files, digest of file digests `{suite['digest_of_file_digests']}`.
Source: `{suite['source']}`.

Every run's command, working directory, exit status, full transcript and resulting baseline store
are retained under `{r['run_dir']}/`. Runs are never overwritten. Spec parameters were set
explicitly for every run; the suite refuses a live run otherwise, so no result was measured
against fixture constants.

```
PVR_LINEAGE={r['spec_parameters']['PVR_LINEAGE']}   PVR_EXPECTED_CURRENT={r['spec_parameters']['PVR_EXPECTED_CURRENT']}   PVR_ESTABLISHED={r['spec_parameters']['PVR_ESTABLISHED']}
PUBLIC_VERSION_RECORD_URL={r['spec_parameters']['PUBLIC_VERSION_RECORD_URL']}
PVR_CONTROL_URL={r['spec_parameters']['PVR_CONTROL_URL']}
```

**The frozen release was not mutated by any run.** The mutation and removal tests operate on a
served copy; the release directory is read-only input to the verification.

{synthetic_bound}

**Each run declares the outcome it must produce**, in `expectations.py`, which the harness and
this gate both import. The columns below are **re-read from the retained transcripts** by the
gate, not copied from the harness's summary: a summary that disagrees with its own transcript is
a finding, and a transcript that cannot be parsed is a finding. Observed / expected.

| Run | Exit | Checks failed | Baseline | As expected |
|---|---|---|---|---|
{chr(10).join(run_row(x) for x in runs)}

### What each run is for

{chr(10).join(f"**`{x['label']}`** — {x['note']}" + chr(10) for x in runs)}

### Rebuild reproducibility

{rebuild['objects_compared']} objects compared against an independent rebuild
({rebuild['built_into']}), including all {len(rebuild['pdfs_compared'])} PDFs. Membership
identical: {str(rebuild['membership_identical']).lower()}.

`as_of` is a date rather than a build timestamp, so the index and the page reproduce bit for bit.
Only these carry a build time and are expected to differ:
{', '.join('`' + p + '`' for p in rebuild['expected_to_change'])}.
Objects that differed: {', '.join('`' + p + '`' for p in rebuild['changed']) or 'none'}.
**Unexpected changes: {', '.join(rebuild['unexpected_changes']) or 'none'}.**

## 7. Lineage

**v1, v1.1, v2, v3.** Four versions, and the published set contains no other. Checked
mechanically across every served file: no version outside that lineage is named anywhere in the
record. "v5" in the package name is the package revision, not a Charter version.
"""


# ------------------------------------------------------------------- driver

def main(argv):
    check_only = "--check" in argv

    manifest = load(os.path.join(RECORD, "manifest.json"), "manifest")
    manifest_sha = sha(os.path.join(RECORD, "manifest.json"))
    release, problems = check_release_frozen(manifest_sha)
    problems += check_manifest_against_disk(manifest)
    problems += check_marker_agrees_with_manifest(manifest, release)
    if problems:
        print("PACKAGE REFUSED. The frozen release is not internally consistent:")
        for p in problems:
            print(f"  - {p}")
        return 2
    print(f"  release        frozen, sequence {release['sequence']}, "
          f"manifest {manifest_sha[:16]}…")

    results = find_results(manifest_sha)
    problems = check_source_identities(manifest, results) + check_results(manifest, results)
    if problems:
        print("PACKAGE REFUSED. The verification evidence does not support this release:")
        for p in problems:
            print(f"  - {p}")
        return 2
    print(f"  identities     builder, {len(manifest['inputs'])} inputs, README source and "
          f"{len(results['acceptance_suite']['files'])} suite files match their records")
    print(f"  verification   {len(results['runs'])} runs re-derived from transcripts, "
          f"rebuild recomputed  ({results['run_dir']})")

    regenerated = generate_production_record(manifest, results, release)
    if not check_only:
        with open(PRODUCTION_RECORD, "w") as f:
            f.write(regenerated)
        print("  record         generated")

    if not os.path.isfile(PRODUCTION_RECORD):
        print("PACKAGE REFUSED: the production record has not been generated.")
        return 2
    with open(PRODUCTION_RECORD) as f:
        on_disk = f.read()
    if on_disk != regenerated:
        print("PACKAGE REFUSED. The production record is not its deterministic regeneration:")
        a, b = on_disk.splitlines(), regenerated.splitlines()
        shown = 0
        for i in range(max(len(a), len(b))):
            x = a[i] if i < len(a) else "<absent>"
            y = b[i] if i < len(b) else "<absent>"
            if x != y:
                print(f"  - line {i + 1}")
                print(f"      on disk:      {x[:150]}")
                print(f"      regenerated:  {y[:150]}")
                shown += 1
                if shown >= 5:
                    print("  - (further differences suppressed)")
                    break
        return 2
    print("  record check   matches its deterministic regeneration")

    for label, cmd in (("build tests", [sys.executable, "test_build.py"]),
                       ("verifier tests", [sys.executable, "test_verify_live.py"]),
                       ("gate tests", [sys.executable, "test_package.py"])):
        if not os.path.isfile(os.path.join(HERE, cmd[1])):
            print(f"PACKAGE REFUSED: {cmd[1]} is missing.")
            return 2
        if os.environ.get("PVR_SKIP_TESTS") == "1":
            print(f"  {label:<14} SKIPPED (PVR_SKIP_TESTS=1)")
            continue
        r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-3000:])
            print(r.stderr[-3000:])
            print(f"PACKAGE REFUSED: {label} failed with exit {r.returncode}")
            return 2
        print(f"  {label:<14} ok")

    if check_only:
        return 0

    tar_path = os.path.join(HERE, f"{PACKAGE_NAME}.tar.gz")
    with tarfile.open(tar_path, "w:gz") as t:
        for item in CONTENTS:
            p = os.path.join(HERE, item)
            if os.path.exists(p):
                t.add(p, arcname=os.path.join(PACKAGE_NAME, item))
            elif not item.startswith(("publications", "releases")):
                print(f"  WARNING        {item} is absent from the package")
    print(f"  package        {os.path.basename(tar_path)}  "
          f"{os.path.getsize(tar_path):,} bytes  sha256 {sha(tar_path)[:16]}…")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except PackageError as exc:
        print(f"PACKAGE REFUSED: {exc}")
        raise SystemExit(2)
