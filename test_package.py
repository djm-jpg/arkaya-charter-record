"""Prove the packaging gate and the publication recorder refuse what they claim to refuse.

DM's finding 4, 16 September 2026: the gate's production-record check tested
whether a digest occurred anywhere in the evidence, not whether it belonged to
the object it was printed against. Substituting v1.1's valid digest into v1's row
passed. The verification runner likewise returned success without enforcing the
outcomes it described.

DM's finding 5: publication was recorded before it occurred.

Every test below breaks one thing and requires the refusal. Tests that only ever
run against a correct package prove nothing about an incorrect one.

Run: python3 test_package.py
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def make_writable(root):
    """Every file in a sandbox must be writable by the tests that damage it.

    The package ships `inputs/*.pdf` read-only, `shutil.copytree` preserves the
    mode, and a test that appends to one then fails with PermissionError rather
    than testing what it claims. It passed here only because this container runs
    as root. DM reproduced it on a normal account: the gate errored on
    `test_an_input_edited_after_freezing_is_rejected`, so `package.py` could not
    complete on an ordinary checkout.

    Fixed for the whole sandbox rather than for the one test that tripped it,
    because any later test that damages a shipped read-only file would hit the
    same thing.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            p = os.path.join(dirpath, name)
            try:
                os.chmod(p, os.stat(p).st_mode | stat.S_IWUSR)
            except OSError:
                pass

# Copied into every sandbox. `vendor` is included because package.py checks the
# retained evidence paths that point into the runs, not the suite itself.
SANDBOX = ("publish", "releases", "verification", "inputs", "vendor", "publications",
           "build_publication_set.py", "record_publication.py", "package.py",
           "expectations.py", "verify_live.py", "test_build.py",
           "test_verify_live.py", "test_package.py", "README_source.md",
           "DEPLOY.md", "PUBLICATION_LOG.md")

# Written into a release marker by `record_publication.py`: the first two by
# `--bind`, the rest when a publication is recorded.
PUBLICATION_MARKER_KEYS = ("bound_at", "binding_bound", "release_commit",
                           "release_tag", "published_on", "publication_snapshot")

# The marker fields a freshly built, frozen release carries. Anything outside
# this set and PUBLICATION_MARKER_KEYS is unclassified and stops the reset.
BASELINE_MARKER_KEYS = frozenset((
    "schema", "release_dir", "sequence", "release_date", "built_at",
    "canonical_base", "manifest_sha256", "index_sha256", "root_pointer_sha256",
    "builder", "date_mismatch_reason", "versions_awaiting_first_publication",
    "published", "state"))

CANDIDATE_STATE = "frozen release candidate; not deployed, not published"


def _copy_package_into(root):
    for item in SANDBOX:
        src = os.path.join(HERE, item)
        if not os.path.exists(src):
            continue
        dst = os.path.join(root, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copyfile(src, dst)
    make_writable(root)


_UNPUBLISHED_RECORD = None


def unpublished_production_record():
    """The production record as the gate generates it for an unpublished release.

    `verification/` is copied into every sandbox and carries
    PRODUCTION_RECORD.md. `package.py` regenerates that file whenever it runs,
    so once a publication has been recorded the working tree holds the published
    record. Copied unchanged into a sandbox that has been reset to unpublished,
    it is no longer its own deterministic regeneration and `package.py --check`
    refuses. Deleting it is not the answer either: the gate then refuses because
    the record has not been generated, and tests that read the record before
    running the gate have nothing to read.

    The record is derived, so the baseline is whatever the gate itself produces
    from a reset tree. Generated once per process and cached. Generation is
    deterministic and takes no reading of the clock, so one generation serves
    every sandbox.
    """
    global _UNPUBLISHED_RECORD
    if _UNPUBLISHED_RECORD is None:
        scratch = tempfile.mkdtemp(prefix="gate-record-")
        try:
            _copy_package_into(scratch)
            reset_publication_state(scratch)
            record = os.path.join(scratch, "verification", "PRODUCTION_RECORD.md")
            if os.path.isfile(record):
                os.unlink(record)
            # PVR_SKIP_TESTS is right here and only here: this run exists to
            # regenerate one derived file, not to gate anything. The suites it
            # skips are the suites this module is.
            env = dict(os.environ, PVR_SKIP_TESTS="1")
            r = subprocess.run([sys.executable, "package.py"], cwd=scratch,
                               env=env, capture_output=True, text=True)
            if r.returncode != 0 or not os.path.isfile(record):
                raise AssertionError(
                    "could not generate the unpublished production record that "
                    "every sandbox starts from:\n" + r.stdout[-3000:] + r.stderr[-1000:])
            with open(record) as f:
                _UNPUBLISHED_RECORD = f.read()
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    return _UNPUBLISHED_RECORD


def reset_publication_state(root):
    """Clear the recorded publication and the release binding.

    The state half of the reset, separated so that the cached record above can
    use it without recursing. Callers want `reset_to_unpublished`.
    """
    releases = os.path.join(root, "releases")
    for name in sorted(os.listdir(releases)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(releases, name)
        with open(path) as f:
            marker = json.load(f)

        unknown = set(marker) - BASELINE_MARKER_KEYS - set(PUBLICATION_MARKER_KEYS)
        if unknown:
            raise AssertionError(
                f"{name} carries unclassified marker field(s) {sorted(unknown)}. "
                f"Add each to BASELINE_MARKER_KEYS if a frozen release carries it, "
                f"or to PUBLICATION_MARKER_KEYS if recording writes it. Left "
                f"unclassified it would leak publication state into every sandbox.")

        for key in PUBLICATION_MARKER_KEYS:
            marker.pop(key, None)
        marker["published"] = False
        marker["state"] = CANDIDATE_STATE
        with open(path, "w") as f:
            json.dump(marker, f, indent=2)

        assert marker["published"] is False, name
        assert not [k for k in PUBLICATION_MARKER_KEYS if k in marker], name

    # publications/ ships carrying only its own README. Recorded sequences are
    # directories beside it and must not survive into a sandbox.
    publications = os.path.join(root, "publications")
    if os.path.isdir(publications):
        for name in sorted(os.listdir(publications)):
            if name == "README.md":
                continue
            target = os.path.join(publications, name)
            shutil.rmtree(target) if os.path.isdir(target) else os.unlink(target)
        assert os.listdir(publications) == ["README.md"], os.listdir(publications)


def reset_to_unpublished(root):
    """Return a sandbox to an explicit unpublished, unbound baseline.

    DM's finding, 16 September 2026, at runbook step 97. `Sandbox` copied
    `releases`, `publications` and `verification` verbatim out of the working
    tree. That was harmless until a publication had been recorded; afterwards
    every sandbox inherited `published: true`, the release binding, the
    `publications/1` snapshot and the regenerated published production record.
    31 of 55 tests then failed on fixture state rather than on the behaviour
    under test, so `package.py` could never complete once
    `record_publication.py` had run and runbook steps 88 and 97 could not both
    succeed in the order the runbook gives them. The sandbox was not hermetic.

    Reproduced on a pristine extraction of the shipped archive by injecting
    nothing but the post-publication state: `releases/publish.json` alone gave
    31 failures, `publications/1` alone gave 15, both gave 31, and the
    untouched tree passed 55 of 55.

    The reset is explicit, not best-effort. The baseline is asserted afterwards,
    so a marker field added later that records publication stops the fixture
    here with a message instead of silently contaminating it again. The ledgers
    `first_publication.json` and `published_indexes.json` need no handling: they
    are not in SANDBOX, so they are never copied, and the recorder writes them.
    """
    reset_publication_state(root)
    record = os.path.join(root, "verification", "PRODUCTION_RECORD.md")
    if os.path.isdir(os.path.dirname(record)):
        with open(record, "w") as f:
            f.write(unpublished_production_record())


class Sandbox(unittest.TestCase):
    """A private copy of the package, built and verified, explicitly unpublished.

    Every sandbox starts from the same baseline whatever state the working tree
    is in, so the suite behaves identically before and after a publication has
    been recorded.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="gate-test-")
        for item in SANDBOX:
            src = os.path.join(HERE, item)
            if not os.path.exists(src):
                continue
            dst = os.path.join(self.dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copyfile(src, dst)
        make_writable(self.dir)
        reset_to_unpublished(self.dir)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def gate(self, *args):
        # PVR_SKIP_TESTS stops the gate re-entering this file, which would
        # recurse without terminating.
        env = dict(os.environ, PVR_SKIP_TESTS="1")
        return subprocess.run([sys.executable, "package.py", *args],
                              cwd=self.dir, env=env, capture_output=True, text=True)

    def record_path(self):
        return os.path.join(self.dir, "verification", "PRODUCTION_RECORD.md")

    def results_path(self):
        """The newest run that actually completed.

        A crashed or interrupted run leaves a directory with no results.json.
        Taking simply the newest directory picked that one up on a fresh
        extraction and the tests failed on a missing file rather than on what
        they were testing.
        """
        runs = os.path.join(self.dir, "verification", "runs")
        complete = sorted(d for d in os.listdir(runs)
                          if os.path.isfile(os.path.join(runs, d, "results.json")))
        self.assertTrue(complete, "no completed verification run in the sandbox")
        return os.path.join(runs, complete[-1], "results.json")

    def all_results_paths(self):
        runs = os.path.join(self.dir, "verification", "runs")
        return [os.path.join(runs, d, "results.json") for d in sorted(os.listdir(runs))
                if os.path.isfile(os.path.join(runs, d, "results.json"))]

    def edit_results(self, fn, every=False):
        """Edit the newest completed run, or every run.

        A packaged extraction ships the run it was packaged with, and running
        verification again adds another. Editing only the newest left the gate
        legitimately falling back to the older valid run, so a test meant to
        prove a refusal was not exercising its own condition. Tests about
        "there is no valid evidence" must edit every run.
        """
        for p in (self.all_results_paths() if every else [self.results_path()]):
            with open(p) as f:
                d = json.load(f)
            fn(d)
            with open(p, "w") as f:
                json.dump(d, f, indent=2)

    def release_meta_path(self):
        return os.path.join(self.dir, "releases", "publish.json")


class TestGateBaseline(Sandbox):

    def test_the_untouched_package_passes(self):
        r = self.gate("--check")
        self.assertEqual(0, r.returncode, r.stdout[-3000:])
        self.assertIn("matches its deterministic regeneration", r.stdout)


class TestProductionRecord(Sandbox):

    def test_a_digest_moved_to_the_wrong_row_is_rejected(self):
        """DM's exact reproduction: v1.1's valid digest substituted into v1's row.

        The old check asked whether the digest appeared anywhere in the evidence.
        It did, so it passed. The record is now compared against its
        deterministic regeneration, and a digest in the wrong row is a different
        file.
        """
        with open(self.record_path()) as f:
            text = f.read()
        v1 = "03794ff916330d36e551ccb0d98a173c5205e98c27eb35124a7466eedc776e6e"
        v11 = "2d55ac0b81e07fee580e4784126c2d581b7acaec70ee55f84f5f0bec1bac0897"
        self.assertIn(v1, text)
        # Replace only the row for v1 in the published-objects table.
        text = text.replace(f"| v1 | `v1/charter-v1.pdf` | `{v1}`",
                            f"| v1 | `v1/charter-v1.pdf` | `{v11}`")
        with open(self.record_path(), "w") as f:
            f.write(text)

        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("not its deterministic regeneration", r.stdout)

    def test_a_single_character_change_is_rejected(self):
        with open(self.record_path()) as f:
            text = f.read()
        with open(self.record_path(), "w") as f:
            f.write(text.replace("751972efbfa4fb60", "751972efbfa4fb61", 1))
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("not its deterministic regeneration", r.stdout)

    def test_an_added_claim_is_rejected(self):
        """Prose cannot be added to a generated record without regenerating it."""
        with open(self.record_path(), "a") as f:
            f.write("\n**This set has been published and independently verified.**\n")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("not its deterministic regeneration", r.stdout)

    def test_a_missing_record_is_rejected(self):
        os.unlink(self.record_path())
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)


class TestVerificationEvidence(Sandbox):

    def test_a_deviating_run_is_rejected(self):
        self.edit_results(lambda d: (d["runs"][1].update(as_expected=False,
                                                         deviations=["exit 1, expected 0"]),
                                     d.update(all_runs_as_expected=False,
                                              deviations=["run02: exit 1, expected 0"])),
                          every=True)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("the transcripts say", r.stdout)

    def test_a_claim_of_success_without_the_per_run_evidence_is_rejected(self):
        """all_runs_as_expected true while a run says otherwise must not pass."""
        self.edit_results(lambda d: d["runs"][0].update(as_expected=False, deviations=[]),
                          every=True)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("the transcript says", r.stdout)

    def test_missing_retained_evidence_is_rejected(self):
        for p in self.all_results_paths():
            with open(p) as f:
                d = json.load(f)
            target = os.path.join(self.dir, d["runs"][0]["transcript"])
            if os.path.exists(target):
                os.unlink(target)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("retained evidence missing", r.stdout)

    def test_a_rebuild_claim_contradicting_the_comparison_is_rejected(self):
        """The gate ignores the claim, but a false claim is still a finding."""
        self.edit_results(lambda d: d["rebuild"].update(
            passed=False, unexpected_changes=["v3/charter-v3.pdf"]), every=True)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("the retained comparison says", r.stdout)

    def test_evidence_for_a_different_manifest_is_rejected(self):
        self.edit_results(lambda d: d["record_under_test"].update(manifest_sha256="f" * 64),
                          every=True)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("no verification run was made against the frozen manifest", r.stdout)


class TestSourceIdentities(Sandbox):
    """DM's finding 1: the shipped files must be the recorded files.

    The v5 archive recorded one builder digest in both the manifest and the
    freeze marker while shipping a different builder. The two records agreed
    with each other, which is what concealed it: nothing compared either to the
    file on disk.
    """

    def test_a_builder_edited_after_freezing_is_rejected(self):
        with open(os.path.join(self.dir, "build_publication_set.py"), "a") as f:
            f.write("\n# edited after the release was frozen\n")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("the shipped builder hashes to", r.stdout)
        self.assertIn("rebuild and refreeze", r.stdout)

    def test_an_input_edited_after_freezing_is_rejected(self):
        target = os.path.join(self.dir, "inputs", "charter-v2.pdf")
        self.assertTrue(os.access(target, os.W_OK),
                        "the sandbox copy must be writable, or this test cannot run")
        with open(target, "ab") as f:
            f.write(b"X")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("inputs/charter-v2.pdf", r.stdout)

    def test_a_readme_source_edited_after_freezing_is_rejected(self):
        with open(os.path.join(self.dir, "README_source.md"), "a") as f:
            f.write("\nappended\n")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("README_source.md", r.stdout)

    def test_an_altered_vendored_suite_is_rejected(self):
        with open(os.path.join(self.dir, "vendor", "acceptance_suite", "checks.py"), "a") as f:
            f.write("\n# altered\n")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("acceptance suite file altered", r.stdout)

    def test_a_freeze_marker_diverging_from_the_manifest_is_rejected(self):
        with open(self.release_meta_path()) as f:
            meta = json.load(f)
        meta["builder"]["sha256"] = "b" * 64
        with open(self.release_meta_path(), "w") as f:
            json.dump(meta, f)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("builder block differs from the manifest", r.stdout)


class TestEvidenceIsRederived(Sandbox):
    """DM's finding 2: the gate trusted labels instead of the evidence."""

    def test_a_contradicted_summary_is_rejected(self):
        """DM's reproduction: exit 99 with a digest failure, as_expected untouched."""
        self.edit_results(lambda d: d["runs"][1].update(
            exit_status=99,
            checks_failed=["11 entry digests match  digest mismatch: v2"]), every=True)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("contradicts its transcript", r.stdout)

    def test_a_transcript_replaced_with_unrelated_text_is_rejected(self):
        """DM's reproduction: the gate verified existence, not content."""
        for p in self.all_results_paths():
            with open(p) as f:
                d = json.load(f)
            for run in d["runs"]:
                target = os.path.join(self.dir, run["transcript"])
                if os.path.exists(target):
                    with open(target, "w") as f:
                        f.write("this is not a transcript\n")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("transcript", r.stdout)

    def test_a_transcript_altered_since_it_was_written_is_rejected(self):
        with open(self.results_path()) as f:
            d = json.load(f)
        target = os.path.join(self.dir, d["runs"][0]["transcript"])
        with open(target, "a") as f:
            f.write("\n")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("altered since it was written", r.stdout)

    def test_a_rebuild_claimed_to_pass_is_recomputed(self):
        """`passed` is ignored; the verdict comes from the retained trees."""
        for p in self.all_results_paths():
            run_dir = os.path.dirname(p)
            comp = os.path.join(run_dir, "run06_rebuild.json")
            with open(comp) as f:
                d = json.load(f)
            key = next(k for k in d["after"] if k.endswith("charter-v3.pdf"))
            d["after"][key] = "c" * 64
            d["result"]["passed"] = True
            d["result"]["unexpected_changes"] = []
            with open(comp, "w") as f:
                json.dump(d, f, indent=2)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("rebuild: unexpected differences", r.stdout)

    def test_a_missing_required_run_is_rejected(self):
        self.edit_results(lambda d: d.__setitem__(
            "runs", [x for x in d["runs"] if x["label"] != "run05_after_restoration"]),
            every=True)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("expected run not present: run05_after_restoration", r.stdout)


class TestReleaseIntegrity(Sandbox):

    def test_a_release_changed_after_freezing_is_rejected(self):
        target = os.path.join(self.dir, "publish", "charter", "README.md")
        with open(target, "a") as f:
            f.write("\nappended after freezing\n")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("manifest", r.stdout)

    def test_an_unnamed_served_file_is_rejected(self):
        with open(os.path.join(self.dir, "publish", "charter", "extra.txt"), "w") as f:
            f.write("not in the manifest")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("served but not named in the manifest", r.stdout)

    def test_a_missing_freeze_marker_is_rejected(self):
        os.unlink(self.release_meta_path())
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("freeze marker", r.stdout)


class PublicationBase(Sandbox):
    """Helpers only. No test_ methods, so subclasses do not inherit each other's."""

    def evidence(self, **overrides):
        with open(self.release_meta_path()) as f:
            meta = json.load(f)
        ev = {
            "verified_at": meta["release_date"] + "T10:00:00+00:00",
            "base": meta["canonical_base"] + "/",
            "canonical_uri": meta["canonical_base"] + "/",
            "rehearsal": False,
            "release": "publish",
            "release_frozen": True,
            "manifest_sha256": meta["manifest_sha256"],
            "passed": True,
            "production_approval": True,
            "approval_blockers": [],
            "findings": [],
            "checks": [],
        }
        ev.update(overrides)
        path = os.path.join(self.dir, "evidence.json")
        with open(path, "w") as f:
            json.dump(ev, f, indent=2)
        return path

    COMMIT = "a" * 40

    def bind(self, commit=None, tag="release-001"):
        return subprocess.run(
            [sys.executable, "record_publication.py", "--bind",
             "--commit", commit or self.COMMIT, "--tag", tag],
            cwd=self.dir, capture_output=True, text=True)

    def record(self, evidence_path, *extra, commit=None, tag="release-001"):
        return subprocess.run(
            [sys.executable, "record_publication.py", "--evidence", evidence_path,
             "--deploy-id", "68c9a1f0deadbeef00000001",
             "--deploy-permalink", "https://68c9a1f0--arkaya-record.netlify.app",
             "--commit", commit or self.COMMIT, "--tag", tag, *extra],
            cwd=self.dir, capture_output=True, text=True)

    # Bound in setUp, before any test damages the release: binding validates the
    # release, so a test that damages it first would fail at the wrong step.
    AUTOBIND = True

    def setUp(self):
        super().setUp()
        if self.AUTOBIND:
            r = self.bind()
            self.assertEqual(0, r.returncode, r.stdout)


class TestRecordPublication(PublicationBase):
    """Finding 5: publication is recorded from evidence that it happened."""

    def test_a_rehearsal_cannot_record_publication(self):
        r = self.record(self.evidence(rehearsal=True, production_approval=False,
                                      approval_blockers=["rehearsal over plain HTTP"]))
        self.assertEqual(2, r.returncode)
        self.assertIn("rehearsal", r.stdout)
        # publications/ ships with the package (it carries its own README), so the
        # assertion is that no sequence was written into it.
        self.assertFalse(os.path.isdir(os.path.join(self.dir, "publications", "1")))

    def test_a_failed_verification_cannot_record_publication(self):
        r = self.record(self.evidence(passed=False, production_approval=False,
                                      findings=["digest v2/charter-v2.pdf: mismatch"]))
        self.assertEqual(2, r.returncode)
        self.assertIn("did not pass", r.stdout)

    def test_evidence_for_a_different_manifest_cannot_record_publication(self):
        r = self.record(self.evidence(manifest_sha256="f" * 64))
        self.assertEqual(2, r.returncode)
        self.assertIn("taken against manifest", r.stdout)

    def test_evidence_from_another_address_cannot_record_publication(self):
        r = self.record(self.evidence(base="https://staging.example/charter/"))
        self.assertEqual(2, r.returncode)
        self.assertIn("not the canonical address", r.stdout)

    def test_verification_on_a_different_day_cannot_record_publication(self):
        """The set carries its date on its face; a later observation is not it."""
        r = self.record(self.evidence(verified_at="2026-10-01T10:00:00+00:00"))
        self.assertEqual(2, r.returncode)
        self.assertIn("on its face", r.stdout)

    def test_a_passing_verification_records_publication_once(self):
        ev = self.evidence()
        r = self.record(ev)
        self.assertEqual(0, r.returncode, r.stdout)

        with open(os.path.join(self.dir, "first_publication.json")) as f:
            self.assertEqual({"v1", "v1.1", "v2", "v3"}, set(json.load(f)["versions"]))
        with open(os.path.join(self.dir, "published_indexes.json")) as f:
            self.assertEqual({"1"}, set(json.load(f)["versions"]))

        # The snapshot is the index itself, not only its hash. Finding 6.
        snap = os.path.join(self.dir, "publications", "1")
        for name in ("index.json", "manifest.json", "manifest.json.sha256",
                     "release.json", "live_verification.json", "publication.json"):
            self.assertTrue(os.path.isfile(os.path.join(snap, name)), name)

        # Recording twice must not be possible. The release marker refuses first.
        again = self.record(ev)
        self.assertEqual(2, again.returncode)
        self.assertIn("already recorded as published", again.stdout)

    def test_clearing_the_marker_does_not_let_a_publication_be_rewritten(self):
        """The snapshot and the ledgers, not the marker alone, define the state."""
        ev = self.evidence()
        self.assertEqual(0, self.record(ev).returncode)
        with open(self.release_meta_path()) as f:
            meta = json.load(f)
        meta["published"] = False
        with open(self.release_meta_path(), "w") as f:
            json.dump(meta, f)
        again = self.record(ev)
        self.assertEqual(2, again.returncode)
        self.assertIn("INCOMPLETE recording", again.stdout)
        self.assertIn("release_marked", again.stdout)

    def test_a_release_with_an_altered_object_cannot_record_publication(self):
        """DM's finding 4: the recorder validated the manifest, not what it describes.

        With synthetic approved evidence and index.json replaced by {}, the
        previous recorder reported no problems and would have snapshotted an
        index inconsistent with its own recorded digest.
        """
        with open(os.path.join(self.dir, "publish", "charter", "index.json"), "w") as f:
            f.write("{}")
        r = self.record(self.evidence())
        self.assertEqual(2, r.returncode)
        self.assertIn("index.json", r.stdout)
        self.assertFalse(os.path.isdir(os.path.join(self.dir, "publications", "1")))

    def test_a_release_with_an_unnamed_extra_object_cannot_record_publication(self):
        with open(os.path.join(self.dir, "publish", "charter", "extra.txt"), "w") as f:
            f.write("smuggled in")
        r = self.record(self.evidence())
        self.assertEqual(2, r.returncode)
        self.assertIn("not named in the manifest", r.stdout)

    def test_a_missing_pointer_page_cannot_record_publication(self):
        os.unlink(os.path.join(self.dir, "publish", "index.html"))
        r = self.record(self.evidence())
        self.assertEqual(2, r.returncode)
        self.assertIn("pointer page", r.stdout)

    def test_a_venue_serving_another_manifest_cannot_record_publication(self):
        r = self.record(self.evidence(served_manifest_sha256="e" * 64))
        self.assertEqual(2, r.returncode)
        self.assertIn("the venue served manifest", r.stdout)

    def test_the_production_record_follows_recorded_state(self):
        """DM, 17 September: the record asserted non-publication unconditionally.

        The release sequence regenerates the record after recording, so the
        packaged record would have contradicted the publication it shipped with.
        """
        with open(self.record_path()) as f:
            before = f.read()
        self.assertIn("Publication not yet authorised or observed", before)
        self.assertIn("dated pre-deployment assessment", before)

        self.assertEqual(0, self.record(self.evidence()).returncode)
        r = self.gate()
        self.assertEqual(0, r.returncode, r.stdout[-3000:])

        with open(self.record_path()) as f:
            after = f.read()
        self.assertNotIn("Publication not yet authorised or observed", after)
        self.assertNotIn("no Netlify project, repository or DNS record had been created", after)
        self.assertIn("**Status: published.", after)
        self.assertIn("68c9a1f0deadbeef00000001", after)          # deploy id
        self.assertIn("a" * 40, after)                            # release commit
        self.assertIn("publications/1/", after)
        # And it still refuses a hand-edited record.
        with open(self.record_path(), "w") as f:
            f.write(after.replace("**Status: published.", "**Status: independently audited."))
        self.assertEqual(2, self.gate("--check").returncode)

    def test_a_published_release_cannot_be_rebuilt(self):
        self.record(self.evidence())
        r = subprocess.run([sys.executable, "build_publication_set.py"],
                           cwd=self.dir, capture_output=True, text=True,
                           env=dict(os.environ, PVR_REPLACE_RELEASE="1"))
        self.assertEqual(2, r.returncode)
        self.assertIn("published", r.stdout)


class TestReleaseBinding(PublicationBase):
    """DM's point of 17 September: publication-001 must be bound to release-001.

    The manifest digest was already bound. The commit was free text: recorded,
    never checked. Approval evidence for one frozen release could in principle
    have been recorded against another.
    """

    AUTOBIND = False

    def test_recording_without_a_binding_is_refused(self):
        r = self.record(self.evidence())
        self.assertEqual(2, r.returncode)
        self.assertIn("not bound to a commit", r.stdout)
        self.assertFalse(os.path.isdir(os.path.join(self.dir, "publications", "1")))

    def test_recording_with_a_different_commit_is_refused(self):
        self.assertEqual(0, self.bind().returncode)
        r = self.record(self.evidence(), commit="b" * 40)
        self.assertEqual(2, r.returncode)
        self.assertIn("is not the commit bound to this frozen release", r.stdout)

    def test_recording_with_a_different_tag_is_refused(self):
        self.assertEqual(0, self.bind().returncode)
        r = self.record(self.evidence(), tag="publication-001")
        self.assertEqual(2, r.returncode)
        self.assertIn("is not the tag bound", r.stdout)

    def test_a_release_is_bound_once(self):
        self.assertEqual(0, self.bind().returncode)
        again = self.bind(commit="c" * 40)
        self.assertEqual(2, again.returncode)
        self.assertIn("already bound", again.stdout)

    def test_rebinding_the_same_values_is_harmless(self):
        self.assertEqual(0, self.bind().returncode)
        self.assertEqual(0, self.bind().returncode)

    def test_a_malformed_commit_is_refused(self):
        r = self.bind(commit="not-a-sha")
        self.assertEqual(2, r.returncode)
        self.assertIn("not a 40-character commit SHA", r.stdout)

    def test_binding_a_release_that_has_drifted_is_refused(self):
        with open(os.path.join(self.dir, "publish", "charter", "README.md"), "a") as f:
            f.write("\ndrifted\n")
        r = self.bind()
        self.assertEqual(2, r.returncode)
        self.assertIn("NOT BOUND", r.stdout)

    def test_the_binding_states_what_it_does_not_establish(self):
        self.assertEqual(0, self.bind().returncode)
        with open(self.release_meta_path()) as f:
            meta = json.load(f)
        self.assertEqual("a" * 40, meta["release_commit"])
        self.assertIn("does not verify that the commit exists", meta["binding_bound"])

    def test_the_snapshot_carries_the_bound_commit_not_the_supplied_one(self):
        self.assertEqual(0, self.bind().returncode)
        self.assertEqual(0, self.record(self.evidence()).returncode)
        with open(os.path.join(self.dir, "publications", "1", "publication.json")) as f:
            pub = json.load(f)
        self.assertEqual("a" * 40, pub["release_commit"])
        self.assertEqual("release-001", pub["release_tag"])
        self.assertIsNotNone(pub["release_bound_at"])


class TestReplacementIdentifiers(PublicationBase):
    """DM, 17 September: the record hard-coded release-001 and publication-001.

    A replacement release takes the next identifiers, so a record naming the
    first attempt's tags would contradict the publication it describes.
    """

    AUTOBIND = False
    COMMIT = "7c1d" + "0" * 36

    def note(self, tag="publication-002", commit="b" * 40):
        args = [sys.executable, "record_publication.py", "--note-evidence-tag",
                "--evidence-tag", tag]
        if commit:
            args += ["--evidence-commit", commit]
        return subprocess.run(args, cwd=self.dir, capture_output=True, text=True)

    def test_replacement_tags_reach_the_production_record(self):
        self.assertEqual(0, self.bind(tag="release-002").returncode)
        self.assertEqual(0, self.record(self.evidence(), tag="release-002").returncode)
        self.assertEqual(0, self.note().returncode)
        r = self.gate()
        self.assertEqual(0, r.returncode, r.stdout[-3000:])
        with open(self.record_path()) as f:
            text = f.read()
        self.assertIn("`release-002` (tag on the frozen-release commit)", text)
        self.assertIn("`publication-002` (tag on the publication-evidence commit)", text)
        self.assertNotIn("release-001", text)
        self.assertNotIn("publication-001", text)

    def test_an_unpublished_release_has_no_evidence_tag_to_record(self):
        r = self.note()
        self.assertEqual(2, r.returncode)
        self.assertIn("not recorded as published", r.stdout)

    def test_an_evidence_tag_is_not_moved_once_recorded(self):
        self.assertEqual(0, self.bind(tag="release-002").returncode)
        self.assertEqual(0, self.record(self.evidence(), tag="release-002").returncode)
        self.assertEqual(0, self.note().returncode)
        again = self.note(tag="publication-003")
        self.assertEqual(2, again.returncode)
        self.assertIn("already records evidence tag publication-002", again.stdout)

    def test_the_evidence_tag_does_not_touch_the_immutable_snapshot(self):
        self.assertEqual(0, self.bind(tag="release-002").returncode)
        self.assertEqual(0, self.record(self.evidence(), tag="release-002").returncode)
        snap = os.path.join(self.dir, "publications", "1", "publication.json")
        with open(snap, "rb") as f:
            before = f.read()
        self.assertEqual(0, self.note().returncode)
        with open(snap, "rb") as f:
            self.assertEqual(before, f.read(),
                             "the published snapshot is never edited after the fact")
        with open(os.path.join(self.dir, "published_indexes.json")) as f:
            entry = json.load(f)["versions"]["1"]
        self.assertEqual("publication-002", entry["publication_evidence_tag"])

    def test_an_unpublished_record_names_no_tag_it_cannot_know(self):
        with open(self.record_path()) as f:
            text = f.read()
        self.assertIn("The frozen-release tag", text)
        self.assertIn("The publication-evidence tag, recorded once it exists", text)


class TestInterruptedPublication(PublicationBase):
    """DM's finding 5: a partial transaction must be recoverable, not a dead end."""

    def interrupt_after_snapshot(self, ev):
        """Record, then roll the ledgers back to emulate a crash after the snapshot."""
        self.assertEqual(0, self.record(ev).returncode)
        for name in ("first_publication.json", "published_indexes.json"):
            with open(os.path.join(self.dir, name), "w") as f:
                json.dump({"note": "emulated crash", "versions": {}}, f)
        with open(self.release_meta_path()) as f:
            meta = json.load(f)
        meta["published"] = False
        meta.pop("published_on", None)
        meta.pop("publication_snapshot", None)
        with open(self.release_meta_path(), "w") as f:
            json.dump(meta, f)

    def test_an_interrupted_recording_refuses_a_plain_retry_and_says_why(self):
        ev = self.evidence()
        self.interrupt_after_snapshot(ev)
        r = self.record(ev)
        self.assertEqual(2, r.returncode)
        self.assertIn("INCOMPLETE recording", r.stdout)
        self.assertIn("--resume", r.stdout)
        self.assertIn("this is not a published sequence", r.stdout)

    def test_an_interrupted_recording_completes_on_resume(self):
        ev = self.evidence()
        self.interrupt_after_snapshot(ev)
        r = self.record(ev, "--resume")
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn("resumed from", r.stdout)
        with open(os.path.join(self.dir, "published_indexes.json")) as f:
            self.assertEqual({"1"}, set(json.load(f)["versions"]))
        with open(os.path.join(self.dir, "first_publication.json")) as f:
            self.assertEqual({"v1", "v1.1", "v2", "v3"}, set(json.load(f)["versions"]))
        # And a completed publication refuses a further resume.
        again = self.record(ev, "--resume")
        self.assertEqual(2, again.returncode)
        self.assertIn("already recorded", again.stdout)

    def test_resume_without_a_partial_recording_is_refused(self):
        r = self.record(self.evidence(), "--resume")
        self.assertEqual(2, r.returncode)
        self.assertIn("no partial recording", r.stdout)

    def test_a_partial_recording_for_another_release_is_not_resumed(self):
        ev = self.evidence()
        self.interrupt_after_snapshot(ev)
        snap = os.path.join(self.dir, "publications", "1", "publication.json")
        with open(snap) as f:
            d = json.load(f)
        d["manifest_sha256"] = "d" * 64
        with open(snap, "w") as f:
            json.dump(d, f)
        r = self.record(ev, "--resume")
        self.assertEqual(2, r.returncode)
        self.assertIn("different release", r.stdout)

    def test_nothing_is_staged_when_validation_fails(self):
        """A refused recording leaves no staging directory behind."""
        with open(os.path.join(self.dir, "publish", "charter", "index.json"), "w") as f:
            f.write("{}")
        self.assertEqual(2, self.record(self.evidence()).returncode)
        pubs = os.path.join(self.dir, "publications")
        leftovers = [d for d in os.listdir(pubs) if d.startswith(".staging")]
        self.assertEqual([], leftovers)


class TestGateAfterPublication(PublicationBase):
    """The gate must pass from a working tree that has already published.

    Runbook step 97 runs `package.py` after step 88 has recorded publication.
    Nothing exercised that order until the live sequence reached it, and the
    gate refused. This test holds the order open: it records a publication in a
    sandbox, then runs the complete gate there, test stage included.

    PVR_NO_RECURSE terminates the nesting. The gate under test runs this file,
    which reaches this class again; the guard skips it at that depth. Every
    other test still runs, so the inner gate is a real gate, and the tests it
    runs spawn `package.py` with PVR_SKIP_TESTS as they always have.
    """

    def test_the_full_gate_passes_after_a_publication_is_recorded(self):
        if os.environ.get("PVR_NO_RECURSE") == "1":
            self.skipTest("inner gate; the outer run is the one under test")

        self.assertEqual(0, self.record(self.evidence()).returncode)

        # The sandbox is now in exactly the state that refused: published,
        # bound, and carrying its snapshot.
        with open(self.release_meta_path()) as f:
            marker = json.load(f)
        self.assertIs(True, marker["published"])
        self.assertIn("release_commit", marker)
        self.assertTrue(os.path.isdir(os.path.join(self.dir, "publications", "1")))

        env = dict(os.environ, PVR_NO_RECURSE="1")
        env.pop("PVR_SKIP_TESTS", None)
        r = subprocess.run([sys.executable, "package.py"], cwd=self.dir,
                           env=env, capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stdout[-4000:] + r.stderr[-2000:])
        self.assertIn("gate tests", r.stdout)
        self.assertNotIn("PACKAGE REFUSED", r.stdout)
        self.assertNotIn("SKIPPED (PVR_SKIP_TESTS=1)", r.stdout)

    def test_a_sandbox_is_unpublished_whatever_the_working_tree_holds(self):
        """The reset is asserted, not assumed. Guards the fixture itself."""
        with open(self.release_meta_path()) as f:
            marker = json.load(f)
        self.assertIs(False, marker["published"])
        self.assertEqual(CANDIDATE_STATE, marker["state"])
        for key in ("published_on", "publication_snapshot"):
            self.assertNotIn(key, marker)
        self.assertEqual(["README.md"],
                         sorted(os.listdir(os.path.join(self.dir, "publications"))))

    # AUTOBIND rebinds in setUp, so the binding keys are expected here; the
    # unbound half of the baseline is what that must not mask.
    def test_the_reset_clears_the_binding_before_setup_rebinds(self):
        fresh = tempfile.mkdtemp(prefix="gate-reset-")
        self.addCleanup(shutil.rmtree, fresh, True)
        for item in ("releases", "publications"):
            src = os.path.join(HERE, item)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(fresh, item))
        make_writable(fresh)
        reset_to_unpublished(fresh)
        with open(os.path.join(fresh, "releases", "publish.json")) as f:
            marker = json.load(f)
        for key in PUBLICATION_MARKER_KEYS:
            self.assertNotIn(key, marker)


if __name__ == "__main__":
    unittest.main(verbosity=2)
