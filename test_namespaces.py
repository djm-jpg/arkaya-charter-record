"""Prove the multi-namespace pipeline carries the Charter unchanged and refuses otherwise.

The governance decision of 28 September 2026: the pipeline may carry a second
record, the disclosure record at /disclosures/, only if /charter/ in every new
release is byte for byte the published Charter, no release omits it, the
disclosure record is a record of its own and not a disguised Charter copy, and
nothing already published moves or changes.

Every guarantee below is exercised by breaking the thing it guards. The gate
numbering (G2 to G7) is the one the change was specified against.

INPUTS. No real disclosure is an input here. Each sandbox copies the synthetic
TEST INPUT fixtures from `test_fixtures/disclosures/` and registers their digests
in the SANDBOX's own copy of `records.py`, in the same single block an operator
completes at freeze. The repository's `records.py` is never edited by a test.

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


# The shipped placeholder, as records.py carries it until freeze.
PLACEHOLDER_BLOCK = registration_block(
    [{"version": "v1", "src": records.UNREGISTERED, "sha256": records.UNREGISTERED,
      "bytes": None, "document_date": records.UNREGISTERED, "reason": None}],
    slug=records.UNREGISTERED, title=records.UNREGISTERED)


class Sandbox(unittest.TestCase):
    """A private copy of the repository, with the TEST INPUT registered in it."""

    VERSIONS = ("v1",)
    REGISTER = True

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
        self.write_registration(PLACEHOLDER_BLOCK)
        if self.REGISTER:
            self.register(self.VERSIONS)

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
        path = os.path.join(self.dir, "records.py")
        with open(path) as f:
            text = f.read()
        new = re.sub(r"# BEGIN DISCLOSURE REGISTRATION.*?# END DISCLOSURE REGISTRATION",
                     lambda m: block, text, flags=re.S)
        self.assertNotEqual(text, new, "the registration block was not found")
        with open(path, "w") as f:
            f.write(new)

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
        self.edit_registry("NAMESPACES = (CHARTER, DISCLOSURES)", "NAMESPACES = (DISCLOSURES,)")
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
