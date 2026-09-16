"""Prove the live verifier rejects a known-bad venue before it is trusted on a real one.

A check that has only ever been run against a correct record is not evidence that
it would catch an incorrect one. Each test serves a deliberately wrong venue and
requires the verifier to fail on the specific thing that is wrong.

Three of these exist because DM reproduced the defect they now cover: a venue
serving a wrong manifest with a consistent sidecar passed, a venue serving
anything at `/charter/` passed, and nothing distinguished an exploratory run from
one that could be relied on.

Run: python3 test_verify_live.py
"""

import hashlib
import http.server
import json
import os
import shutil
import socket
import stat
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "publish")


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class Venue(unittest.TestCase):
    """Serves a private copy of the deploy root, which each test may damage."""

    substitute_landing = None       # bytes served at /charter/ instead of index.html

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="venue-")
        self.root = os.path.join(self.dir, "publish")
        shutil.copytree(SOURCE, self.root)
        # The tests below damage this copy. A shipped read-only file would make
        # them fail with PermissionError rather than test what they claim.
        for dirpath, dirnames, filenames in os.walk(self.dir):
            for name in dirnames + filenames:
                q = os.path.join(dirpath, name)
                try:
                    os.chmod(q, os.stat(q).st_mode | stat.S_IWUSR)
                except OSError:
                    pass
        self.port = free_port()
        test = self

        class H(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **kw):
                super().__init__(*a, directory=test.root, **kw)

            def log_message(self, *a):
                pass

            def do_GET(self):
                if test.substitute_landing is not None and self.path == "/charter/":
                    body = test.substitute_landing
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

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        shutil.rmtree(self.dir, ignore_errors=True)

    def verify(self):
        env = dict(os.environ, PVR_ALLOW_PLAIN_HTTP="1")
        return subprocess.run(
            [sys.executable, "verify_live.py", f"http://127.0.0.1:{self.port}/charter/"],
            cwd=HERE, env=env, capture_output=True, text=True)

    def path(self, *parts):
        return os.path.join(self.root, "charter", *parts)


class TestLiveVerifier(Venue):

    def test_correct_venue_passes_but_is_not_approved(self):
        r = self.verify()
        self.assertEqual(0, r.returncode, r.stdout[-2000:])
        self.assertIn("NOT EXERCISED", r.stdout,
                      "a plain-HTTP rehearsal must say which transport checks it did not run")
        self.assertIn("PRODUCTION APPROVAL: WITHHELD", r.stdout,
                      "a rehearsal must never grant production approval")
        self.assertIn("rehearsal over plain HTTP", r.stdout)

    def test_tampered_object_is_detected(self):
        with open(self.path("v2", "charter-v2.pdf"), "ab") as f:
            f.write(b"TAMPER")
        r = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  digest v2/charter-v2.pdf", r.stdout)
        self.assertIn("DO NOT ARCHIVE", r.stdout)

    def test_missing_object_is_detected(self):
        os.unlink(self.path("v1.1", "charter-v1.1.pdf"))
        r = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("served v1.1/charter-v1.1.pdf", r.stdout)

    def test_substituted_index_is_detected(self):
        with open(self.path("index.json")) as f:
            doc = json.load(f)
        doc["versions"] = [v for v in doc["versions"] if v["version"] != "v1"]
        with open(self.path("index.json"), "w") as f:
            json.dump(doc, f, indent=2)
        r = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  digest index.json", r.stdout)

    def test_wrong_served_manifest_with_a_consistent_sidecar_is_detected(self):
        """DM's finding 3: this exact venue passed the previous verifier.

        The manifest is not in `objects` because it cannot contain its own
        digest. The old verifier therefore never fetched it, and compared the
        served sidecar against the LOCAL manifest. Making the sidecar agree with
        a substituted manifest defeated the whole check.
        """
        with open(self.path("manifest.json")) as f:
            man = json.load(f)
        man["objects"] = [o for o in man["objects"] if o.get("version") != "v1"]
        man["provenance_claim"] = "this manifest was substituted"
        body = json.dumps(man, indent=2).encode()
        with open(self.path("manifest.json"), "wb") as f:
            f.write(body)
        with open(self.path("manifest.json.sha256"), "w") as f:
            f.write(sha_bytes(body) + "  manifest.json\n")

        r = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  served manifest matches the frozen manifest", r.stdout)
        self.assertIn("FAIL  served sidecar matches the frozen manifest", r.stdout)
        self.assertIn("PASS  served sidecar matches the served manifest", r.stdout,
                      "the sidecar is internally consistent: that is the point of the test")

    def test_wrong_landing_page_is_detected(self):
        """DM's finding 3: the address people visit was only checked for a 200."""
        self.substitute_landing = b"<html><body>Arkaya record: <a href='/charter/'>here</a></body></html>"
        r = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  landing page body matches index.html", r.stdout)
        self.assertIn("PASS  digest index.html", r.stdout,
                      "index.html itself is untouched: only the landing page differs")

    def test_internal_file_exposure_is_detected(self):
        shutil.copyfile(os.path.join(HERE, "build_publication_set.py"),
                        os.path.join(self.root, "build_publication_set.py"))
        r = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("internal file not served: build_publication_set.py", r.stdout)

    def test_catch_all_responder_is_detected(self):
        """A venue answering every path 200 makes retrieval checks meaningless."""
        test = self

        class CatchAll(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **kw):
                super().__init__(*a, directory=test.root, **kw)

            def log_message(self, *a):
                pass

            def send_error(self, code, *a, **kw):           # noqa: D102
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html>not found, but 200</html>")

        self.srv.shutdown()
        self.srv.server_close()
        socketserver.TCPServer.allow_reuse_address = True
        self.srv = socketserver.TCPServer(("127.0.0.1", self.port), CatchAll)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

        r = self.verify()
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL  control path 404s", r.stdout)

    def test_evidence_records_approval_and_its_blockers(self):
        r = self.verify()
        self.assertEqual(0, r.returncode)
        live = os.path.join(HERE, "verification", "live")
        newest = max((os.path.join(live, f) for f in os.listdir(live)), key=os.path.getmtime)
        with open(newest) as f:
            ev = json.load(f)
        self.assertTrue(ev["rehearsal"])
        self.assertFalse(ev["production_approval"])
        self.assertTrue(ev["release_frozen"])
        self.assertTrue(any("canonical address is" in b for b in ev["approval_blockers"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
