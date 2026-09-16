"""Build-discipline tests for the Charter publication set.

Each test states the defect it would catch. A test that cannot fail against a
known-bad build is not evidence, so every guard here is exercised by breaking the
thing it guards and checking both that the build refuses AND that any previously
built release survived untouched.

Run: python3 test_build.py
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.now(timezone.utc).date().isoformat()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def tree_digests(root):
    out = {}
    for dirpath, _, names in os.walk(root):
        for n in names:
            p = os.path.join(dirpath, n)
            out[os.path.relpath(p, root)] = sha(p)
    return out


class Harness(unittest.TestCase):
    """Each test runs against its own copy of the build directory."""

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="pubset-test-")
        for item in ("build_publication_set.py", "README_source.md", "inputs"):
            src = os.path.join(HERE, item)
            dst = os.path.join(self.dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copyfile(src, dst)
        os.chmod(os.path.join(self.dir, "inputs"), 0o755)
        for f in os.listdir(os.path.join(self.dir, "inputs")):
            os.chmod(os.path.join(self.dir, "inputs", f), 0o644)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def run_build(self, **env):
        e = dict(os.environ)
        e.setdefault("PVR_RELEASE_DATE", TODAY)
        e.update({k: str(v) for k, v in env.items()})
        return subprocess.run([sys.executable, "build_publication_set.py"],
                              cwd=self.dir, env=e, capture_output=True, text=True)

    @property
    def out(self):
        return os.path.join(self.dir, "publish", "charter")

    def meta(self, name="publish"):
        with open(os.path.join(self.dir, "releases", f"{name}.json")) as f:
            return json.load(f)

    def index(self):
        with open(os.path.join(self.out, "index.json")) as f:
            return json.load(f)

    def manifest(self):
        with open(os.path.join(self.out, "manifest.json")) as f:
            return json.load(f)

    def write_ledger(self, name, data):
        with open(os.path.join(self.dir, name), "w") as f:
            json.dump(data, f)


class TestInputValidation(Harness):

    def test_altered_input_refuses_and_preserves_the_release(self):
        """Finding 2 of the v3 review: validate before deleting anything."""
        self.assertEqual(0, self.run_build().returncode)
        before = tree_digests(self.out)

        with open(os.path.join(self.dir, "inputs", "charter-v2.pdf"), "ab") as f:
            f.write(b"XXXXXXXX")

        r = self.run_build(PVR_REPLACE_RELEASE="1")
        self.assertEqual(2, r.returncode)
        self.assertIn("[INPUTS]", r.stdout)
        self.assertIn("charter-v2.pdf", r.stdout)
        self.assertEqual(before, tree_digests(self.out),
                         "a refused build must leave the existing release untouched")

    def test_missing_input_refuses(self):
        os.unlink(os.path.join(self.dir, "inputs", "charter-v1.1.pdf"))
        r = self.run_build()
        self.assertEqual(2, r.returncode)
        self.assertIn("missing input", r.stdout)
        self.assertFalse(os.path.exists(self.out))

    def test_unexpected_input_refuses(self):
        """An extra PDF means the input set is not what the build believes."""
        shutil.copyfile(os.path.join(self.dir, "inputs", "charter-v3.pdf"),
                        os.path.join(self.dir, "inputs", "charter-v4.pdf"))
        r = self.run_build()
        self.assertEqual(2, r.returncode)
        self.assertIn("unexpected input", r.stdout)

    def test_missing_readme_source_refuses(self):
        os.unlink(os.path.join(self.dir, "README_source.md"))
        r = self.run_build()
        self.assertEqual(2, r.returncode)
        self.assertIn("README_source.md", r.stdout)
        self.assertFalse(os.path.exists(self.out))


class TestFreeze(Harness):
    """Finding 1: a release is built once and packaged as built."""

    def test_release_is_frozen_and_not_rebuilt_over(self):
        self.assertEqual(0, self.run_build().returncode)
        before = tree_digests(self.out)
        meta = self.meta()
        self.assertFalse(meta["published"])
        self.assertEqual(sha(os.path.join(self.out, "manifest.json")), meta["manifest_sha256"])

        r = self.run_build()
        self.assertEqual(2, r.returncode)
        self.assertIn("[FROZEN]", r.stdout)
        self.assertEqual(before, tree_digests(self.out))

    def test_replace_is_possible_but_must_be_deliberate(self):
        self.assertEqual(0, self.run_build().returncode)
        r = self.run_build(PVR_REPLACE_RELEASE="1")
        self.assertEqual(0, r.returncode)

    def test_a_published_release_may_not_be_replaced(self):
        self.assertEqual(0, self.run_build().returncode)
        meta = self.meta()
        meta["published"] = True
        with open(os.path.join(self.dir, "releases", "publish.json"), "w") as f:
            json.dump(meta, f)
        r = self.run_build(PVR_REPLACE_RELEASE="1")
        self.assertEqual(2, r.returncode)
        self.assertIn("recorded as published", r.stdout)

    def test_a_separate_release_dir_is_independent(self):
        """This is how reproducibility is tested without touching the release."""
        self.assertEqual(0, self.run_build().returncode)
        before = tree_digests(self.out)
        other = os.path.join(self.dir, "rebuild")
        self.assertEqual(0, self.run_build(PVR_RELEASE_DIR=other).returncode)
        self.assertEqual(before, tree_digests(self.out), "the release must be untouched")
        self.assertTrue(os.path.isfile(os.path.join(self.dir, "releases", "rebuild.json")))


class TestDeployLayout(Harness):

    def test_deploy_root_carries_only_the_record_and_a_pointer(self):
        """Finding 1 of the v3 review: internal files are not deployed."""
        self.assertEqual(0, self.run_build().returncode)
        root = os.path.join(self.dir, "publish")
        self.assertEqual({"index.html", "charter"}, set(os.listdir(root)))
        self.assertEqual(set(tree_digests(self.out)), {
            "index.json", "index.html", "manifest.json", "manifest.json.sha256",
            "README.md",
            "v1/charter-v1.pdf", "v1.1/charter-v1.1.pdf",
            "v2/charter-v2.pdf", "v3/charter-v3.pdf",
        })

    def test_freeze_marker_lives_outside_the_release_directory(self):
        """Anything inside the release directory is served."""
        self.assertEqual(0, self.run_build().returncode)
        root = os.path.join(self.dir, "publish")
        for dirpath, _, names in os.walk(root):
            for n in names:
                self.assertNotIn("release", n.lower(),
                                 f"{n} would be served from the deploy root")

    def test_every_manifest_path_exists_and_matches(self):
        self.assertEqual(0, self.run_build().returncode)
        for o in self.manifest()["objects"]:
            p = os.path.join(self.out, o["path"])
            self.assertTrue(os.path.isfile(p), f"{o['path']} not built")
            self.assertEqual(o["sha256"], sha(p), o["path"])
            self.assertEqual(o["bytes"], os.path.getsize(p), o["path"])

    def test_index_entry_urls_resolve_within_the_record(self):
        self.assertEqual(0, self.run_build().returncode)
        for v in self.index()["versions"]:
            p = os.path.join(self.out, v["entry_url"])
            self.assertTrue(os.path.isfile(p), v["entry_url"])
            self.assertEqual(v["content_digest"], "sha256:" + sha(p))
            self.assertTrue(v["canonical_uri"].endswith("/" + v["entry_url"]))

    def test_manifest_sidecar_matches_manifest(self):
        self.assertEqual(0, self.run_build().returncode)
        with open(os.path.join(self.out, "manifest.json.sha256")) as f:
            recorded = f.read().split()[0]
        self.assertEqual(sha(os.path.join(self.out, "manifest.json")), recorded)


class TestProvenance(Harness):

    def test_manifest_records_builder_inputs_and_parameters(self):
        self.assertEqual(0, self.run_build().returncode)
        man = self.manifest()
        self.assertEqual(sha(os.path.join(self.dir, "build_publication_set.py")),
                         man["builder"]["sha256"])
        self.assertEqual("build_publication_set.py", man["builder"]["source_path"],
                         "the repository must run the builder from its declared path")
        self.assertEqual(4, len(man["inputs"]))
        for i in man["inputs"]:
            self.assertEqual(i["sha256"], sha(os.path.join(self.dir, i["path"])))
        for key in ("python", "platform", "built_at", "PVR_SEQUENCE"):
            self.assertIn(key, man["build_parameters"])
        self.assertIn("do not independently prove", man["provenance_claim"])

    def test_generated_sources_are_recorded(self):
        self.assertEqual(0, self.run_build().returncode)
        gen = {g["path"]: g for g in self.manifest()["generated"]}
        self.assertEqual(gen["README.md"]["source_sha256"],
                         sha(os.path.join(self.dir, "README_source.md")))
        self.assertEqual(gen["README.md"]["source_sha256"], gen["README.md"]["sha256"],
                         "a verbatim copy must have an identical digest")
        self.assertEqual(gen["index.html"]["source_sha256"],
                         sha(os.path.join(self.out, "index.json")))

    def test_independent_rebuild_reproduces_everything_but_the_manifest(self):
        """Reproducibility is checked between two directories, never in place."""
        self.assertEqual(0, self.run_build().returncode)
        first = tree_digests(self.out)
        other = os.path.join(self.dir, "rebuild")
        self.assertEqual(0, self.run_build(PVR_RELEASE_DIR=other).returncode)
        second = tree_digests(os.path.join(other, "charter"))

        expected_change = set(self.manifest()["not_bit_reproducible"]["paths"])
        self.assertEqual(set(first), set(second))
        for path in first:
            if path in expected_change:
                continue
            self.assertEqual(first[path], second[path], f"{path} differs across builds")
        self.assertEqual(4, len([p for p in first if p.endswith(".pdf")]))
        self.assertIn("index.json", set(first) - expected_change,
                      "as_of is a date, so the index must be bit-reproducible")


class TestReleaseDate(Harness):
    """Finding 5: the set carries its date on its face."""

    def test_a_date_that_is_not_the_build_date_is_refused(self):
        r = self.run_build(PVR_RELEASE_DATE="2026-07-29")
        self.assertEqual(2, r.returncode)
        self.assertIn("[RELEASE_DATE]", r.stdout)
        self.assertFalse(os.path.exists(self.out))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "publish", ".staging-charter")))

    def test_the_override_requires_a_recorded_reason(self):
        """The rule is stated with its exception, not contradicted by it."""
        r = self.run_build(PVR_RELEASE_DATE="2026-07-29", PVR_ALLOW_DATE_MISMATCH="1")
        self.assertEqual(2, r.returncode)
        self.assertIn("PVR_DATE_MISMATCH_REASON", r.stdout)
        self.assertFalse(os.path.exists(self.out))

    def test_the_override_reason_is_recorded_where_a_reader_will_see_it(self):
        r = self.run_build(PVR_RELEASE_DATE="2026-07-29", PVR_ALLOW_DATE_MISMATCH="1",
                           PVR_DATE_MISMATCH_REASON="rebuild for comparison only")
        self.assertEqual(0, r.returncode)
        self.assertEqual("rebuild for comparison only",
                         self.manifest()["build_parameters"]["date_mismatch_reason"])
        self.assertEqual("rebuild for comparison only", self.meta()["date_mismatch_reason"])


class TestPublicationSeparation(Harness):
    """Finding 5: the builder does not record publication."""

    def test_the_builder_writes_no_publication_ledger(self):
        self.assertEqual(0, self.run_build().returncode)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "first_publication.json")))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "published_indexes.json")))
        self.assertFalse(self.meta()["published"])

    def test_the_served_record_does_not_narrate_its_own_deployment(self):
        self.assertEqual(0, self.run_build().returncode)
        self.assertNotIn("publication_state", self.index())
        self.assertNotIn("publication_state", self.manifest())
        with open(os.path.join(self.out, "index.html")) as f:
            page = f.read()
        for word in ("candidate", "published set", "pending"):
            self.assertNotIn(word, page.lower(),
                             f"the served page should not claim a deployment status ({word})")

    def test_an_already_published_version_keeps_its_recorded_date(self):
        self.write_ledger("first_publication.json", {"versions": {
            "v1": {"first_published": "2026-08-01", "sequence": 1}}})
        self.assertEqual(0, self.run_build(PVR_SEQUENCE="2").returncode)
        dates = {v["version"]: v["published_to_record"] for v in self.index()["versions"]}
        self.assertEqual("2026-08-01", dates["v1"])
        self.assertEqual(TODAY, dates["v3"])
        self.assertEqual(["v1.1", "v2", "v3"],
                         self.meta()["versions_awaiting_first_publication"])

    def test_an_unreadable_ledger_is_not_treated_as_empty(self):
        with open(os.path.join(self.dir, "first_publication.json"), "w") as f:
            f.write("{not json")
        r = self.run_build()
        self.assertEqual(2, r.returncode)
        self.assertIn("[LEDGER]", r.stdout)


class TestSequence(Harness):

    def test_a_published_sequence_may_not_be_rebuilt(self):
        self.write_ledger("published_indexes.json", {"versions": {
            "1": {"index_sha256": "a" * 64, "recorded_at": "2026-09-16T00:00:00+00:00"}}})
        r = self.run_build(PVR_SEQUENCE="1")
        self.assertEqual(2, r.returncode)
        self.assertIn("[SEQUENCE]", r.stdout)
        self.assertIn("immutable", r.stdout)

    def test_sequence_may_not_regress(self):
        self.write_ledger("published_indexes.json", {"versions": {
            "2": {"index_sha256": "a" * 64, "recorded_at": "2026-09-16T00:00:00+00:00"}}})
        r = self.run_build(PVR_SEQUENCE="1")
        self.assertEqual(2, r.returncode)
        self.assertIn("behind the record", r.stdout)


class TestRecordContent(Harness):

    def test_superseded_from_is_qualified_as_documentary_chronology(self):
        self.assertEqual(0, self.run_build().returncode)
        idx = self.index()
        self.assertIn("not an assertion that supersession took legal effect",
                      idx["definitions"]["superseded_from"])
        for v in idx["versions"]:
            if "superseded_from" in v:
                self.assertIn("documentary chronology", v["superseded_from_basis"])

    def test_published_to_record_points_at_its_evidence(self):
        self.assertEqual(0, self.run_build().returncode)
        d = self.index()["definitions"]["published_to_record"]
        self.assertIn("publication log", d)
        self.assertIn("This field is not itself that evidence", d)

    def test_no_version_outside_the_lineage_appears_anywhere(self):
        self.assertEqual(0, self.run_build().returncode)
        for dirpath, _, names in os.walk(self.out):
            for n in names:
                if n.endswith(".pdf"):
                    continue
                with open(os.path.join(dirpath, n), "rb") as f:
                    body = f.read().decode("utf-8", "replace")
                for bad in ("/v4/", "charter-v4", "v1.2", "v2.1"):
                    self.assertNotIn(bad, body, f"{n} names {bad}")

    def test_publication_does_not_assert_historical_effectiveness(self):
        self.assertEqual(0, self.run_build().returncode)
        self.assertIn("does not validate, cure or establish", self.index()["not_asserted"])
        with open(os.path.join(self.out, "index.html")) as f:
            self.assertIn("does not validate, cure or establish", f.read())

    def test_exactly_one_version_is_current(self):
        self.assertEqual(0, self.run_build().returncode)
        current = [v for v in self.index()["versions"] if v["is_current"]]
        self.assertEqual(1, len(current))
        self.assertEqual("v3", current[0]["version"])
        for v in self.index()["versions"]:
            self.assertEqual(v["status"], "current" if v["is_current"] else "superseded")


if __name__ == "__main__":
    unittest.main(verbosity=2)
