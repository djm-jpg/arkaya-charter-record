"""Run the acceptance suite against the frozen release and record the evidence.

DM's finding 2, 16 September 2026: this script deleted `verification/evidence/`,
including the retained acceptance suite, and only then tried to copy an
unpackaged sibling directory `../pvr`. A packaged extraction therefore destroyed
its own supplied evidence before discovering it could not rebuild it.

Three changes answer that:

  - The suite lives permanently in `vendor/acceptance_suite/`, inside the
    package. There is no sibling dependency.
  - Every dependency is validated BEFORE anything is created or removed.
  - Each run writes to its own directory under `verification/runs/<stamp>/`.
    Nothing existing is deleted, ever.

DM's finding 4: this script returned success without enforcing what the runs were
supposed to show. Each run now declares its EXPECTED exit status, failing checks
and baseline transition, and the harness fails if an observation deviates. A
verification that cannot fail is not verification.

The frozen release is never mutated. The mutation and removal tests operate on a
served COPY; the release directory is read-only input to this script.

    python3 verification/run_verification.py
"""

import hashlib
import http.server
import json
import os
import shutil
import socket
import socketserver
import stat
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PUBSET = os.path.dirname(HERE)
sys.path.insert(0, PUBSET)

# The expected outcomes live in the package root, imported by both this harness
# and the packaging gate, so the gate can re-derive every outcome independently
# instead of reading the summary this script writes. DM's finding 2.
from expectations import EXPECTED, REQUIRED_RUNS, evaluate_run   # noqa: E402
SUITE = os.path.join(PUBSET, "vendor", "acceptance_suite")
RUNS = os.path.join(HERE, "runs")
BUILDER = os.path.join(PUBSET, "build_publication_set.py")

RELEASE_NAME = os.environ.get("PVR_RELEASE", "publish")
RELEASE_DIR = os.path.join(PUBSET, RELEASE_NAME)
RECORD = os.path.join(RELEASE_DIR, "charter")
RELEASE_META = os.path.join(PUBSET, "releases", f"{RELEASE_NAME}.json")



class VerificationError(Exception):
    pass


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


def validate_dependencies():
    """Everything this run needs, checked before anything is created."""
    problems = []
    if not os.path.isdir(SUITE):
        problems.append(f"acceptance suite not found at vendor/acceptance_suite/")
    else:
        for needed in ("run_acceptance.py", "checks.py", "live.py", "model.py", "fixtures.py"):
            if not os.path.isfile(os.path.join(SUITE, needed)):
                problems.append(f"acceptance suite is incomplete: {needed} missing")
    if not os.path.isfile(os.path.join(RECORD, "manifest.json")):
        problems.append(f"no built release at {RELEASE_NAME}/charter/manifest.json")
    if not os.path.isfile(RELEASE_META):
        problems.append(f"release {RELEASE_NAME} is not frozen: releases/{RELEASE_NAME}.json "
                        f"missing. Build a release before verifying it")
    if not os.path.isfile(BUILDER):
        problems.append("build_publication_set.py missing; the rebuild test cannot run")
    if problems:
        raise VerificationError("; ".join(problems))


STATE = {"dir": None}


def serve():
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=STATE["dir"], **kw)

        def log_message(self, *a):
            pass

    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


class Runner:
    def __init__(self, run_dir, spec_env):
        self.dir = run_dir
        self.spec = spec_env
        self.snapshot = os.path.join(run_dir, "pvr_snapshot.json")
        self.results = []
        self.deviations = []

    def run(self, label, note):
        env = dict(os.environ)
        env.update(self.spec)
        env["PVR_SNAPSHOT"] = self.snapshot
        r = subprocess.run([sys.executable, "run_acceptance.py"],
                           cwd=SUITE, env=env, capture_output=True, text=True)

        shown = " ".join(f"{k}={v}" for k, v in sorted(self.spec.items()))
        header = (f"COMMAND   {shown} PVR_SNAPSHOT=<run>/pvr_snapshot.json \\\n"
                  f"          python3 run_acceptance.py\n"
                  f"CWD       vendor/acceptance_suite\n"
                  f"EXIT      {r.returncode}\n"
                  f"{'-' * 78}\n")
        transcript = os.path.join(self.dir, f"{label}.txt")
        with open(transcript, "w") as f:
            f.write(header + r.stdout + (("\nSTDERR\n" + r.stderr) if r.stderr else ""))

        baseline_after = os.path.join(self.dir, f"{label}.snapshot.json")
        if os.path.exists(self.snapshot):
            shutil.copyfile(self.snapshot, baseline_after)

        live = r.stdout.split("LIVE RUN", 1)[-1]
        failed = sorted(line.strip().split("FAIL", 1)[1].strip()
                        for line in live.splitlines() if line.strip().startswith("FAIL"))
        failed_numbers = {c.split()[0] for c in failed}
        baseline_note = next((line.split("baseline", 1)[1].strip()
                              for line in live.splitlines()
                              if line.strip().startswith("baseline")), None)

        # Enforce the expected outcome, by reading the transcript that was just
        # written rather than the values parsed above. The gate re-does exactly
        # this from the retained file, so the two cannot drift apart.
        want = EXPECTED[label]
        with open(transcript) as f:
            dev = evaluate_run(label, f.read())
        for required in (transcript, baseline_after):
            if not os.path.isfile(required):
                dev.append(f"{label}: evidence file not retained: "
                           f"{os.path.basename(required)}")
        self.deviations.extend(dev)

        self.results.append({
            "label": label,
            "note": note,
            "expected": {"exit_status": want["exit"], "checks_failed": sorted(want["failed"]),
                         "baseline": want["baseline"]},
            "exit_status": r.returncode,
            "checks_failed": failed,
            "baseline_note": baseline_note,
            "as_expected": not dev,
            "deviations": dev,
            "transcript": os.path.relpath(transcript, PUBSET),
            "transcript_sha256": sha(transcript),
            "baseline_after": os.path.relpath(baseline_after, PUBSET),
            "baseline_after_sha256": sha(baseline_after) if os.path.isfile(baseline_after) else None,
        })
        return r


def main():
    validate_dependencies()

    with open(os.path.join(RECORD, "manifest.json")) as f:
        manifest = json.load(f)
    with open(RELEASE_META) as f:
        release = json.load(f)
    manifest_sha = sha(os.path.join(RECORD, "manifest.json"))
    if manifest_sha != release["manifest_sha256"]:
        raise VerificationError(
            f"the release directory does not match its freeze marker "
            f"({manifest_sha[:16]}… vs {release['manifest_sha256'][:16]}…)")

    started = datetime.now(timezone.utc)
    stamp = started.isoformat().replace(":", "").replace("-", "")[:15]
    run_dir = os.path.join(RUNS, stamp)
    if os.path.exists(run_dir):
        raise VerificationError(f"run directory already exists: {run_dir}")
    os.makedirs(run_dir)

    # The frozen release is read-only input. Everything below is served from a
    # working copy, so no test can alter what will be deployed.
    work = tempfile.mkdtemp(prefix="pvr-verify-")
    serving = os.path.join(work, "serving")
    shutil.copytree(RECORD, serving)
    # The mutation and removal runs damage this copy, and the copy inherits the
    # release's modes. A read-only object would fail the run rather than test it.
    for dirpath, dirnames, filenames in os.walk(work):
        for name in dirnames + filenames:
            q = os.path.join(dirpath, name)
            try:
                os.chmod(q, os.stat(q).st_mode | stat.S_IWUSR)
            except OSError:
                pass
    STATE["dir"] = serving

    srv, port = serve()
    base = f"http://127.0.0.1:{port}/"
    spec = {
        "PVR_LINEAGE": "v1,v1.1,v2,v3",
        "PVR_EXPECTED_CURRENT": "v3",
        "PVR_ESTABLISHED": release["release_date"],
        "PUBLIC_VERSION_RECORD_URL": base,
        "PVR_CONTROL_URL": base + "definitely-not-here",
    }
    R = Runner(run_dir, spec)

    try:
        # 1. First observation: two checks cannot be satisfied without a prior
        #    inventory, and the same run establishes the baseline. Both facts
        #    belong in the record; the earlier version stated only the first.
        R.run("run01_first_observation",
              "First observation against an empty baseline store. Checks 8 and 12 "
              "cannot be satisfied: there is no prior inventory to compare against. "
              "This run also ESTABLISHES the baseline, accepting the record as it "
              "stands. It shows the suite reporting the absence of comparison rather "
              "than passing; it is not evidence that the record was preserved.")

        R.run("run02_baseline_established",
              "Second observation, record unchanged. All twelve pass because a prior "
              "inventory now exists to compare against.")

        # 2. Mutation: every published PDF, one at a time. Four tests, each of
        #    which must fail check 11 and must hold the baseline.
        for v in ("v1", "v1.1", "v2", "v3"):
            target = os.path.join(serving, v, f"charter-{v}.pdf")
            original = os.path.join(RECORD, v, f"charter-{v}.pdf")
            before, after_bytes = sha(target), None
            with open(target, "ab") as f:
                f.write(b"MUTATION")
            after_bytes = sha(target)
            R.run(f"run03_{v.replace('.', '_')}_mutation",
                  f"Deliberate mutation of charter-{v}.pdf in the served copy: 8 bytes "
                  f"appended. {before} -> {after_bytes}. Check 11 must fail and the "
                  f"baseline must be HELD, so a repeat run against the altered file "
                  f"fails again rather than accepting it.")
            shutil.copyfile(original, target)
            if sha(target) != before:
                raise VerificationError(f"{v} not restored in the served copy")

        # 3. Two different removals. Taking the FILE away leaves the index still
        #    listing the version: membership is retained and retrieval fails.
        #    Taking the ENTRY out of the index is what a silent removal looks
        #    like, and that is what check 12 detects. An earlier draft of this
        #    script conflated them and claimed the first exercised check 12.
        held = os.path.join(work, "_removed")
        shutil.move(os.path.join(serving, "v1.1"), held)
        R.run("run04a_object_removed",
              "The v1.1 PDF is removed while the index still lists it. Retrievability "
              "(check 10) fails. Membership is unaffected because the index has not "
              "changed: the two failures are distinct and this run does not exercise "
              "check 12.")
        shutil.move(held, os.path.join(serving, "v1.1"))

        index_path = os.path.join(serving, "index.json")
        with open(index_path) as f:
            doc = json.load(f)
        doc["versions"] = [v for v in doc["versions"] if v["version"] != "v1.1"]
        with open(index_path, "w") as f:
            json.dump(doc, f, indent=2)
        R.run("run04b_entry_removed_from_index",
              "The v1.1 ENTRY is removed from the published index while the PDF "
              "remains in place. This is what a silent removal looks like from "
              "outside, and membership retention against the accepted baseline is "
              "what detects it.")
        shutil.copyfile(os.path.join(RECORD, "index.json"), index_path)

        R.run("run05_after_restoration",
              "The served copy is restored to the frozen release. The run is clean "
              "again, which shows the failures above tracked the record rather than "
              "latching.")

        # 4. Rebuild reproducibility, into a SEPARATE directory. Finding 1: the
        #    release is built once and packaged as built; a rebuild is a
        #    comparison, never a replacement.
        rebuild_dir = os.path.join(work, "rebuild")
        rb = subprocess.run(
            [sys.executable, BUILDER], cwd=PUBSET, capture_output=True, text=True,
            env=dict(os.environ,
                     PVR_RELEASE_DIR=rebuild_dir,
                     # The scratch build keeps its freeze marker in the temp
                     # directory. Writing it into releases/ put a marker in the
                     # package that made the same comparison refuse on a fresh
                     # extraction.
                     PVR_RELEASE_META_DIR=os.path.join(work, "releases"),
                     PVR_RELEASE_DATE=release["release_date"],
                     PVR_SEQUENCE=str(release["sequence"]),
                     PVR_CANONICAL_BASE=release["canonical_base"],
                     PVR_ALLOW_DATE_MISMATCH="1",
                     PVR_DATE_MISMATCH_REASON=(
                         "reproducibility comparison against the frozen release; "
                         "this build is never deployed")))
        before_tree = tree(RECORD)
        after_tree = tree(os.path.join(rebuild_dir, "charter")) if rb.returncode == 0 else {}
        expected_change = set(manifest["not_bit_reproducible"]["paths"])
        changed = {p for p in before_tree if before_tree[p] != after_tree.get(p)}
        rebuild = {
            "exit_status": rb.returncode,
            "stderr": rb.stderr[-2000:] if rb.returncode != 0 else "",
            "built_into": "a separate directory; the frozen release was not touched",
            "objects_compared": len(before_tree),
            "expected_to_change": sorted(expected_change),
            "changed": sorted(changed),
            "unexpected_changes": sorted(changed - expected_change),
            "expected_change_not_observed": sorted(expected_change - changed),
            "membership_identical": sorted(before_tree) == sorted(after_tree),
            "pdfs_compared": sorted(p for p in before_tree if p.endswith(".pdf")),
            "passed": (rb.returncode == 0
                       and not (changed - expected_change)
                       and sorted(before_tree) == sorted(after_tree)),
        }
        with open(os.path.join(run_dir, "run06_rebuild.json"), "w") as f:
            json.dump({"before": before_tree, "after": after_tree, "result": rebuild},
                      f, indent=2)
        if not rebuild["passed"]:
            # The builder reports refusals on stdout; stderr is empty for a
            # controlled refusal and populated only for a crash. Taking the last
            # line of stderr unconditionally raised IndexError and lost the
            # actual reason, which the fresh-extraction run exposed.
            detail = (rb.stdout.strip() or rb.stderr.strip() or "no output").splitlines()
            rebuild["refusal"] = detail[0] if detail else ""
            R.deviations.append(
                "rebuild: " + (rebuild["refusal"] if rb.returncode
                               else f"unexpected changes {rebuild['unexpected_changes']}"))

        # 5. Observation against the rebuilt set, served in place of the copy.
        #    index.json and index.html are bit-reproducible, so a clean run here
        #    shows the rebuild produced the same record, not merely a valid one.
        if rb.returncode == 0:
            STATE["dir"] = os.path.join(rebuild_dir, "charter")
            R.run("run06_after_rebuild",
                  "Observation against the independently rebuilt set. The index, the "
                  "page and the four PDFs are bit-identical to the frozen release, so "
                  "the preservation checks pass against the same accepted baseline.")
    finally:
        srv.shutdown()
        srv.server_close()

    suite_files = dict(sorted(tree(SUITE).items()))
    suite_digest = hashlib.sha256(
        "".join(f"{k}:{v}\n" for k, v in suite_files.items()).encode()).hexdigest()

    results = {
        "schema": "arkaya-verification-results/2",
        "generated_at": started.isoformat(),
        "run_dir": os.path.relpath(run_dir, PUBSET),
        "scope": "Local HTTP, one process, one machine. These runs say nothing about "
                 "the behaviour of record.arkayarisk.com, which does not yet exist.",
        "spec_parameters": spec | {"PUBLIC_VERSION_RECORD_URL": "http://127.0.0.1:<port>/",
                                   "PVR_CONTROL_URL": "http://127.0.0.1:<port>/definitely-not-here"},
        "acceptance_suite": {
            "source": "OPS_QA_PublicVersionRecord_AcceptanceSuite_v10",
            "retained_at": "vendor/acceptance_suite/",
            "files": suite_files,
            "digest_of_file_digests": suite_digest,
        },
        "record_under_test": {
            "release": RELEASE_NAME,
            "manifest_sha256": manifest_sha,
            "sequence": manifest["sequence"],
            "release_date": release["release_date"],
            "builder": manifest["builder"],
            "frozen": True,
            "mutated_during_testing": False,
        },
        "expected_labels": list(REQUIRED_RUNS),
        "rebuild_comparison": "run06_rebuild.json",
        "runs": R.results,
        "rebuild": rebuild,
        "all_runs_as_expected": not R.deviations,
        "deviations": R.deviations,
    }
    with open(os.path.join(run_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    shutil.rmtree(work, ignore_errors=True)

    for r in R.results:
        mark = "ok " if r["as_expected"] else "DEV"
        print(f"  {mark} {r['label']:<32} exit {r['exit_status']}  "
              f"failed: {', '.join(c.split()[0] for c in r['checks_failed']) or 'none'}  "
              f"baseline: {r['baseline_note']}")
    print(f"  {'ok ' if rebuild['passed'] else 'DEV'} rebuild{'':<25} "
          f"{rebuild['objects_compared']} objects, {len(rebuild['pdfs_compared'])} PDFs, "
          f"unexpected changes: {rebuild['unexpected_changes'] or 'none'}")
    print(f"\n  evidence -> {os.path.relpath(run_dir, PUBSET)}")
    if R.deviations:
        print("\n  VERIFICATION FAILED. Observations deviated from what was expected:")
        for d in R.deviations:
            print(f"    - {d}")
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as exc:
        print(f"VERIFICATION REFUSED: {exc}")
        print("Nothing was created or removed.")
        raise SystemExit(2)
