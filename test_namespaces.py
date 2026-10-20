"""Prove the multi-namespace pipeline carries the Charter unchanged and refuses otherwise.

The governance decision of 28 September 2026: the pipeline may carry a second
record, the disclosure record at /disclosures/, only if /charter/ in every new
release is byte for byte the published Charter, no release omits it, the
disclosure record is a record of its own and not a disguised Charter copy, and
nothing already published moves or changes.

Every guarantee below is exercised by breaking the thing it guards. The gate
numbering (G2 to G7) is the one the change was specified against.

INPUTS. No real disclosure or GET schema is an input here. Each sandbox copies
the synthetic TEST INPUT fixtures from `test_fixtures/disclosures/` and
`test_fixtures/get/` and registers their digests in the SANDBOX's own copy of
`records.py`, in the same single blocks an operator completes at freeze. The
repository's `records.py` is never edited by a test.

The GET namespace and carrying a built record forward (19 October 2026) are
tested in the classes after G7: TestGetNamespace, TestGetLive,
TestCarriedForward. Those classes register a synthetic GET issue explicitly.
Every other sandbox keeps GET_REGISTRATION = ABSENT, as records.py ships it, and
the GET-absent release is tested across build, gate, live verifier and recorder
in TestGetAbsent, TestGetAbsentLive and TestGetAbsentRecording.
TestGetAbsentRegression builds the same disclosure-only release with the
builder and registry at b4e36d3 and with the current code, and compares them
byte for byte.

Run: python3 test_namespaces.py
"""

import hashlib
import http.server
import json
import os
import re
import shutil
import socket
import socketserver
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import records  # noqa: E402

TODAY = datetime.now(timezone.utc).date().isoformat()
FIXTURES = os.path.join(HERE, "test_fixtures", "disclosures")
GET_FIXTURES = os.path.join(HERE, "test_fixtures", "get")
GET_V1 = "1.0.1-test-draft-v1"
GET_V2 = "1.0.2-test-draft-v2"
GET_SCHEMA = "application/schema+json"
PUBLISHED = records.CHARTER["published_manifest_sha256"]

# A release name used only inside test sandboxes.
RELEASE = "release-under-test"

# What a sandbox needs. The Charter's ledgers ARE copied, unlike in
# test_package.py: carrying the Charter depends on its publication being
# recorded, and these tests must prove that state is never written. Only the
# carried-from release's freeze marker is copied from `releases/`, and the
# disclosure ledgers are not copied, so every sandbox starts with no disclosure
# published.
SANDBOX = ("publish", "verification", "inputs", "vendor", "publications", "test_fixtures",
           "build_publication_set.py", "build_release.py", "records.py",
           "record_publication.py", "package.py", "expectations.py", "verify_live.py",
           "test_build.py", "test_verify_live.py", "test_package.py", "test_namespaces.py",
           "README_source.md", "DEPLOY.md", "PUBLICATION_LOG.md",
           "first_publication.json", "published_indexes.json")


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def tree(root):
    out = {}
    for dirpath, _, names in os.walk(root):
        for n in names:
            p = os.path.join(dirpath, n)
            out[os.path.relpath(p, root)] = sha(p)
    return out


def make_writable(root):
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            q = os.path.join(dirpath, name)
            try:
                os.chmod(q, os.stat(q).st_mode | stat.S_IWUSR)
            except OSError:
                pass


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def registration_block(entries, slug="test-disclosure",
                       title="TEST INPUT synthetic disclosure record"):
    lines = ["# BEGIN DISCLOSURE REGISTRATION",
             "DISCLOSURE_REGISTRATION = {",
             f"    \"record_slug\": {slug!r},",
             f"    \"title\": {title!r},",
             "    \"entries\": ["]
    for e in entries:
        lines.append(f"        {e!r},")
    lines += ["    ],", "}", "# END DISCLOSURE REGISTRATION"]
    return "\n".join(lines)


def get_registration_block(entries):
    lines = ["# BEGIN GET REGISTRATION", "GET_REGISTRATION = {", "    \"entries\": ["]
    lines += [f"        {e!r}," for e in entries]
    lines += ["    ],", "}", "# END GET REGISTRATION"]
    return "\n".join(lines)


# The shipped GET block: the release has no GET namespace.
GET_ABSENT_BLOCK = "# BEGIN GET REGISTRATION\nGET_REGISTRATION = ABSENT\n# END GET REGISTRATION"

# The round-1 placeholder. No longer shipped; refused, never read as absent.
GET_PLACEHOLDER_BLOCK = get_registration_block(
    [{"version": records.UNREGISTERED, "src": records.UNREGISTERED,
      "sha256": records.UNREGISTERED, "bytes": None, "document_date": records.UNREGISTERED,
      "media_type": GET_SCHEMA, "status": records.UNREGISTERED,
      "reason": records.UNREGISTERED}])


# The shipped placeholder, as records.py carries it until freeze.
PLACEHOLDER_BLOCK = registration_block(
    [{"version": "v1", "src": records.UNREGISTERED, "sha256": records.UNREGISTERED,
      "bytes": None, "document_date": records.UNREGISTERED, "reason": None}],
    slug=records.UNREGISTERED, title=records.UNREGISTERED)


class Sandbox(unittest.TestCase):
    """A private copy of the repository, with the TEST INPUT registered in it."""

    VERSIONS = ("v1",)
    REGISTER = True
    # The GET record is optional and absent by default, as records.py ships it.
    # A class testing the GET record registers it explicitly.
    GET_VERSIONS = ()

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ns-test-")
        for item in SANDBOX:
            src = os.path.join(HERE, item)
            if not os.path.exists(src):
                continue
            dst = os.path.join(self.dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copyfile(src, dst)
        carried = records.CHARTER["carried_from_release"]
        os.makedirs(os.path.join(self.dir, "releases"))
        shutil.copyfile(os.path.join(HERE, "releases", f"{carried}.json"),
                        os.path.join(self.dir, "releases", f"{carried}.json"))
        make_writable(self.dir)
        self.live = os.path.join(self.dir, "live-evidence")
        # The sandbox owns its disclosure inputs and its registration, whatever
        # the repository holds. Once the real carrier is registered at freeze,
        # it must not leak into a test, and these tests must still pass.
        shutil.rmtree(os.path.join(self.dir, "inputs", "disclosures"), ignore_errors=True)
        shutil.rmtree(os.path.join(self.dir, "inputs", "get"), ignore_errors=True)
        self.write_registration(PLACEHOLDER_BLOCK)
        self.write_block("GET REGISTRATION", GET_ABSENT_BLOCK)
        self.write_carry({})
        if self.REGISTER:
            self.register(self.VERSIONS)
        # The GET record is registered only where a class asks for it. Without
        # that, the sandbox keeps GET_REGISTRATION = ABSENT, as shipped.
        if self.GET_VERSIONS:
            self.register_get(self.GET_VERSIONS)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    # --- registration, exactly as an operator does it at freeze, but in the sandbox

    def register(self, versions, **overrides):
        inputs = os.path.join(self.dir, "inputs", "disclosures")
        os.makedirs(inputs, exist_ok=True)
        entries = []
        for i, v in enumerate(versions):
            name = f"TEST-INPUT-disclosure-{v}.md"
            shutil.copyfile(os.path.join(FIXTURES, name), os.path.join(inputs, name))
            with open(os.path.join(inputs, name), "rb") as f:
                body = f.read()
            e = {"version": v, "src": name, "sha256": sha_bytes(body), "bytes": len(body),
                 "document_date": "2026-09-2" + str(i + 1),
                 "reason": None if i == 0 else "Synthetic revision for the lineage test."}
            e.update(overrides)
            entries.append(e)
        self.write_registration(registration_block(entries))

    def write_registration(self, block):
        self.write_block("DISCLOSURE REGISTRATION", block)

    def write_block(self, marker, block):
        path = os.path.join(self.dir, "records.py")
        with open(path) as f:
            text = f.read()
        new = re.sub(rf"# BEGIN {marker}.*?# END {marker}", lambda m: block, text, flags=re.S)
        self.assertNotEqual(text, new, f"the {marker} block was not found")
        with open(path, "w") as f:
            f.write(new)

    def register_get(self, versions, **overrides):
        """Register synthetic GET issues: issue N of the fixtures under each version slug."""
        inputs = os.path.join(self.dir, "inputs", "get")
        os.makedirs(inputs, exist_ok=True)
        entries = []
        for i, v in enumerate(versions):
            name = f"TEST-INPUT-get-schema-issue{i + 1}.json"
            shutil.copyfile(os.path.join(GET_FIXTURES, name), os.path.join(inputs, name))
            with open(os.path.join(inputs, name), "rb") as f:
                body = f.read()
            e = {"version": v, "src": name, "sha256": sha_bytes(body), "bytes": len(body),
                 "document_date": "2026-10-1" + str(i + 1), "media_type": GET_SCHEMA,
                 "status": "public draft for comment",
                 "reason": "Synthetic GET issue for the namespace tests."}
            e.update(overrides)
            entries.append(e)
        self.write_block("GET REGISTRATION", get_registration_block(entries))

    def write_carry(self, carry):
        self.write_block("CARRY REGISTRATION", "# BEGIN CARRY REGISTRATION\n"
                         f"CARRY_REGISTRATION = {carry!r}\n# END CARRY REGISTRATION")

    def edit_registry(self, old, new):
        path = os.path.join(self.dir, "records.py")
        with open(path) as f:
            text = f.read()
        self.assertIn(old, text)
        with open(path, "w") as f:
            f.write(text.replace(old, new, 1))

    # --- the scripts, run in the sandbox

    def run_script(self, script, *args, **env):
        e = dict(os.environ)
        for k in ("PVR_RELEASE", "PVR_RELEASE_DIR", "PVR_ALLOW_TEST_INPUT",
                  "PVR_CHARTER_CHANGE", "PVR_REPLACE_RELEASE", "PVR_SEQUENCE"):
            e.pop(k, None)
        e.setdefault("PVR_RELEASE_DATE", TODAY)
        e.update({k: str(v) for k, v in env.items()})
        return subprocess.run([sys.executable, script, *args], cwd=self.dir, env=e,
                              capture_output=True, text=True)

    def build(self, name=RELEASE, **env):
        env.setdefault("PVR_ALLOW_TEST_INPUT", "1")
        return self.run_script("build_release.py",
                               PVR_RELEASE_DIR=os.path.join(self.dir, name), **env)

    def built(self, name=RELEASE, **env):
        r = self.build(name, **env)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        return r

    def gate(self, *args, name=RELEASE):
        return self.run_script("package.py", *args, PVR_RELEASE=name, PVR_SKIP_TESTS="1")

    def rel(self, *parts, name=RELEASE):
        return os.path.join(self.dir, name, *parts)

    def meta(self, name=RELEASE):
        with open(os.path.join(self.dir, "releases", f"{name}.json")) as f:
            return json.load(f)

    def write_meta(self, meta, name=RELEASE):
        with open(os.path.join(self.dir, "releases", f"{name}.json"), "w") as f:
            json.dump(meta, f, indent=2)

    def load(self, *parts):
        with open(os.path.join(self.dir, *parts)) as f:
            return json.load(f)

    def charter_state(self):
        """Every Charter ledger and snapshot byte, to prove none is ever written."""
        out = {}
        for rel in ("first_publication.json", "published_indexes.json"):
            out[rel] = sha(os.path.join(self.dir, rel))
        for p, d in tree(os.path.join(self.dir, "publications")).items():
            out["publications/" + p] = d
        out["publish"] = json.dumps(tree(os.path.join(self.dir, "publish")), sort_keys=True)
        out["releases/publish.json"] = sha(os.path.join(self.dir, "releases", "publish.json"))
        return out

    def alter_consistently(self, record_dir, meta_name=None):
        """Change the Charter's index and make manifest, sidecar and marker agree.

        This is the alteration a careless rebuild produces: internally
        consistent, and not the published Charter.
        """
        index = os.path.join(record_dir, "index.json")
        with open(index) as f:
            doc = json.load(f)
        doc["as_of"] = "2026-09-28"
        with open(index, "w") as f:
            json.dump(doc, f, indent=2)
        man_path = os.path.join(record_dir, "manifest.json")
        with open(man_path) as f:
            man = json.load(f)
        for o in man["objects"]:
            if o["path"] == "index.json":
                o["sha256"] = sha(index)
                o["bytes"] = os.path.getsize(index)
        with open(man_path, "w") as f:
            json.dump(man, f, indent=2)
        with open(os.path.join(record_dir, "manifest.json.sha256"), "w") as f:
            f.write(sha(man_path) + "  manifest.json\n")
        if meta_name:
            m = self.meta(meta_name)
            if m.get("schema") == "arkaya-release/2":
                m["namespaces"]["charter"]["manifest_sha256"] = sha(man_path)
                m["namespaces"]["charter"]["index_sha256"] = sha(index)
            else:
                m["manifest_sha256"] = sha(man_path)
                m["index_sha256"] = sha(index)
            self.write_meta(m, meta_name)
        return sha(man_path)


# ======================================================================== G2

class TestCoexistence(Sandbox):
    """G2: a release carrying both namespaces builds, packages and verifies."""

    def test_a_release_carrying_both_namespaces_builds(self):
        self.built()
        self.assertEqual({"index.html", "charter", "disclosures"}, set(os.listdir(self.rel())))
        # The Charter is the published Charter, byte for byte.
        self.assertEqual(tree(os.path.join(self.dir, "publish", "charter")),
                         tree(self.rel("charter")))
        self.assertEqual(PUBLISHED, sha(self.rel("charter", "manifest.json")))
        # The disclosure record is a record of its own.
        self.assertEqual({"index.json", "index.html", "manifest.json", "manifest.json.sha256",
                          "test-disclosure/v1/test-disclosure-v1.md"},
                         set(tree(self.rel("disclosures"))))
        meta = self.meta()
        self.assertEqual("arkaya-release/2", meta["schema"])
        self.assertFalse(meta["published"])
        self.assertTrue(meta["test_input"], "a fixture-built release must say so")
        c, d = meta["namespaces"]["charter"], meta["namespaces"]["disclosures"]
        self.assertEqual(("carried", 1, PUBLISHED, []),
                         (c["mode"], c["sequence"], c["manifest_sha256"],
                          c["versions_awaiting_first_publication"]))
        self.assertEqual(("built", 1, ["v1"]),
                         (d["mode"], d["sequence"], d["versions_awaiting_first_publication"]))
        self.assertEqual(sha(self.rel("disclosures", "manifest.json")), d["manifest_sha256"])
        self.assertNotEqual(c["manifest_sha256"], d["manifest_sha256"])
        with open(self.rel("disclosures", "manifest.json.sha256")) as f:
            self.assertEqual(d["manifest_sha256"], f.read().split()[0])

    def test_the_disclosure_entry_is_served_as_markdown_at_its_canonical_path(self):
        self.built()
        man = self.load(RELEASE, "disclosures", "manifest.json")
        entry = [o for o in man["objects"] if o.get("version") == "v1"][0]
        self.assertEqual("test-disclosure/v1/test-disclosure-v1.md", entry["path"])
        self.assertEqual("text/markdown", entry["mime_type"])
        self.assertEqual("https://record.arkayarisk.com/disclosures/"
                         "test-disclosure/v1/test-disclosure-v1.md", entry["canonical_uri"])
        with open(os.path.join(FIXTURES, "TEST-INPUT-disclosure-v1.md"), "rb") as f:
            self.assertEqual(sha_bytes(f.read()), entry["sha256"],
                             "the disclosure is copied, never regenerated")

    def test_the_root_pointer_links_both_records_and_is_part_of_neither(self):
        self.built()
        with open(self.rel("index.html")) as f:
            page = f.read()
        self.assertIn('href="/charter/"', page)
        self.assertIn('href="/disclosures/"', page)
        for ns in ("charter", "disclosures"):
            man = self.load(RELEASE, ns, "manifest.json")
            self.assertNotIn("../index.html", [o["path"] for o in man["objects"]])
        self.assertEqual(sha(self.rel("index.html")), self.meta()["root_pointer_sha256"])

    def test_the_coexisting_release_packages(self):
        self.built()
        r = self.gate()
        self.assertEqual(0, r.returncode, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("charter        carried", r.stdout)
        self.assertIn("record         generated", r.stdout)
        check = self.gate("--check")
        self.assertEqual(0, check.returncode, check.stdout[-3000:])
        self.assertIn("matches its deterministic regeneration", check.stdout)
        record = os.path.join(self.dir, "verification", f"RELEASE_RECORD_{RELEASE}.md")
        with open(record) as f:
            text = f.read()
        self.assertIn(PUBLISHED, text)
        self.assertIn("TEST INPUT RELEASE", text)
        # The Charter's own production record is not touched by a multi release.
        self.assertEqual(sha(os.path.join(HERE, "verification", "PRODUCTION_RECORD.md")),
                         sha(os.path.join(self.dir, "verification", "PRODUCTION_RECORD.md")))

    def test_a_hand_edited_release_record_is_refused(self):
        self.built()
        self.assertEqual(0, self.gate().returncode)
        record = os.path.join(self.dir, "verification", f"RELEASE_RECORD_{RELEASE}.md")
        with open(record, "a") as f:
            f.write("\n**Independently audited.**\n")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("not its deterministic regeneration", r.stdout)

    def test_the_disclosure_rebuild_reproduces_everything_but_the_manifest(self):
        self.built()
        self.built("second-release")
        first, second = tree(self.rel("disclosures")), tree(self.rel("disclosures",
                                                                     name="second-release"))
        self.assertEqual(set(first), set(second))
        man = self.load(RELEASE, "disclosures", "manifest.json")
        for p in set(first) - set(man["not_bit_reproducible"]["paths"]):
            self.assertEqual(first[p], second[p], f"{p} differs across builds")
        self.assertEqual(tree(self.rel("charter")), tree(self.rel("charter",
                                                                  name="second-release")))


class TestLineage(Sandbox):

    VERSIONS = ("v1", "v2")

    def test_a_two_entry_lineage_has_one_current_entry(self):
        self.built()
        idx = self.load(RELEASE, "disclosures", "index.json")
        self.assertEqual(["v1", "v2"], [e["version"] for e in idx["entries"]])
        self.assertEqual("v2", [e for e in idx["entries"] if e["is_current"]][0]["version"])
        self.assertEqual("v2", idx["entries"][0]["superseded_by"])
        self.assertEqual("v1", idx["entries"][1]["predecessor"])


# ======================================================================== G3

class TestCharterRemovalRefused(Sandbox):
    """G3: no release may omit the Charter, at build or at package."""

    def assert_nothing_built(self):
        self.assertFalse(os.path.exists(self.rel()))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "releases", f"{RELEASE}.json")))
        self.assertFalse(os.path.exists(os.path.join(self.dir, f".staging-{RELEASE}")))

    def test_a_build_without_the_carried_charter_source_is_refused(self):
        shutil.rmtree(os.path.join(self.dir, "publish", "charter"))
        r = self.build()
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_CARRY]", r.stdout)
        self.assertIn("No release may be built without the Charter", r.stdout)
        self.assert_nothing_built()

    def test_a_disclosure_only_registry_is_refused_at_build(self):
        self.edit_registry("ALL_NAMESPACES = (CHARTER, DISCLOSURES, GET)",
                           "ALL_NAMESPACES = (DISCLOSURES, GET)")
        r = self.build()
        self.assertEqual(2, r.returncode)
        self.assertIn("[REGISTRY]", r.stdout)
        self.assertIn("No release may be built without the carried Charter", r.stdout)
        self.assert_nothing_built()

    def test_a_charter_registered_as_built_is_refused_as_a_charter_change(self):
        self.edit_registry('"path": "charter",\n    "mode": "carried",',
                           '"path": "charter",\n    "mode": "built",')
        r = self.build()
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_CHANGE]", r.stdout)
        self.assert_nothing_built()

    def test_a_requested_charter_change_is_refused_by_name(self):
        r = self.build(PVR_CHARTER_CHANGE="1")
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_CHANGE]", r.stdout)
        self.assertIn("No authorised Charter change path exists", r.stdout)
        self.assert_nothing_built()

    def test_an_unpublished_carried_source_is_refused(self):
        m = self.load("releases", "publish.json")
        m["published"] = False
        with open(os.path.join(self.dir, "releases", "publish.json"), "w") as f:
            json.dump(m, f)
        r = self.build()
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_CARRY]", r.stdout)
        self.assert_nothing_built()

    def test_a_release_whose_charter_was_removed_is_refused_at_package(self):
        self.built()
        shutil.rmtree(self.rel("charter"))
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("PACKAGE REFUSED", r.stdout)
        self.assertIn("[CHARTER_IDENTITY] the release has no charter/ directory", r.stdout)
        self.assertIn("[LAYOUT]", r.stdout)

    def test_a_disclosure_only_release_is_refused_at_package(self):
        """Charter directory gone AND the marker rewritten to match: still refused."""
        self.built()
        shutil.rmtree(self.rel("charter"))
        meta = self.meta()
        del meta["namespaces"]["charter"]
        self.write_meta(meta)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_CARRY] the release does not carry the charter namespace", r.stdout)
        self.assertIn("[NAMESPACES]", r.stdout)


# ======================================================================== G4

class TestCharterAlterationRefused(Sandbox):
    """G4: any byte of difference from the published Charter is refused."""

    def test_one_appended_byte_in_the_carried_source_is_refused_at_build(self):
        with open(os.path.join(self.dir, "publish", "charter", "v2", "charter-v2.pdf"), "ab") as f:
            f.write(b"X")
        r = self.build()
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_IDENTITY]", r.stdout)
        self.assertIn("v2/charter-v2.pdf", r.stdout)
        self.assertFalse(os.path.exists(self.rel()))

    def test_a_consistently_altered_carried_source_is_refused_at_build(self):
        """Index, manifest, sidecar and freeze marker all agree; it is still not published."""
        self.alter_consistently(os.path.join(self.dir, "publish", "charter"), "publish")
        r = self.build()
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_IDENTITY]", r.stdout)
        self.assertFalse(os.path.exists(self.rel()))

    def test_an_extra_file_in_the_carried_source_is_refused_at_build(self):
        with open(os.path.join(self.dir, "publish", "charter", "disclosure.md"), "w") as f:
            f.write("smuggled in")
        r = self.build()
        self.assertEqual(2, r.returncode)
        self.assertIn("present but not in the published manifest", r.stdout)

    def test_a_charter_byte_changed_after_building_is_refused_at_package(self):
        self.built()
        with open(self.rel("charter", "README.md"), "ab") as f:
            f.write(b"\n")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_IDENTITY] charter/README.md", r.stdout)

    def test_a_consistently_altered_charter_is_refused_at_package(self):
        self.built()
        self.alter_consistently(self.rel("charter"), RELEASE)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_IDENTITY] charter/manifest.json hashes to", r.stdout)

    def test_a_charter_only_rebuild_by_the_legacy_builder_is_refused_at_package(self):
        """The Charter's own builder can still rebuild; nothing will package the result.

        `build_publication_set.py` is left byte-identical because the published
        manifest names it. A rebuild at a new sequence is internally consistent
        and passes every freeze check, so the gate needs the published digest.
        """
        rebuild = os.path.join(self.dir, "charter-rebuild")
        r = self.run_script("build_publication_set.py", PVR_RELEASE_DIR=rebuild,
                            PVR_SEQUENCE="2")
        self.assertEqual(0, r.returncode, r.stdout)
        g = self.run_script("package.py", "--check", PVR_RELEASE="charter-rebuild",
                            PVR_SKIP_TESTS="1")
        self.assertEqual(2, g.returncode)
        self.assertIn("[CHARTER_IDENTITY]", g.stdout)

    def test_the_published_release_still_packages(self):
        """The identity check is satisfied by the published release itself."""
        g = self.run_script("package.py", "--check", PVR_RELEASE="publish", PVR_SKIP_TESTS="1")
        self.assertEqual(0, g.returncode, g.stdout[-3000:])


# ======================================================================== G5

class Venue:
    """Serves a private copy of a release's deploy root, which a test may damage."""

    def __init__(self, source, substitute=None):
        self.dir = tempfile.mkdtemp(prefix="ns-venue-")
        self.root = os.path.join(self.dir, "root")
        shutil.copytree(source, self.root)
        make_writable(self.dir)
        self.substitute = substitute or {}
        self.port = free_port()
        venue = self

        class H(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **kw):
                super().__init__(*a, directory=venue.root, **kw)

            def log_message(self, *a):
                pass

            def do_GET(self):
                if self.path in venue.substitute:
                    body = venue.substitute[self.path]
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                super().do_GET()

        socketserver.TCPServer.allow_reuse_address = True
        self.srv = socketserver.TCPServer(("127.0.0.1", self.port), H)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def path(self, *parts):
        return os.path.join(self.root, *parts)

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()
        shutil.rmtree(self.dir, ignore_errors=True)


class VenueCase(Sandbox):

    def setUp(self):
        super().setUp()
        self.built()
        self.venue = Venue(self.rel())

    def tearDown(self):
        self.venue.close()
        super().tearDown()

    def verify(self, base=None, release=RELEASE):
        r = self.run_script("verify_live.py", f"--release={release}",
                            base or f"http://127.0.0.1:{self.venue.port}/",
                            PVR_ALLOW_PLAIN_HTTP="1", PVR_LIVE_OUT_DIR=self.live)
        evidence = None
        if os.path.isdir(self.live) and os.listdir(self.live):
            newest = max((os.path.join(self.live, f) for f in os.listdir(self.live)),
                         key=os.path.getmtime)
            with open(newest) as f:
                evidence = json.load(f)
        return r, evidence


class TestLiveVerificationOfBoth(VenueCase):
    """G5: each namespace verified against its own manifest; the Charter against publication."""

    def test_a_venue_serving_both_records_passes(self):
        r, ev = self.verify()
        self.assertEqual(0, r.returncode, r.stdout[-3000:])
        self.assertTrue(ev["namespaces"]["charter"]["passed"])
        self.assertTrue(ev["namespaces"]["disclosures"]["passed"])
        self.assertTrue(ev["charter_identity"]["passed"])
        self.assertEqual(PUBLISHED, ev["charter_identity"]["served_manifest_sha256"])
        self.assertNotEqual(ev["namespaces"]["charter"]["manifest_sha256"],
                            ev["namespaces"]["disclosures"]["manifest_sha256"])
        # A rehearsal of a test-input release is never approved, and says why.
        self.assertFalse(ev["production_approval"])
        self.assertIn("rehearsal over plain HTTP", ev["approval_blockers"])
        self.assertTrue(any("TEST INPUT" in b for b in ev["approval_blockers"]))
        self.assertFalse(any("Charter is absent or altered" in b for b in ev["approval_blockers"]))
        # Every check the Charter has, the disclosure record has too.
        names = {c["check"] for c in ev["checks"]}
        for check in ("landing page body matches index.html",
                      "served manifest matches the frozen manifest",
                      "served sidecar matches the served manifest",
                      "served sidecar matches the frozen manifest",
                      "control path 404s", "index reachable"):
            self.assertIn(f"[charter] {check}", names)
            self.assertIn(f"[disclosures] {check}", names)
        self.assertIn("[disclosures] content-type test-disclosure/v1/test-disclosure-v1.md", names)

    def test_charter_removed_from_the_venue_fails_and_withholds_approval(self):
        shutil.rmtree(self.venue.path("charter"))
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  [charter] served manifest matches the frozen manifest", r.stdout)
        self.assertIn("FAIL  charter identity: served Charter manifest is the published manifest",
                      r.stdout)
        self.assertFalse(ev["production_approval"])
        self.assertTrue(any("Charter is absent or altered" in b for b in ev["approval_blockers"]))
        self.assertTrue(any("namespace charter failed" in b for b in ev["approval_blockers"]))

    def test_an_altered_charter_object_on_the_venue_fails_and_withholds_approval(self):
        with open(self.venue.path("charter", "v3", "charter-v3.pdf"), "ab") as f:
            f.write(b"TAMPER")
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  [charter] digest v3/charter-v3.pdf", r.stdout)
        self.assertIn("FAIL  charter identity: every served Charter object is the published "
                      "object", r.stdout)
        self.assertTrue(any("Charter is absent or altered" in b for b in ev["approval_blockers"]))

    def test_a_substituted_charter_manifest_with_a_consistent_sidecar_fails(self):
        with open(self.venue.path("charter", "manifest.json")) as f:
            man = json.load(f)
        man["provenance_claim"] = "substituted"
        body = json.dumps(man, indent=2).encode()
        with open(self.venue.path("charter", "manifest.json"), "wb") as f:
            f.write(body)
        with open(self.venue.path("charter", "manifest.json.sha256"), "w") as f:
            f.write(sha_bytes(body) + "  manifest.json\n")
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  charter identity: served Charter manifest is the published manifest",
                      r.stdout)
        self.assertFalse(ev["charter_identity"]["passed"])
        self.assertFalse(ev["production_approval"])

    def test_a_consistently_altered_local_charter_fails_identity(self):
        """The venue and the local release agree with each other, and not with publication."""
        self.alter_consistently(self.rel("charter"), RELEASE)
        self.alter_consistently(self.venue.path("charter"))
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("PASS  [charter] served manifest matches the frozen manifest", r.stdout)
        self.assertIn("FAIL  charter identity: local Charter manifest is the published manifest",
                      r.stdout)
        self.assertTrue(any("Charter is absent or altered" in b for b in ev["approval_blockers"]))

    def test_a_wrong_disclosure_object_fails_and_withholds_approval(self):
        target = self.venue.path("disclosures", "test-disclosure", "v1", "test-disclosure-v1.md")
        with open(target, "ab") as f:
            f.write(b"\nappended on the venue\n")
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  [disclosures] digest test-disclosure/v1/test-disclosure-v1.md",
                      r.stdout)
        self.assertFalse(ev["namespaces"]["disclosures"]["passed"])
        self.assertTrue(ev["charter_identity"]["passed"], "the Charter itself is unaffected")
        self.assertTrue(any("namespace disclosures failed" in b for b in ev["approval_blockers"]))

    def test_a_wrong_disclosure_landing_page_fails(self):
        self.venue.substitute["/disclosures/"] = b"<html>not the disclosure record</html>"
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  [disclosures] landing page body matches index.html", r.stdout)
        self.assertFalse(ev["production_approval"])

    def test_the_disclosure_record_missing_from_the_venue_fails(self):
        shutil.rmtree(self.venue.path("disclosures"))
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  [disclosures] served manifest matches the frozen manifest", r.stdout)
        self.assertTrue(any("namespace disclosures failed" in b for b in ev["approval_blockers"]))

    def test_a_pointer_not_linking_both_records_fails(self):
        self.venue.substitute["/"] = b'<html><a href="/charter/">Charter</a></html>'
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  deploy root serves the pointer page linking every record", r.stdout)
        self.assertIn("no link to /disclosures/", r.stdout)

    def test_the_disclosure_ledger_must_not_be_served(self):
        os.makedirs(self.venue.path("ledgers", "disclosures"))
        with open(self.venue.path("ledgers", "disclosures", "first_publication.json"), "w") as f:
            f.write("{}")
        r, _ = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  internal file not served: ledgers/disclosures/first_publication.json",
                      r.stdout)

    def test_a_multi_record_release_is_not_verified_from_charter(self):
        r, _ = self.verify(base=f"http://127.0.0.1:{self.venue.port}/charter/")
        self.assertEqual(2, r.returncode)
        self.assertIn("verified from the deploy root", r.stdout)


# ======================================================================== G6

class PublicationCase(Sandbox):

    COMMIT = "a" * 40

    def setUp(self):
        super().setUp()
        self.built()
        r = self.bind()
        self.assertEqual(0, r.returncode, r.stdout)

    def bind(self, name=RELEASE):
        return self.run_script("record_publication.py", "--bind", "--release", name,
                               "--commit", self.COMMIT, "--tag", "release-002")

    def evidence(self, name=RELEASE, **overrides):
        meta = self.meta(name)
        ev = {
            "verified_at": meta["release_date"] + "T10:00:00+00:00",
            "base": records.CANONICAL_ROOT,
            "canonical_uri": records.CANONICAL_ROOT,
            "rehearsal": False,
            "release": name,
            "release_schema": "arkaya-release/2",
            "release_frozen": True,
            "test_input": False,
            "namespaces": {n: {"manifest_sha256": d["manifest_sha256"],
                               "served_manifest_sha256": d["manifest_sha256"],
                               "passed": True}
                           for n, d in meta["namespaces"].items()},
            "charter_identity": {"published_manifest_sha256": PUBLISHED,
                                 "served_manifest_sha256": PUBLISHED, "passed": True},
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

    def record(self, evidence_path, *extra, name=RELEASE, allow_test_input=True):
        env = {"PVR_ALLOW_TEST_INPUT": "1"} if allow_test_input else {}
        return self.run_script("record_publication.py", "--release", name,
                               "--evidence", evidence_path,
                               "--deploy-id", "68d9a1f0deadbeef00000002",
                               "--deploy-permalink", "https://68d9a1f0--arkaya-record.netlify.app",
                               "--commit", self.COMMIT, "--tag", "release-002", *extra, **env)

    def disclosure_ledgers(self):
        ns = records.DISCLOSURES
        return (os.path.join(self.dir, ns["first_publication_ledger"]),
                os.path.join(self.dir, ns["index_ledger"]),
                os.path.join(self.dir, ns["snapshots"]))


class TestRecording(PublicationCase):
    """G6: record per namespace; the Charter is carried, never recorded anew."""

    def test_approved_evidence_records_the_disclosure_record_and_not_the_charter(self):
        before = self.charter_state()
        r = self.record(self.evidence())
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("carried unchanged at sequence 1", r.stdout)

        # Nothing of the Charter's was written: ledgers, snapshots, release.
        self.assertEqual(before, self.charter_state())
        first = self.load("first_publication.json")
        self.assertEqual({"v1", "v1.1", "v2", "v3"}, set(first["versions"]))
        self.assertEqual({"1"}, set(self.load("published_indexes.json")["versions"]))

        # The disclosure record's own ledgers and snapshot.
        first_path, index_path, snaps = self.disclosure_ledgers()
        with open(first_path) as f:
            d_first = json.load(f)
        self.assertEqual({"v1"}, set(d_first["versions"]))
        self.assertEqual(TODAY, d_first["versions"]["v1"]["first_published"])
        with open(index_path) as f:
            d_index = json.load(f)
        self.assertEqual({"1"}, set(d_index["versions"]))
        meta = self.meta()
        self.assertEqual(meta["namespaces"]["disclosures"]["manifest_sha256"],
                         d_index["versions"]["1"]["manifest_sha256"])

        snap = os.path.join(snaps, "1")
        for name in ("index.json", "manifest.json", "manifest.json.sha256",
                     "carried/charter/manifest.json", "carried/charter/manifest.json.sha256",
                     "carried/charter/index.json", "release.json", "live_verification.json",
                     "publication.json"):
            self.assertTrue(os.path.isfile(os.path.join(snap, name)), name)
        # Both manifests, exactly, and the evidence.
        self.assertEqual(PUBLISHED, sha(os.path.join(snap, "carried", "charter", "manifest.json")))
        self.assertEqual(meta["namespaces"]["disclosures"]["manifest_sha256"],
                         sha(os.path.join(snap, "manifest.json")))
        self.assertEqual(sha(os.path.join(self.dir, "evidence.json")),
                         sha(os.path.join(snap, "live_verification.json")))

        with open(os.path.join(snap, "publication.json")) as f:
            pub = json.load(f)
        self.assertEqual("carried unchanged", pub["namespaces"]["charter"]["state"])
        self.assertEqual(1, pub["namespaces"]["charter"]["sequence"])
        self.assertEqual([], pub["namespaces"]["charter"]["first_publication_entries"])
        self.assertFalse(pub["namespaces"]["charter"]["ledgers_written"])
        self.assertEqual(["v1"], pub["namespaces"]["disclosures"]["first_publication_entries"])
        self.assertEqual("a" * 40, pub["release_commit"])
        self.assertTrue(pub["test_input"])
        self.assertTrue(meta["published"])

    def test_withheld_evidence_is_refused_and_nothing_is_written(self):
        before = self.charter_state()
        r = self.record(self.evidence(production_approval=False, approval_blockers=[
            "the Charter is absent or altered: what is served or held is not the published "
            "Charter"]))
        self.assertEqual(2, r.returncode)
        self.assertIn("did not grant production approval", r.stdout)
        self.assertIn("Nothing was written", r.stdout)
        self.assertEqual(before, self.charter_state())
        self.assertFalse(os.path.exists(os.path.join(self.dir, "ledgers")))
        self.assertFalse(self.meta()["published"])

    def test_a_rehearsal_is_refused(self):
        r = self.record(self.evidence(rehearsal=True))
        self.assertEqual(2, r.returncode)
        self.assertIn("rehearsal", r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "ledgers")))

    def test_evidence_that_the_charter_was_not_identical_is_refused(self):
        r = self.record(self.evidence(charter_identity={"passed": False,
                                                        "served_manifest_sha256": "e" * 64}))
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_IDENTITY] the evidence does not show the published Charter",
                      r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "ledgers")))

    def test_evidence_against_another_disclosure_manifest_is_refused(self):
        with open(self.evidence()) as f:
            ev = json.load(f)
        ev["namespaces"]["disclosures"]["manifest_sha256"] = "f" * 64
        path = os.path.join(self.dir, "evidence.json")
        with open(path, "w") as f:
            json.dump(ev, f)
        r = self.record(path)
        self.assertEqual(2, r.returncode)
        self.assertIn("disclosures: the evidence was taken against manifest", r.stdout)

    def test_single_record_evidence_is_refused_for_a_multi_record_release(self):
        r = self.record(self.evidence(release_schema=None, namespaces=None))
        self.assertEqual(2, r.returncode)
        self.assertIn("not a multi-namespace verification", r.stdout)

    def test_a_test_input_release_is_not_recorded_without_the_explicit_switch(self):
        r = self.record(self.evidence(), allow_test_input=False)
        self.assertEqual(2, r.returncode)
        self.assertIn("[TEST_INPUT]", r.stdout)

    def test_a_charter_altered_after_binding_cannot_be_recorded(self):
        with open(self.rel("charter", "v1", "charter-v1.pdf"), "ab") as f:
            f.write(b"X")
        r = self.record(self.evidence())
        self.assertEqual(2, r.returncode)
        self.assertIn("[CHARTER_IDENTITY]", r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "ledgers")))

    def test_recording_twice_is_refused(self):
        ev = self.evidence()
        self.assertEqual(0, self.record(ev).returncode)
        again = self.record(ev)
        self.assertEqual(2, again.returncode)
        self.assertIn("already recorded as published", again.stdout)

    def test_the_next_release_advances_only_the_disclosure_sequence(self):
        self.assertEqual(0, self.record(self.evidence()).returncode)
        self.register(("v1", "v2"))
        self.built("next-release")
        meta = self.meta("next-release")
        self.assertEqual(2, meta["namespaces"]["disclosures"]["sequence"])
        self.assertEqual(["v2"], meta["namespaces"]["disclosures"]
                         ["versions_awaiting_first_publication"])
        self.assertEqual(1, meta["namespaces"]["charter"]["sequence"])
        idx = self.load("next-release", "disclosures", "index.json")
        self.assertEqual(TODAY, idx["entries"][0]["published_to_record"])

    def test_a_published_multi_release_may_not_be_rebuilt(self):
        self.assertEqual(0, self.record(self.evidence()).returncode)
        r = self.build(PVR_REPLACE_RELEASE="1")
        self.assertEqual(2, r.returncode)
        self.assertIn("recorded as published", r.stdout)

    def test_the_evidence_tag_goes_to_the_disclosure_ledger_only(self):
        self.assertEqual(0, self.record(self.evidence()).returncode)
        before = self.charter_state()
        r = self.run_script("record_publication.py", "--release", RELEASE,
                            "--note-evidence-tag", "--evidence-tag", "publication-002",
                            "--evidence-commit", "b" * 40)
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertEqual(before, self.charter_state())
        _, index_path, _ = self.disclosure_ledgers()
        with open(index_path) as f:
            self.assertEqual("publication-002",
                             json.load(f)["versions"]["1"]["publication_evidence_tag"])

    def test_the_gate_passes_after_publication_and_says_so(self):
        self.assertEqual(0, self.record(self.evidence()).returncode)
        r = self.gate()
        self.assertEqual(0, r.returncode, r.stdout[-3000:])
        with open(os.path.join(self.dir, "verification", f"RELEASE_RECORD_{RELEASE}.md")) as f:
            self.assertIn(f"**Status: published on {TODAY}.**", f.read())


# ======================================================================== G7

class TestNoDisguise(PublicationCase):
    """G7: the disclosure record is its own record, never inside the Charter's."""

    def test_no_disclosure_object_appears_in_any_charter_index_manifest_or_ledger(self):
        self.assertEqual(0, self.record(self.evidence()).returncode)
        charter_files = [os.path.join(self.dir, RELEASE, "charter"),
                         os.path.join(self.dir, "publish", "charter"),
                         os.path.join(self.dir, "publications"),
                         os.path.join(self.dir, "first_publication.json"),
                         os.path.join(self.dir, "published_indexes.json")]
        for root in charter_files:
            paths = [root] if os.path.isfile(root) else [
                os.path.join(d, n) for d, _, ns in os.walk(root) for n in ns]
            for p in paths:
                if p.endswith(".pdf"):
                    continue
                with open(p, "rb") as f:
                    body = f.read().decode("utf-8", "replace").lower()
                for needle in ("disclosure", "test-input", "ledgers/"):
                    self.assertNotIn(needle, body, f"{p} names {needle}")

    def test_the_disclosure_record_reuses_no_charter_field_or_identity(self):
        self.built("fresh")
        idx = self.load("fresh", "disclosures", "index.json")
        man = self.load("fresh", "disclosures", "manifest.json")
        charter_idx = self.load("publish", "charter", "index.json")
        charter_man = self.load("publish", "charter", "manifest.json")
        self.assertNotEqual(charter_idx["schema"], idx["schema"])
        self.assertNotEqual(charter_man["schema"], man["schema"])
        for doc in (idx, man):
            self.assertNotIn("instrument", doc, "the Charter's instrument field is not reused")
            self.assertNotEqual(records.CHARTER["title"], doc.get("record"))
            self.assertTrue(doc["canonical_uri"].startswith(records.DISCLOSURES["canonical_uri"]))
        self.assertNotIn("versions", idx, "the Charter's version list shape is not reused")
        self.assertNotIn("instrument_date", json.dumps(idx))
        for o in man["objects"]:
            self.assertTrue(o["canonical_uri"].startswith(records.DISCLOSURES["canonical_uri"]))
            self.assertNotIn("/charter/", o["canonical_uri"])
        for p in tree(self.rel("disclosures", name="fresh")):
            with open(self.rel("disclosures", p, name="fresh"), "rb") as f:
                body = f.read().decode("utf-8", "replace")
            self.assertNotIn(records.CHARTER["title"], body)
            self.assertNotIn("/charter/", body)
        self.assertEqual(man["builder"]["source_path"], "build_release.py")
        self.assertNotEqual(man["builder"]["sha256"], charter_man["builder"]["sha256"])

    def test_the_registry_refuses_a_disclosure_ledger_shared_with_the_charter(self):
        self.edit_registry('"first_publication_ledger": "ledgers/disclosures/first_publication.json"',
                           '"first_publication_ledger": "first_publication.json"')
        r = self.build("shared-ledger")
        self.assertEqual(2, r.returncode)
        self.assertIn("share a ledger or snapshot location", r.stdout)

    def test_the_namespaces_have_distinct_ledgers_and_snapshots(self):
        c, d = records.CHARTER, records.DISCLOSURES
        for key in ("first_publication_ledger", "index_ledger", "snapshots", "path",
                    "canonical_uri"):
            self.assertNotEqual(c[key], d[key], key)
        self.assertEqual([], records.registry_problems())


# =================================================================== GET

class TestGetNamespace(Sandbox):
    """The GET schema record: its own namespace, its bytes exactly as registered."""

    GET_VERSIONS = (GET_V1,)

    def get_file(self, name=RELEASE, version=GET_V1, issue=1):
        return self.rel("get", version, f"TEST-INPUT-get-schema-issue{issue}.json", name=name)

    def test_a_combined_release_builds_the_get_and_disclosure_records(self):
        self.built()
        self.assertEqual({"index.html", "charter", "disclosures", "get"},
                         set(os.listdir(self.rel())))
        self.assertEqual({"index.json", "index.html", "manifest.json", "manifest.json.sha256",
                          f"{GET_V1}/TEST-INPUT-get-schema-issue1.json"},
                         set(tree(self.rel("get"))))
        meta = self.meta()
        g, d = meta["namespaces"]["get"], meta["namespaces"]["disclosures"]
        self.assertEqual(("built", 1, [GET_V1]),
                         (g["mode"], g["sequence"], g["versions_awaiting_first_publication"]))
        self.assertEqual(("built", 1, ["v1"]),
                         (d["mode"], d["sequence"], d["versions_awaiting_first_publication"]))
        self.assertEqual(sha(self.rel("get", "manifest.json")), g["manifest_sha256"])
        with open(self.rel("get", "manifest.json.sha256")) as f:
            self.assertEqual(g["manifest_sha256"], f.read().split()[0])
        self.assertEqual(tree(os.path.join(self.dir, "publish", "charter")),
                         tree(self.rel("charter")))
        r = self.gate()
        self.assertEqual(0, r.returncode, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("get            built, sequence 1", r.stdout)
        check = self.gate("--check")
        self.assertEqual(0, check.returncode, check.stdout[-3000:])

    def test_the_schema_is_served_with_its_bytes_exactly_as_input(self):
        self.built()
        with open(os.path.join(GET_FIXTURES, "TEST-INPUT-get-schema-issue1.json"), "rb") as f:
            want = f.read()
        # The fixture is hostile on purpose: a byte-order mark, CRLF line
        # endings, a non-ASCII character and no final newline.
        self.assertTrue(want.startswith(b"\xef\xbb\xbf") and b"\r\n" in want
                        and not want.endswith(b"\n") and "é".encode() in want)
        with open(self.get_file(), "rb") as f:
            self.assertEqual(want, f.read(), "the schema bytes changed on the way to be served")
        man = self.load(RELEASE, "get", "manifest.json")
        entry = [o for o in man["objects"] if o.get("version") == GET_V1][0]
        self.assertEqual(f"{GET_V1}/TEST-INPUT-get-schema-issue1.json", entry["path"])
        self.assertEqual("https://record.arkayarisk.com/get/"
                         f"{GET_V1}/TEST-INPUT-get-schema-issue1.json", entry["canonical_uri"])
        self.assertEqual((GET_SCHEMA, sha_bytes(want), len(want)),
                         (entry["mime_type"], entry["sha256"], entry["bytes"]))
        idx = self.load(RELEASE, "get", "index.json")
        self.assertEqual(("public draft for comment", True, TODAY),
                         (idx["entries"][0]["status"], idx["entries"][0]["is_current"],
                          idx["entries"][0]["published_to_record"]))

    def test_the_root_pointer_lists_the_get_record(self):
        self.built()
        with open(self.rel("index.html")) as f:
            page = f.read()
        for ns in ("charter", "disclosures", "get"):
            self.assertIn(f'href="/{ns}/"', page)
        self.assertIn(records.GET["title"], page)

    def assert_refused(self, r, *needles):
        self.assertEqual(2, r.returncode, r.stdout)
        for n in needles:
            self.assertIn(n, r.stdout)
        self.assertFalse(os.path.exists(self.rel()))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "releases", f"{RELEASE}.json")))

    def test_the_get_placeholder_is_refused(self):
        self.write_block("GET REGISTRATION", GET_PLACEHOLDER_BLOCK)
        self.assert_refused(self.build(), "[REGISTRY]", "the GET schema is not registered",
                            "version slug is 'UNREGISTERED'")

    def test_a_registered_digest_that_does_not_match_is_refused(self):
        self.register_get((GET_V1,), sha256="0" * 64)
        self.assert_refused(self.build(), "[INPUTS]", "registered sha256")

    def test_a_registered_byte_count_that_does_not_match_is_refused(self):
        with open(os.path.join(GET_FIXTURES, "TEST-INPUT-get-schema-issue1.json"), "rb") as f:
            size = len(f.read())
        self.register_get((GET_V1,), bytes=size + 1)
        self.assert_refused(self.build(), "[INPUTS]", f"registered {size + 1} bytes")

    def test_version_1_0_is_refused_by_name(self):
        for slug in ("1.0", "1.0/"):
            self.register_get((slug,))
            self.assert_refused(self.build(), "[GET_PATH]", "/get/1.0 and /get/1.0/ are refused "
                                                            "by name")

    def test_a_media_type_other_than_schema_json_is_refused(self):
        self.register_get((GET_V1,), media_type="application/json")
        self.assert_refused(self.build(), "[REGISTRY]", "the GET record serves "
                                                        "application/schema+json")

    def test_a_get_test_input_is_refused_without_the_explicit_switch(self):
        self.assert_refused(self.build(PVR_ALLOW_TEST_INPUT="0"), "[TEST_INPUT]")

    def test_a_schema_altered_after_building_is_refused_at_package(self):
        self.built()
        with open(self.get_file(), "ab") as f:
            f.write(b"\n")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("not the registered bytes", r.stdout)

    def test_a_path_at_get_1_0_is_refused_at_package(self):
        self.built()
        os.makedirs(self.rel("get", "1.0"))
        with open(self.rel("get", "1.0", "schema.json"), "w") as f:
            f.write("{}")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("[GET_PATH] get/1.0/schema.json", r.stdout)

    def test_a_two_issue_lineage_has_one_current_issue(self):
        self.register_get((GET_V1, GET_V2))
        self.built()
        idx = self.load(RELEASE, "get", "index.json")
        self.assertEqual([GET_V1, GET_V2], [e["version"] for e in idx["entries"]])
        self.assertEqual(GET_V2, idx["entries"][0]["superseded_by"])
        self.assertEqual([False, True], [e["is_current"] for e in idx["entries"]])


class TestGetLive(VenueCase):
    """The served GET schema bytes, hashed against the registration."""

    GET_VERSIONS = (GET_V1,)

    def test_the_venue_serving_the_schema_bytes_passes(self):
        r, ev = self.verify()
        self.assertEqual(0, r.returncode, r.stdout[-3000:])
        self.assertTrue(ev["namespaces"]["get"]["passed"])
        path = f"{GET_V1}/TEST-INPUT-get-schema-issue1.json"
        checks = {c["check"]: c["passed"] for c in ev["checks"]}
        for name in (f"[get] digest {path}", f"[get] bytes {path}",
                     f"[get] content-type {path}", f"[get] registered digest {path}",
                     "[get] served manifest matches the frozen manifest",
                     "[get] landing page body matches index.html"):
            self.assertTrue(checks.get(name), name)
        import urllib.request
        with urllib.request.urlopen(f"http://127.0.0.1:{self.venue.port}/get/{path}") as resp:
            served = resp.read()
        with open(os.path.join(GET_FIXTURES, "TEST-INPUT-get-schema-issue1.json"), "rb") as f:
            self.assertEqual(f.read(), served)
        self.assertEqual(sha_bytes(served), ev["served"]["get"][path]["sha256"])

    def test_a_served_schema_that_differs_fails_and_withholds_approval(self):
        path = f"{GET_V1}/TEST-INPUT-get-schema-issue1.json"
        with open(self.venue.path("get", GET_V1, "TEST-INPUT-get-schema-issue1.json"),
                  "ab") as f:
            f.write(b"\n")
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn(f"FAIL  [get] digest {path}", r.stdout)
        self.assertIn(f"FAIL  [get] registered digest {path}", r.stdout)
        self.assertTrue(any("namespace get failed" in b for b in ev["approval_blockers"]))

    def test_the_served_bytes_are_hashed_against_the_registration_not_only_the_manifest(self):
        """Venue and frozen manifest agree; the registration does not. It fails."""
        self.register_get((GET_V1,), sha256="0" * 64)
        r, ev = self.verify()
        path = f"{GET_V1}/TEST-INPUT-get-schema-issue1.json"
        self.assertEqual(1, r.returncode)
        self.assertIn(f"PASS  [get] digest {path}", r.stdout)
        self.assertIn(f"FAIL  [get] registered digest {path}", r.stdout)
        self.assertFalse(ev["namespaces"]["get"]["passed"])

    def test_a_stale_bytecode_cache_of_the_registry_is_never_trusted(self):
        """Regression, 19 October 2026: the case above passed when bytecode was cached.

        A records.cpython-*.pyc is written for the registry, the registration
        is then rewritten with a digest of the same length, and the source's
        modification time is put back, so Python's own check sees the cache as
        current. A plain import reads the stale registration; the verifier must
        not.
        """
        import importlib.util
        import py_compile
        path = os.path.join(self.dir, "records.py")
        before = os.stat(path)
        py_compile.compile(path, cfile=importlib.util.cache_from_source(path), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        self.register_get((GET_V1,), sha256="0" * 64)
        self.assertEqual(before.st_size, os.path.getsize(path))
        os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
        # The trap is set: an ordinary import is served the stale registration.
        stale = subprocess.run(
            [sys.executable, "-c", "import sys; sys.path.insert(0, '.'); import records; "
                                   "print(records.GET_REGISTRATION['entries'][0]['sha256'])"],
            cwd=self.dir, capture_output=True, text=True)
        self.assertNotEqual("0" * 64, stale.stdout.strip(), "the stale cache was not in force")
        r, ev = self.verify()
        path_ = f"{GET_V1}/TEST-INPUT-get-schema-issue1.json"
        self.assertEqual(1, r.returncode, r.stdout[-3000:])
        self.assertIn(f"FAIL  [get] registered digest {path_}", r.stdout)
        self.assertFalse(ev["namespaces"]["get"]["passed"])

    def test_the_reserved_get_paths_are_not_served_and_their_status_is_recorded(self):
        r, ev = self.verify()
        self.assertEqual(0, r.returncode, r.stdout[-3000:])
        checks = {c["check"]: c for c in ev["checks"]}
        for p in ("/get/1.0", "/get/1.0/"):
            c = checks[f"[get] reserved path not served: {p}"]
            self.assertTrue(c["passed"])
            self.assertIn("status 404", c["detail"])

    def test_a_venue_serving_get_1_0_fails_and_withholds_approval(self):
        os.makedirs(self.venue.path("get", "1.0"))
        with open(self.venue.path("get", "1.0", "index.html"), "w") as f:
            f.write("<html>not produced by this pipeline</html>")
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  [get] reserved path not served: /get/1.0 ", r.stdout)
        self.assertIn("FAIL  [get] reserved path not served: /get/1.0/", r.stdout)
        self.assertIn("status 200", r.stdout)
        self.assertFalse(ev["production_approval"])
        self.assertTrue(any("namespace get failed" in b for b in ev["approval_blockers"]))


# ================================================================ carry

class TestCarriedForward(PublicationCase):
    """A built record already published is carried forward byte for byte, never rebuilt."""

    NEXT = "get-only-release"
    GET_VERSIONS = (GET_V1,)

    def publish_first(self):
        r = self.record(self.evidence())
        self.assertEqual(0, r.returncode, r.stdout)
        return self.meta()

    def carry(self, name="disclosures", release=RELEASE, sequence=1, digest=None):
        if digest is None:
            digest = self.meta(release)["namespaces"][name]["manifest_sha256"]
        self.write_carry({name: {"carried_from_release": release, "published_sequence": sequence,
                                 "published_manifest_sha256": digest}})

    def ledger_bytes(self, ns):
        out = {}
        for rel in (ns["first_publication_ledger"], ns["index_ledger"]):
            out[rel] = sha(os.path.join(self.dir, rel))
        for p, d in tree(os.path.join(self.dir, ns["snapshots"])).items():
            out[p] = d
        return out

    def get_only(self):
        self.publish_first()
        self.register_get((GET_V1, GET_V2))
        self.carry()
        self.built(self.NEXT)

    def test_a_get_only_release_carries_the_disclosure_record_byte_for_byte(self):
        self.get_only()
        self.assertEqual(tree(self.rel("disclosures")),
                         tree(self.rel("disclosures", name=self.NEXT)))
        first, meta = self.meta(), self.meta(self.NEXT)
        d, g = meta["namespaces"]["disclosures"], meta["namespaces"]["get"]
        self.assertEqual(("carried", RELEASE, 1, [],
                          first["namespaces"]["disclosures"]["manifest_sha256"],
                          first["namespaces"]["disclosures"]["index_sha256"]),
                         (d["mode"], d["carried_from_release"], d["sequence"],
                          d["versions_awaiting_first_publication"], d["manifest_sha256"],
                          d["index_sha256"]))
        self.assertEqual(("built", 2, [GET_V2]),
                         (g["mode"], g["sequence"], g["versions_awaiting_first_publication"]))
        r = self.gate(name=self.NEXT)
        self.assertEqual(0, r.returncode, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn(f"disclosures    carried from {RELEASE}", r.stdout)
        check = self.gate("--check", name=self.NEXT)
        self.assertEqual(0, check.returncode, check.stdout[-3000:])
        with open(os.path.join(self.dir, "verification",
                               f"RELEASE_RECORD_{self.NEXT}.md")) as f:
            self.assertIn("### `/disclosures/`, carried forward", f.read())

    def test_a_carry_registered_against_another_digest_is_refused(self):
        self.publish_first()
        self.carry(digest="e" * 64)
        r = self.build(self.NEXT)
        self.assertEqual(2, r.returncode)
        # Round 2: refused first as not the latest published record.
        self.assertIn("[CARRY] the disclosures record registered as carried forward is not "
                      "the latest published disclosures record", r.stdout)
        self.assertFalse(os.path.exists(self.rel(name=self.NEXT)))

    def test_a_carried_source_differing_by_one_byte_is_refused(self):
        self.publish_first()
        self.carry()
        with open(self.rel("disclosures", "test-disclosure", "v1", "test-disclosure-v1.md"),
                  "ab") as f:
            f.write(b"X")
        r = self.build(self.NEXT)
        self.assertEqual(2, r.returncode)
        self.assertIn("[CARRY_IDENTITY]", r.stdout)
        self.assertIn(f"{RELEASE}/disclosures/test-disclosure/v1/test-disclosure-v1.md", r.stdout)
        self.assertFalse(os.path.exists(self.rel(name=self.NEXT)))

    def test_carrying_from_an_unpublished_release_is_refused(self):
        self.carry()
        r = self.build(self.NEXT)
        self.assertEqual(2, r.returncode)
        self.assertIn("[CARRY_IDENTITY]", r.stdout)
        self.assertIn("not recorded as published", r.stdout)

    def test_a_carried_record_altered_after_building_is_refused_at_package(self):
        self.get_only()
        with open(self.rel("disclosures", "index.html", name=self.NEXT), "ab") as f:
            f.write(b"\n")
        r = self.gate("--check", name=self.NEXT)
        self.assertEqual(2, r.returncode)
        self.assertIn("[CARRY_IDENTITY] disclosures/index.html", r.stdout)

    def test_recording_a_get_only_release_writes_no_disclosure_ledger(self):
        self.get_only()
        self.assertEqual(0, self.bind(self.NEXT).returncode)
        disclosures_before = self.ledger_bytes(records.DISCLOSURES)
        charter_before = self.charter_state()
        r = self.record(self.evidence(self.NEXT), name=self.NEXT)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"disclosures     carried unchanged from {RELEASE}", r.stdout)
        self.assertEqual(disclosures_before, self.ledger_bytes(records.DISCLOSURES))
        self.assertEqual(charter_before, self.charter_state())
        g = records.GET
        self.assertEqual({"1", "2"}, set(self.load(g["index_ledger"])["versions"]))
        self.assertEqual({GET_V1, GET_V2},
                         set(self.load(g["first_publication_ledger"])["versions"]))
        snap = os.path.join(self.dir, g["snapshots"], "2")
        pub = self.load(g["snapshots"], "2", "publication.json")
        self.assertEqual(("carried unchanged", RELEASE, False),
                         (pub["namespaces"]["disclosures"]["state"],
                          pub["namespaces"]["disclosures"]["carried_from_release"],
                          pub["namespaces"]["disclosures"]["ledgers_written"]))
        self.assertEqual(self.meta(RELEASE)["namespaces"]["disclosures"]["manifest_sha256"],
                         sha(os.path.join(snap, "carried", "disclosures", "manifest.json")))
        self.assertEqual(PUBLISHED, sha(os.path.join(snap, "carried", "charter",
                                                     "manifest.json")))

    def test_a_get_only_release_verifies_live_with_the_carried_record(self):
        self.get_only()
        venue = Venue(self.rel(name=self.NEXT))
        self.addCleanup(venue.close)
        r = self.run_script("verify_live.py", f"--release={self.NEXT}",
                            f"http://127.0.0.1:{venue.port}/",
                            PVR_ALLOW_PLAIN_HTTP="1", PVR_LIVE_OUT_DIR=self.live)
        self.assertEqual(0, r.returncode, r.stdout[-3000:])
        self.assertIn("PASS  [disclosures] carried: served manifest is the published manifest",
                      r.stdout)
        self.assertIn("PASS  [disclosures] carried: the index ledger records the published "
                      "manifest", r.stdout)
        # A venue serving a consistently altered disclosure record fails.
        self.alter_consistently(venue.path("disclosures"))
        r = self.run_script("verify_live.py", f"--release={self.NEXT}",
                            f"http://127.0.0.1:{venue.port}/",
                            PVR_ALLOW_PLAIN_HTTP="1", PVR_LIVE_OUT_DIR=self.live)
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  [disclosures] carried: served manifest is the published manifest",
                      r.stdout)

    def test_a_disclosure_only_release_can_carry_the_get_record(self):
        self.publish_first()
        self.register(("v1", "v2"))
        self.carry(name="get")
        self.built(self.NEXT)
        self.assertEqual(tree(self.rel("get")), tree(self.rel("get", name=self.NEXT)))
        meta = self.meta(self.NEXT)
        self.assertEqual(("carried", 2), (meta["namespaces"]["get"]["mode"],
                                          meta["namespaces"]["disclosures"]["sequence"]))
        for args in ((), ("--check",)):
            g = self.gate(*args, name=self.NEXT)
            self.assertEqual(0, g.returncode, g.stdout[-3000:])
        self.assertIn(f"get            carried from {RELEASE}", g.stdout)

    def test_carrying_every_built_record_is_refused(self):
        self.publish_first()
        first = self.meta()
        self.write_carry({n: {"carried_from_release": RELEASE, "published_sequence": 1,
                              "published_manifest_sha256":
                                  first["namespaces"][n]["manifest_sha256"]}
                          for n in ("disclosures", "get")})
        r = self.build(self.NEXT)
        self.assertEqual(2, r.returncode)
        self.assertIn("would publish nothing new", r.stdout)

    def check_present_carried_get_registration(self, block, expected):
        """Every validator must reject today's bad registration independently."""
        self.publish_first()
        self.register(("v1", "v2"))
        self.carry(name="get")
        self.built(self.NEXT)
        self.assertEqual(0, self.bind(self.NEXT).returncode)
        evidence = self.evidence(self.NEXT)
        before = (tree(os.path.join(self.dir, "ledgers")),
                  tree(os.path.join(self.dir, "releases")),
                  tree(self.rel(name=self.NEXT)))
        self.write_block("GET REGISTRATION", block)
        r = self.build("invalid-carried-get")
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(expected, r.stdout)
        self.assertFalse(os.path.exists(self.rel(name="invalid-carried-get")))
        for args in ((), ("--check",)):
            r = self.gate(*args, name=self.NEXT)
            self.assertEqual(2, r.returncode, r.stdout + r.stderr)
            self.assertIn(expected, r.stdout)
        venue = Venue(self.rel(name=self.NEXT))
        self.addCleanup(venue.close)
        r = self.run_script("verify_live.py", f"--release={self.NEXT}",
                            f"http://127.0.0.1:{venue.port}/",
                            PVR_ALLOW_PLAIN_HTTP="1", PVR_LIVE_OUT_DIR=self.live)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("FAIL  [get] regist", r.stdout)
        r = self.record(evidence, name=self.NEXT)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(expected, r.stdout)
        self.assertEqual(before, (tree(os.path.join(self.dir, "ledgers")),
                                  tree(os.path.join(self.dir, "releases")),
                                  tree(self.rel(name=self.NEXT))))

    def carried_get_block(self, **changes):
        with open(os.path.join(GET_FIXTURES, "TEST-INPUT-get-schema-issue1.json"), "rb") as f:
            body = f.read()
        entry = {"version": GET_V1, "src": "TEST-INPUT-get-schema-issue1.json",
                 "sha256": sha_bytes(body), "bytes": len(body),
                 "document_date": "2026-10-11", "media_type": GET_SCHEMA,
                 "status": "public draft for comment", "reason": "Synthetic GET issue."}
        entry.update(changes)
        return get_registration_block([entry])

    def test_carried_get_rejects_a_different_present_digest_in_every_validator(self):
        self.check_present_carried_get_registration(self.carried_get_block(sha256="0" * 64),
                                                    "sha256")

    def test_carried_get_rejects_a_different_present_size_in_every_validator(self):
        self.check_present_carried_get_registration(self.carried_get_block(bytes=1), "bytes")

    def test_carried_get_rejects_an_empty_present_registration_in_every_validator(self):
        self.check_present_carried_get_registration(
            "# BEGIN GET REGISTRATION\nGET_REGISTRATION = {}\n# END GET REGISTRATION",
            "[REGISTRY]")

    def test_carried_get_rejects_incomplete_present_metadata_in_every_validator(self):
        self.check_present_carried_get_registration(self.carried_get_block(status=""),
                                                    "[REGISTRY]")

    def test_carried_get_still_checks_the_published_bytes_when_new_inputs_are_valid(self):
        self.publish_first()
        self.register(("v1", "v2"))
        self.carry(name="get")
        # Valid new input bytes and registration cannot authorise carrying old bytes.
        self.register_get((GET_V2,))
        r = self.build(self.NEXT)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("[GET_REGISTRATION]", r.stdout)
        self.assertFalse(os.path.exists(self.rel(name=self.NEXT)))

    def test_a_valid_carried_get_checks_present_registration_live_and_records(self):
        self.publish_first()
        self.register(("v1", "v2"))
        self.carry(name="get")
        self.built(self.NEXT)
        venue = Venue(self.rel(name=self.NEXT))
        self.addCleanup(venue.close)
        r = self.run_script("verify_live.py", f"--release={self.NEXT}",
                            f"http://127.0.0.1:{venue.port}/",
                            PVR_ALLOW_PLAIN_HTTP="1", PVR_LIVE_OUT_DIR=self.live)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("PASS  [get] registration valid", r.stdout)
        self.assertIn("PASS  [get] registered digest", r.stdout)
        before = self.ledger_bytes(records.GET)
        self.assertEqual(0, self.bind(self.NEXT).returncode)
        r = self.record(self.evidence(self.NEXT), name=self.NEXT)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(before, self.ledger_bytes(records.GET))

    # --- only the LATEST published record is carried (round 2 guard)

    LATER = "later-disclosure-release"

    def publish_later_disclosures(self):
        """Publish RELEASE (disclosure seq 1), then LATER (disclosure seq 2, GET carried).

        The sandbox analogue of a disclosure-only publish-004 recorded after
        publish-003: afterwards the latest published disclosure release is
        LATER, and RELEASE is an earlier, still valid, published release.
        """
        self.publish_first()
        self.register(("v1", "v2"))
        self.carry(name="get")
        self.built(self.LATER)
        self.assertEqual(0, self.bind(self.LATER).returncode)
        r = self.record(self.evidence(self.LATER), name=self.LATER)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual({"1", "2"}, set(self.load(records.DISCLOSURES["index_ledger"])["versions"]))
        self.register_get((GET_V1, GET_V2))

    def test_carrying_an_earlier_published_disclosure_release_is_refused(self):
        self.publish_later_disclosures()
        self.carry(release=RELEASE, sequence=1)
        r = self.build(self.NEXT)
        self.assertEqual(2, r.returncode, r.stdout)
        self.assertIn("[CARRY]", r.stdout)
        self.assertIn(f"the latest published disclosures release is {self.LATER} at sequence 2",
                      r.stdout)
        self.assertFalse(os.path.exists(self.rel(name=self.NEXT)))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "releases", f"{self.NEXT}.json")))

    def test_carrying_the_latest_release_with_another_digest_is_refused(self):
        self.publish_later_disclosures()
        self.carry(release=self.LATER, sequence=2, digest=self.meta(RELEASE)["namespaces"]
                   ["disclosures"]["manifest_sha256"])
        r = self.build(self.NEXT)
        self.assertEqual(2, r.returncode, r.stdout)
        self.assertIn("[CARRY]", r.stdout)
        self.assertIn(f"the latest published disclosures release is {self.LATER} at sequence 2",
                      r.stdout)
        self.assertFalse(os.path.exists(self.rel(name=self.NEXT)))

    def test_carrying_the_latest_published_disclosure_release_passes(self):
        self.publish_later_disclosures()
        self.carry(release=self.LATER, sequence=2)
        self.built(self.NEXT)
        self.assertEqual(tree(self.rel("disclosures", name=self.LATER)),
                         tree(self.rel("disclosures", name=self.NEXT)))
        for args in ((), ("--check",)):
            g = self.gate(*args, name=self.NEXT)
            self.assertEqual(0, g.returncode, g.stdout[-3000:])
        self.assertIn(f"disclosures    carried from {self.LATER}, sequence 2", g.stdout)
        venue = Venue(self.rel(name=self.NEXT))
        self.addCleanup(venue.close)
        r = self.run_script("verify_live.py", f"--release={self.NEXT}",
                            f"http://127.0.0.1:{venue.port}/",
                            PVR_ALLOW_PLAIN_HTTP="1", PVR_LIVE_OUT_DIR=self.live)
        self.assertEqual(0, r.returncode, r.stdout[-3000:])
        self.assertIn("PASS  [disclosures] carried: from the latest published disclosures "
                      "release", r.stdout)
        self.assertIn("PASS  [disclosures] carried: served index is the latest published index",
                      r.stdout)

    def test_a_get_release_overtaken_by_a_later_disclosure_publication_fails_gate_and_live(self):
        """Built while RELEASE was latest; LATER is published afterwards. It is now stale."""
        self.publish_first()
        self.register_get((GET_V1, GET_V2))
        self.carry()
        self.built(self.NEXT)
        g = self.gate(name=self.NEXT)
        self.assertEqual(0, g.returncode, g.stdout[-3000:])
        # Now a disclosure release is published, as publish-004 could be.
        self.register(("v1", "v2"))
        self.register_get((GET_V1,))
        os.unlink(os.path.join(self.dir, "inputs", "get", "TEST-INPUT-get-schema-issue2.json"))
        self.carry(name="get")
        self.built(self.LATER)
        self.assertEqual(0, self.bind(self.LATER).returncode)
        r = self.record(self.evidence(self.LATER), name=self.LATER)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        # The GET release's registry again, exactly as it was built.
        self.register_get((GET_V1, GET_V2))
        self.carry()
        g = self.gate("--check", name=self.NEXT)
        self.assertEqual(2, g.returncode)
        self.assertIn("[CARRY] the carry entry names disclosures from release-under-test",
                      g.stdout)
        self.assertIn("[CARRY] disclosures/index.json hashes to", g.stdout)
        venue = Venue(self.rel(name=self.NEXT))
        self.addCleanup(venue.close)
        r = self.run_script("verify_live.py", f"--release={self.NEXT}",
                            f"http://127.0.0.1:{venue.port}/",
                            PVR_ALLOW_PLAIN_HTTP="1", PVR_LIVE_OUT_DIR=self.live)
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  [disclosures] carried: from the latest published disclosures "
                      "release", r.stdout)
        self.assertIn("FAIL  [disclosures] carried: served index is the latest published index",
                      r.stdout)

    def test_a_ledger_behind_a_published_marker_is_refused(self):
        self.publish_first()
        meta = self.meta()
        meta["namespaces"]["disclosures"]["sequence"] = 9
        with open(os.path.join(self.dir, "releases", "phantom.json"), "w") as f:
            json.dump(meta, f)
        self.register_get((GET_V1, GET_V2))
        self.carry()
        r = self.build(self.NEXT)
        self.assertEqual(2, r.returncode, r.stdout)
        self.assertIn("[CARRY]", r.stdout)
        self.assertIn("the ledger is behind publication", r.stdout)

    def test_the_charter_cannot_be_registered_as_carried_forward(self):
        self.write_carry({"charter": {"carried_from_release": "publish", "published_sequence": 1,
                                      "published_manifest_sha256": PUBLISHED}})
        r = self.build(self.NEXT)
        self.assertEqual(2, r.returncode)
        self.assertIn("only a built namespace is carried forward", r.stdout)


# ============================================================ GET absent

class TestGetAbsent(Sandbox):
    """GET_REGISTRATION = ABSENT: no GET namespace anywhere, and only ABSENT means that.

    Round 2, 19 October 2026. In round 1 the GET namespace was unconditional and
    shipped as a refused placeholder, so a disclosure-only release that the
    unchanged code builds was refused ("the GET schema is not registered"). The
    tests passed only because the sandbox registered a synthetic GET by
    default. Here nothing registers GET: the sandbox keeps the shipped ABSENT.
    """

    def assert_refused(self, r, *needles):
        self.assertEqual(2, r.returncode, r.stdout)
        for n in needles:
            self.assertIn(n, r.stdout)
        self.assertFalse(os.path.exists(self.rel()))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "releases", f"{RELEASE}.json")))

    def test_the_sandbox_is_the_shipped_absent_registration(self):
        with open(os.path.join(self.dir, "records.py")) as f:
            text = f.read()
        self.assertIn("\nGET_REGISTRATION = ABSENT\n", text)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "inputs", "get")))

    def test_a_disclosure_only_release_builds_with_no_get_namespace(self):
        r = self.built()
        self.assertIn("get          absent   GET_REGISTRATION = ABSENT", r.stdout)
        self.assertEqual({"index.html", "charter", "disclosures"}, set(os.listdir(self.rel())))
        meta = self.meta()
        self.assertEqual({"charter", "disclosures"}, set(meta["namespaces"]))
        with open(self.rel("index.html")) as f:
            page = f.read()
        self.assertNotIn("/get/", page)
        self.assertNotIn(records.GET["title"], page)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "ledgers", "get")))

    def test_the_gate_requires_no_get_check(self):
        self.built()
        for args in ((), ("--check",)):
            r = self.gate(*args)
            self.assertEqual(0, r.returncode, r.stdout[-3000:] + r.stderr[-2000:])
            self.assertIn("2 namespaces", r.stdout)
            self.assertIn("get            absent (GET_REGISTRATION = ABSENT); no GET check "
                          "required", r.stdout)
            self.assertNotIn("[GET", r.stdout)
        with open(os.path.join(self.dir, "verification", f"RELEASE_RECORD_{RELEASE}.md")) as f:
            self.assertNotIn("/get/", f.read())

    def test_a_get_directory_in_a_release_without_get_is_refused_at_package(self):
        self.built()
        os.makedirs(self.rel("get"))
        with open(self.rel("get", "index.json"), "w") as f:
            f.write("{}")
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("[LAYOUT]", r.stdout)

    def test_a_marker_naming_get_is_refused_when_the_registry_has_none(self):
        self.built()
        meta = self.meta()
        meta["namespaces"]["get"] = dict(meta["namespaces"]["disclosures"], path="get")
        self.write_meta(meta)
        r = self.gate("--check")
        self.assertEqual(2, r.returncode)
        self.assertIn("[NAMESPACES] the freeze marker names ['charter', 'disclosures', 'get'], "
                      "the registry ['charter', 'disclosures']", r.stdout)

    def test_only_absent_means_absent_every_ambiguous_form_is_refused(self):
        placeholder = {"version": records.UNREGISTERED, "src": records.UNREGISTERED,
                       "sha256": records.UNREGISTERED, "bytes": None,
                       "document_date": records.UNREGISTERED, "media_type": GET_SCHEMA,
                       "status": records.UNREGISTERED, "reason": records.UNREGISTERED}
        forms = {
            "GET_REGISTRATION = None": "neither ABSENT nor a registration",
            "GET_REGISTRATION = 'absent'": "neither ABSENT nor a registration",
            "GET_REGISTRATION = ''": "neither ABSENT nor a registration",
            "GET_REGISTRATION = {}": "entries is None: not registered",
            "GET_REGISTRATION = {'entries': []}": "An empty registration is not ABSENT",
            "GET_REGISTRATION = {'entries': None}": "entries is None: not registered",
            f"GET_REGISTRATION = {{'entries': [{placeholder!r}]}}":
                "version slug is 'UNREGISTERED'",
            "GET_REGISTRATION = {'entries': [{'version': '1.0.1-test-draft-v1'}]}":
                "byte count is None",
        }
        for line, needle in forms.items():
            with self.subTest(line=line):
                self.write_block("GET REGISTRATION",
                                 f"# BEGIN GET REGISTRATION\n{line}\n# END GET REGISTRATION")
                self.assert_refused(self.build(), "[REGISTRY]", needle)

    def test_the_round_1_placeholder_is_refused_and_says_how_to_declare_absence(self):
        self.write_block("GET REGISTRATION", GET_PLACEHOLDER_BLOCK)
        self.assert_refused(self.build(), "[REGISTRY]", "the GET schema is not registered",
                            "registers GET_REGISTRATION = ABSENT, nothing else")

    def test_absent_is_refused_once_the_get_record_has_been_published(self):
        os.makedirs(os.path.join(self.dir, "ledgers", "get"))
        with open(os.path.join(self.dir, records.GET["index_ledger"]), "w") as f:
            json.dump({"versions": {"1": {}}}, f)
        self.assert_refused(self.build(), "[REGISTRY]", "the GET record has been published",
                            "never dropped from a release")

    def test_carrying_get_while_absent_is_refused(self):
        self.write_carry({"get": {"carried_from_release": "publish-003",
                                  "published_sequence": 1,
                                  "published_manifest_sha256": "a" * 64}})
        self.assert_refused(self.build(), "[REGISTRY]", "cannot carry it")


class TestGetAbsentLive(VenueCase):
    """The live verifier with GET absent: no GET record check, the reserved paths still checked."""

    def test_a_venue_without_get_passes_with_only_the_reserved_path_checks(self):
        r, ev = self.verify()
        self.assertEqual(0, r.returncode, r.stdout[-3000:])
        self.assertEqual({"charter", "disclosures"}, set(ev["namespaces"]))
        self.assertEqual(["get"], ev["absent_namespaces"])
        get_checks = sorted(c["check"] for c in ev["checks"] if c["check"].startswith("[get]"))
        self.assertEqual(["[get] reserved path not served: /get/1.0",
                          "[get] reserved path not served: /get/1.0/"], get_checks)
        for c in ev["checks"]:
            if c["check"].startswith("[get]"):
                self.assertTrue(c["passed"])
                self.assertIn("status 404", c["detail"])
        self.assertIn("links /charter/, /disclosures/", r.stdout)
        self.assertFalse(any("namespace get" in b for b in ev["approval_blockers"]))

    def test_a_venue_serving_get_1_0_still_fails_when_the_release_has_no_get(self):
        os.makedirs(self.venue.path("get", "1.0"))
        with open(self.venue.path("get", "1.0", "index.html"), "w") as f:
            f.write("<html>not produced by this pipeline</html>")
        r, ev = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  [get] reserved path not served: /get/1.0 ", r.stdout)
        self.assertIn("FAIL  [get] reserved path not served: /get/1.0/", r.stdout)
        self.assertFalse(ev["passed"])
        self.assertFalse(ev["production_approval"])
        self.assertTrue(any("check(s) failed" in b for b in ev["approval_blockers"]))


class TestGetAbsentRecording(PublicationCase):
    """The recorder with GET absent: the disclosure record only, nothing under ledgers/get/."""

    def test_recording_writes_no_get_ledger_and_states_no_get_namespace(self):
        before = self.charter_state()
        r = self.record(self.evidence())
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(before, self.charter_state())
        self.assertFalse(os.path.exists(os.path.join(self.dir, "ledgers", "get")))
        _, index_path, snaps = self.disclosure_ledgers()
        self.assertEqual({"1"}, set(self.load(index_path)["versions"]))
        pub = self.load(snaps, "1", "publication.json")
        self.assertEqual({"charter", "disclosures"}, set(pub["namespaces"]))
        self.assertTrue(self.meta()["published"])

    def test_evidence_or_marker_naming_get_is_refused_when_the_registry_has_none(self):
        meta = self.meta()
        meta["namespaces"]["get"] = dict(meta["namespaces"]["disclosures"], path="get")
        self.write_meta(meta)
        r = self.record(self.evidence())
        self.assertEqual(2, r.returncode)
        self.assertIn("[NAMESPACES]", r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "ledgers")))


# The builder and registry at b4e36d3, which built the published publish-003.
BASELINE = os.path.join(HERE, "test_fixtures", "baseline-b4e36d3")
BASELINE_BUILDER_SHA = "d973186ccf98bd63a22815cf0eaf8b36915e51caf01e44779bf3555717765f6d"
BASELINE_REGISTRY_SHA = "78133311589c784eea11aeb1d6acad87fc786b01b2452671e64f1b69ab5cbdbb"

FROZEN_CLOCK = '''import datetime as _real, runpy, sys, types
FIXED = _real.datetime.fromisoformat(sys.argv[1])
class FrozenDateTime(_real.datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED.astimezone(tz) if tz is not None else FIXED.replace(tzinfo=None)
fake = types.ModuleType("datetime")
fake.__dict__.update(_real.__dict__)
fake.datetime = FrozenDateTime
sys.modules["datetime"] = fake
script = sys.argv[2]
sys.argv = [script] + sys.argv[3:]
runpy.run_path(script, run_name="__main__")
'''


def json_leaves(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from json_leaves(v, f"{path}.{k}" if path else k)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from json_leaves(v, f"{path}[{i}]")
    else:
        yield path, x


def differing_leaves(a, b):
    la, lb = dict(json_leaves(a)), dict(json_leaves(b))
    return {k: (la.get(k), lb.get(k)) for k in set(la) | set(lb) if la.get(k) != lb.get(k)}


class TestGetAbsentRegressionIsolation(Sandbox):
    """The absent comparison owns its state, even inside a GET release gate."""

    GET_VERSIONS = (GET_V1,)

    def run_absent_comparison(self):
        r = self.run_script("test_namespaces.py", "TestGetAbsentRegression")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("Ran 2 tests", r.stderr)
        self.assertNotIn("skipped", r.stderr)

    def test_absent_comparison_with_get_registered_before_first_publication(self):
        self.run_absent_comparison()

    def test_absent_comparison_with_get_carry_and_publication_history(self):
        # The outer state must not leak into the deliberate pre-GET comparison.
        self.write_carry({"get": {"carried_from_release": "not-copied-by-comparison",
                                  "published_sequence": 1,
                                  "published_manifest_sha256": "a" * 64}})
        ledger = os.path.join(self.dir, "ledgers", "get")
        os.makedirs(ledger)
        with open(os.path.join(ledger, "first_publication.json"), "w") as f:
            json.dump({"versions": {GET_V1: {"first_published": TODAY}}}, f)
        self.run_absent_comparison()


class TestGetAbsentRegression(unittest.TestCase):
    """With GET absent, a disclosure-only release is the release b4e36d3 builds.

    Two sandboxes hold the same inputs: the real Charter, the real disclosure
    ledgers and inputs, and the registered disclosure entries plus one
    synthetic TEST INPUT issue appended. One runs the builder and registry at
    b4e36d3 (pinned by the digests publish-003 records), the other the current
    builder with GET_REGISTRATION = ABSENT. Both run under one frozen UTC clock.
    Every file of the two release trees must be byte-identical except the
    disclosure manifest and its sidecar, and those two may differ only in the
    builder and registry source digests the manifest records, each the digest
    of its own tree's file.
    """

    INSTANT = "2026-10-19T12:00:00+00:00"
    DAY = "2026-10-19"
    NAME = "regression-release"

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ns-regression-")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.clock = os.path.join(self.root, "frozen_clock.py")
        with open(self.clock, "w") as f:
            f.write(FROZEN_CLOCK)
        self.base, self.new = (self.sandbox("base", baseline=True),
                               self.sandbox("new", baseline=False))

    def sandbox(self, label, baseline):
        d = os.path.join(self.root, label)
        os.makedirs(d)
        for item in SANDBOX + ("ledgers",):
            src = os.path.join(HERE, item)
            if os.path.isdir(src):
                # This comparison deliberately models a world before GET publication.
                # GET history belongs to the outer repository, not this fixture.
                ignore = (lambda directory, names: ["get"] if "get" in names else []) \
                    if item == "ledgers" else None
                shutil.copytree(src, os.path.join(d, item), ignore=ignore)
            elif os.path.isfile(src):
                shutil.copyfile(src, os.path.join(d, item))
        os.makedirs(os.path.join(d, "releases"))
        shutil.copyfile(os.path.join(HERE, "releases", "publish.json"),
                        os.path.join(d, "releases", "publish.json"))
        make_writable(d)
        if baseline:
            for n in ("build_release.py", "records.py"):
                shutil.copyfile(os.path.join(BASELINE, n), os.path.join(d, n))
        # The same disclosure registration in both: the repository's entries and
        # one synthetic issue appended, as a real next issue would be.
        reg = records.DISCLOSURE_REGISTRATION
        n = max(int(e["version"][1:]) for e in reg["entries"]) + 1
        body = (b"<!-- ARKAYA-TEST-INPUT -->\n# TEST INPUT: synthetic disclosure issue for the "
                b"GET-absent regression test\n")
        name = f"TEST-INPUT-disclosure-v{n}.md"
        with open(os.path.join(d, "inputs", "disclosures", name), "wb") as f:
            f.write(body)
        entries = list(reg["entries"]) + [{
            "version": f"v{n}", "src": name, "sha256": sha_bytes(body), "bytes": len(body),
            "document_date": self.DAY, "reason": "Synthetic issue. TEST INPUT."}]
        path = os.path.join(d, "records.py")
        with open(path) as f:
            text = f.read()
        block = registration_block(entries, slug=reg["record_slug"], title=reg["title"])
        new = re.sub(r"# BEGIN DISCLOSURE REGISTRATION.*?# END DISCLOSURE REGISTRATION",
                     lambda m: block, text, flags=re.S)
        self.assertNotEqual(text, new)
        if not baseline:
            new = re.sub(r"# BEGIN GET REGISTRATION.*?# END GET REGISTRATION",
                         lambda m: GET_ABSENT_BLOCK, new, flags=re.S)
            new = re.sub(r"# BEGIN CARRY REGISTRATION.*?# END CARRY REGISTRATION",
                         lambda m: "# BEGIN CARRY REGISTRATION\nCARRY_REGISTRATION = {}\n"
                                   "# END CARRY REGISTRATION", new, flags=re.S)
        with open(path, "w") as f:
            f.write(new)
        return d

    def build_in(self, d):
        e = {k: v for k, v in os.environ.items() if not k.startswith("PVR_")}
        e.update(PVR_RELEASE_DIR=os.path.join(d, self.NAME), PVR_ALLOW_TEST_INPUT="1",
                 PVR_RELEASE_DATE=self.DAY)
        r = subprocess.run([sys.executable, self.clock, self.INSTANT,
                            os.path.join(d, "build_release.py")],
                           cwd=d, env=e, capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        return r

    def test_the_baseline_is_the_builder_and_registry_that_built_publish_003(self):
        self.assertEqual(BASELINE_BUILDER_SHA, sha(os.path.join(BASELINE, "build_release.py")))
        self.assertEqual(BASELINE_REGISTRY_SHA, sha(os.path.join(BASELINE, "records.py")))
        marker = os.path.join(HERE, "releases", "publish-003.json")
        if os.path.isfile(marker):
            with open(marker) as f:
                m = json.load(f)
            self.assertEqual(BASELINE_BUILDER_SHA, m["release_builder"]["sha256"])
            self.assertEqual(BASELINE_REGISTRY_SHA, m["registry_sha256"])

    def test_a_disclosure_only_release_is_byte_identical_to_the_b4e36d3_build(self):
        self.build_in(self.base)
        out = self.build_in(self.new)
        self.assertIn("GET_REGISTRATION = ABSENT", out.stdout)
        a = tree(os.path.join(self.base, self.NAME))
        b = tree(os.path.join(self.new, self.NAME))
        self.assertEqual(set(a), set(b), "the two releases hold different files")
        self.assertFalse(any(p.startswith("get" + os.sep) for p in b))
        differ = sorted(p for p in a if a[p] != b[p])
        self.assertEqual([os.path.join("disclosures", "manifest.json"),
                          os.path.join("disclosures", "manifest.json.sha256")], differ)

        # The manifests differ in exactly the two recorded source digests ...
        rel = os.path.join(self.NAME, "disclosures", "manifest.json")
        ma, mb = self.load(self.base, rel), self.load(self.new, rel)
        diff = differing_leaves(ma, mb)
        self.assertEqual({"builder.sha256", "registry.sha256"}, set(diff))
        for d, m in ((self.base, ma), (self.new, mb)):
            self.assertEqual(sha(os.path.join(d, "build_release.py")), m["builder"]["sha256"])
            self.assertEqual(sha(os.path.join(d, "records.py")), m["registry"]["sha256"])
        # ... and nowhere else, byte for byte: with the base digests put back,
        # the new manifest serialises to the base manifest's exact bytes.
        mb["builder"]["sha256"] = ma["builder"]["sha256"]
        mb["registry"]["sha256"] = ma["registry"]["sha256"]
        with open(os.path.join(self.base, rel), "rb") as f:
            self.assertEqual(f.read(), json.dumps(mb, indent=2).encode())
        # Each sidecar is the digest of its own manifest.
        for d in (self.base, self.new):
            with open(os.path.join(d, rel + ".sha256")) as f:
                self.assertEqual(sha(os.path.join(d, rel)), f.read().split()[0])

        # The freeze markers, outside the release tree, differ only in those
        # digests and the manifest digest that follows from them.
        diff = differing_leaves(self.load(self.base, "releases", f"{self.NAME}.json"),
                                self.load(self.new, "releases", f"{self.NAME}.json"))
        self.assertEqual({"release_builder.sha256", "registry_sha256",
                          "namespaces.disclosures.builder.sha256",
                          "namespaces.disclosures.manifest_sha256"}, set(diff))

    def load(self, *parts):
        with open(os.path.join(*parts)) as f:
            return json.load(f)


# ========================================================== registration

class TestRegistration(Sandbox):
    """The single registration place, its placeholder, and the TEST INPUT marker."""

    REGISTER = False

    def assert_refused(self, r, *needles):
        self.assertEqual(2, r.returncode, r.stdout)
        for n in needles:
            self.assertIn(n, r.stdout)
        self.assertFalse(os.path.exists(self.rel()))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "releases", f"{RELEASE}.json")))

    def test_the_placeholder_is_refused(self):
        """The shape records.py ships with until freeze builds nothing."""
        r = self.build()
        self.assert_refused(r, "[REGISTRY]", "the disclosure carrier is not registered",
                            "record_slug is 'UNREGISTERED'")

    def test_the_repository_registry_is_refused_by_the_checker(self):
        """Whatever the repository holds must satisfy the checker, or be the placeholder."""
        problems = records.registration_problems()
        if records.DISCLOSURE_REGISTRATION["record_slug"] == records.UNREGISTERED:
            self.assertTrue(problems)
        else:
            self.assertEqual([], problems)

    def test_the_repository_get_and_carry_registrations_are_checked(self):
        """The shipped GET block is ABSENT or a valid registration, never a placeholder."""
        if records.get_absent():
            self.assertNotIn("get", [ns["name"] for ns in records.NAMESPACES])
        else:
            self.assertIsInstance(records.GET_REGISTRATION, dict)
            self.assertEqual([], records.get_registration_problems())
            self.assertIn("get", [ns["name"] for ns in records.NAMESPACES])
        self.assertEqual([], records.registry_problems())
        self.assertEqual([], records.carry_registration_problems())

    def test_a_half_completed_registration_is_refused(self):
        self.register(("v1",), bytes=None)
        r = self.build()
        self.assert_refused(r, "[REGISTRY]", "byte count is None")

    def test_a_registered_digest_that_does_not_match_is_refused(self):
        self.register(("v1",), sha256="0" * 64)
        r = self.build()
        self.assert_refused(r, "[INPUTS]", "registered sha256")

    def test_an_unregistered_extra_input_is_refused(self):
        self.register(("v1",))
        shutil.copyfile(os.path.join(FIXTURES, "TEST-INPUT-disclosure-v2.md"),
                        os.path.join(self.dir, "inputs", "disclosures", "extra.md"))
        r = self.build()
        self.assert_refused(r, "[INPUTS]", "unexpected disclosure input(s): extra.md")

    def test_a_test_input_is_refused_without_the_explicit_switch(self):
        self.register(("v1",))
        r = self.build(PVR_ALLOW_TEST_INPUT="0")
        self.assert_refused(r, "[TEST_INPUT]")

    def test_a_version_that_is_not_a_whole_integer_is_refused(self):
        self.register(("v1",), version="v1.1")
        r = self.build()
        self.assert_refused(r, "[REGISTRY]", "whole integer")


# ============================================================ the gate

class TestGateEnvironment(unittest.TestCase):

    def test_the_test_stage_does_not_inherit_the_release_selection(self):
        """Found running the full gate as `PVR_RELEASE=<release> package.py`.

        Every nested package.py in test_package.py inherited PVR_RELEASE and
        gated the multi-record release instead of its own sandbox: 58 failures.
        """
        import package
        saved = dict(os.environ)
        try:
            os.environ.update(PVR_RELEASE="some-release", PVR_ALLOW_TEST_INPUT="1",
                              PVR_NO_RECURSE="1", UNRELATED="kept")
            env = package.test_environment()
        finally:
            os.environ.clear()
            os.environ.update(saved)
        self.assertNotIn("PVR_RELEASE", env)
        self.assertNotIn("PVR_ALLOW_TEST_INPUT", env)
        self.assertEqual("1", env.get("PVR_NO_RECURSE"))
        self.assertEqual("kept", env.get("UNRELATED"))


# ================================================================ targets

class TestReleaseTarget(Sandbox):
    """A new release goes into a new directory; publish/ is never touched."""

    def test_no_release_dir_is_refused(self):
        r = self.run_script("build_release.py", PVR_ALLOW_TEST_INPUT="1")
        self.assertEqual(2, r.returncode)
        self.assertIn("[RELEASE_DIR] PVR_RELEASE_DIR is not set", r.stdout)

    def test_the_published_release_is_never_a_target(self):
        before = tree(os.path.join(self.dir, "publish"))
        r = self.build("publish")
        self.assertEqual(2, r.returncode)
        self.assertIn("[RELEASE_DIR]", r.stdout)
        self.assertIn("immutable", r.stdout)
        self.assertEqual(before, tree(os.path.join(self.dir, "publish")))

    def test_a_release_outside_the_repository_is_refused(self):
        elsewhere = tempfile.mkdtemp(prefix="ns-elsewhere-")
        self.addCleanup(shutil.rmtree, elsewhere, True)
        r = self.run_script("build_release.py", PVR_ALLOW_TEST_INPUT="1",
                            PVR_RELEASE_DIR=os.path.join(elsewhere, "rel"))
        self.assertEqual(2, r.returncode)
        self.assertIn("[RELEASE_DIR]", r.stdout)

    def test_a_release_reached_through_a_symlink_is_beside_the_builder(self):
        # Regression, 28 September 2026: on macOS /var is a link to /private/var,
        # the builder's own location is reported resolved and PVR_RELEASE_DIR was
        # not, so every build under the system temporary directory was refused and
        # the gate failed 54 tests there while passing on Linux. The same shape is
        # built here on any platform by addressing the sandbox through a link.
        linkdir = tempfile.mkdtemp(prefix="ns-link-")
        self.addCleanup(shutil.rmtree, linkdir, True)
        link = os.path.join(linkdir, "sandbox")
        os.symlink(self.dir, link)
        r = self.run_script("build_release.py", PVR_ALLOW_TEST_INPUT="1",
                            PVR_RELEASE_DIR=os.path.join(link, RELEASE))
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(self.dir, RELEASE, "charter", "manifest.json")))

    def test_a_link_does_not_admit_a_release_outside_the_repository(self):
        elsewhere = tempfile.mkdtemp(prefix="ns-elsewhere-")
        self.addCleanup(shutil.rmtree, elsewhere, True)
        linkdir = tempfile.mkdtemp(prefix="ns-link-")
        self.addCleanup(shutil.rmtree, linkdir, True)
        link = os.path.join(linkdir, "elsewhere")
        os.symlink(elsewhere, link)
        r = self.run_script("build_release.py", PVR_ALLOW_TEST_INPUT="1",
                            PVR_RELEASE_DIR=os.path.join(link, "rel"))
        self.assertEqual(2, r.returncode)
        self.assertIn("[RELEASE_DIR]", r.stdout)

    def test_a_frozen_release_is_not_rebuilt_over(self):
        self.built()
        before = tree(self.rel())
        r = self.build()
        self.assertEqual(2, r.returncode)
        self.assertIn("[FROZEN]", r.stdout)
        self.assertEqual(before, tree(self.rel()))
        self.assertEqual(0, self.build(PVR_REPLACE_RELEASE="1").returncode)

    def test_a_date_that_is_not_the_build_date_is_refused(self):
        r = self.build(PVR_RELEASE_DATE="2026-07-29")
        self.assertEqual(2, r.returncode)
        self.assertIn("[RELEASE_DATE]", r.stdout)
        self.assertFalse(os.path.exists(self.rel()))

    def test_a_refused_build_leaves_no_staging_behind(self):
        with open(os.path.join(self.dir, "publish", "charter", "index.json"), "ab") as f:
            f.write(b" ")
        self.assertEqual(2, self.build().returncode)
        self.assertEqual([], [n for n in os.listdir(self.dir) if n.startswith(".staging")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
