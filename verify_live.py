"""Verify the live canonical venue against the frozen release, before archival.

DM's finding 7 of 16 September 2026: HTTPS, the canonical paths and every served
hash are to be verified before anything is archived. Archiving first captures
whatever was served, correct or not, and lends it the appearance of a checked
record.

DM's finding 3 of the same review, which this version answers:

  - The verifier never fetched `manifest.json`. It compared the served SIDECAR
    against the LOCAL manifest, so a venue serving a wrong manifest with a
    matching sidecar passed. The served manifest is now fetched and hashed
    against the frozen local manifest, and the served sidecar is compared
    against the SERVED manifest as well as the local one.
  - The landing page was only checked for reachability. Bytes were compared at
    `/charter/index.html` but not at `/charter/`, so a venue could serve
    anything at the address people actually visit. The body returned at
    `/charter/` is now hashed against the expected index.html.
  - Redirects were accepted on scheme alone. The destination is now compared.
  - Nothing distinguished an exploratory run from one that may be relied on.
    PRODUCTION APPROVAL is now a separate, stricter result: it requires a frozen
    release, the canonical address, HTTPS, and every check passing.

    python3 verify_live.py                       # https://record.arkayarisk.com/charter/
    python3 verify_live.py https://host/charter/

Exit 0 only if every check passes. Production approval is reported separately and
is what `record_publication.py` requires.
"""

import hashlib
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "verification", "live")

DEFAULT_BASE = "https://record.arkayarisk.com/charter/"
TIMEOUT = 30

EXPECTED_TYPE = {
    "application/pdf": "application/pdf",
    "application/json": "application/json",
    "text/html": "text/html",
    "text/markdown": "text/markdown",
}

INTERNAL = ("build_publication_set.py", "package.py", "record_publication.py",
            "README_source.md", "first_publication.json", "published_indexes.json",
            "releases/publish.json", "verification/PRODUCTION_RECORD.md")


class Headers:
    """Case-insensitive header access.

    An earlier cut converted the response headers to a plain dict, which silently
    lost the case-insensitive lookup HTTP headers require. The local rehearsal
    caught it: a server sending "Content-type" read as no content type at all.
    On a host sending "Content-Type" the same code would have passed, so the
    defect would have shipped.
    """

    def __init__(self, msg):
        self._m = {k.lower(): v for k, v in (msg or {}).items()}

    def get(self, name, default=None):
        return self._m.get(name.lower(), default)

    def as_dict(self):
        return dict(self._m)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "arkaya-record-verify/1"})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            return {"status": r.status, "headers": Headers(r.headers), "body": r.read(),
                    "final_url": r.url}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "headers": Headers(e.headers), "body": b"",
                "final_url": url}
    except Exception as e:                                   # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}", "status": None,
                "headers": Headers(None), "body": b"", "final_url": url}


def local_release(release_name):
    """The frozen release this run is verifying against.

    A verification against an unfrozen working directory is exploratory: the
    local set can change under it. Production approval requires the freeze
    marker and requires the release directory still to match it.
    """
    meta_path = os.path.join(HERE, "releases", f"{release_name}.json")
    record = os.path.join(HERE, release_name, "charter")
    manifest_path = os.path.join(record, "manifest.json")
    if not os.path.isfile(manifest_path):
        raise SystemExit(f"no built release at {release_name}/charter/manifest.json")
    with open(manifest_path, "rb") as f:
        raw = f.read()
    manifest = json.loads(raw)
    local_manifest_sha = hashlib.sha256(raw).hexdigest()

    frozen, drift = None, None
    if os.path.isfile(meta_path):
        with open(meta_path) as f:
            frozen = json.load(f)
        if frozen["manifest_sha256"] != local_manifest_sha:
            drift = (f"the release directory no longer matches its freeze marker "
                     f"({local_manifest_sha[:16]}… vs {frozen['manifest_sha256'][:16]}…)")
    with open(os.path.join(record, "index.html"), "rb") as f:
        index_html_sha = hashlib.sha256(f.read()).hexdigest()
    return manifest, local_manifest_sha, index_html_sha, frozen, drift


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    release_name = next((a.split("=", 1)[1] for a in argv if a.startswith("--release=")),
                        "publish")
    base = (args[0] if args else DEFAULT_BASE)
    if not base.endswith("/"):
        base += "/"

    # Rehearsal against a local HTTP server is how this script is itself tested.
    # It is an explicit opt-in, it is recorded in the output, it can never grant
    # production approval, and the transport checks it cannot exercise are listed
    # as not-exercised rather than counted as passes.
    rehearsal = os.environ.get("PVR_ALLOW_PLAIN_HTTP") == "1"
    if not base.startswith("https://") and not rehearsal:
        print("REFUSED: the canonical venue must be verified over HTTPS.")
        return 2

    manifest, local_manifest_sha, index_html_sha, frozen, drift = local_release(release_name)

    findings, checks, not_exercised = [], [], []

    def record(name, ok, detail):
        checks.append({"check": name, "passed": bool(ok), "detail": detail})
        if not ok:
            findings.append(f"{name}: {detail}")

    # 0. What this run is verifying against.
    record("local release is frozen", frozen is not None and not drift,
           drift or (f"frozen release, sequence {frozen['sequence']}, manifest "
                     f"{local_manifest_sha[:16]}…" if frozen else
                     "no freeze marker: exploratory run against an unfrozen directory"))

    # 1. Transport. A record served over plain HTTP, or downgraded on redirect,
    #    is not the record this manifest describes.
    root = fetch(base)
    if not rehearsal:
        record("https reachable",
               root.get("status") == 200 and root["final_url"].startswith("https://"),
               root.get("error") or f"status {root.get('status')}, final URL {root['final_url']}")

        plain = fetch("http://" + base[len("https://"):])
        # Destination equality, not merely "ends up on https somewhere".
        record("http redirects to the same https address",
               plain.get("status") == 200 and plain["final_url"] == base,
               plain.get("error") or f"status {plain.get('status')}, "
                                     f"final URL {plain['final_url']}, expected {base}")

        hsts = root["headers"].get("Strict-Transport-Security")
        record("strict-transport-security present", bool(hsts), hsts or "header absent")
    else:
        not_exercised += ["https reachable", "http redirects to the same https address",
                          "strict-transport-security present"]
        record("index reachable", root.get("status") == 200,
               root.get("error") or f"status {root.get('status')}")

    # 2. THE LANDING PAGE ITSELF. The address people visit must serve the page
    #    that was built, not merely something with a 200 status.
    if root.get("status") == 200:
        served_root_sha = hashlib.sha256(root["body"]).hexdigest()
        record("landing page body matches index.html", served_root_sha == index_html_sha,
               f"expected {index_html_sha[:16]}… served {served_root_sha[:16]}…")
        rtype = (root["headers"].get("Content-Type") or "").split(";")[0].strip()
        record("landing page content-type", rtype == "text/html",
               f"expected text/html, served {rtype or 'none'}")
    else:
        record("landing page body matches index.html", False,
               f"landing page not retrieved: status {root.get('status')}")

    # 3. THE SERVED MANIFEST. It is not in `objects` because it cannot contain
    #    its own digest, which is exactly why it went unfetched. A venue serving
    #    a wrong manifest with a consistent sidecar passed the previous version.
    man = fetch(base + "manifest.json")
    served_manifest_sha = None
    if man.get("status") == 200:
        served_manifest_sha = hashlib.sha256(man["body"]).hexdigest()
        record("served manifest matches the frozen manifest",
               served_manifest_sha == local_manifest_sha,
               f"frozen {local_manifest_sha[:16]}… served {served_manifest_sha[:16]}…")
    else:
        record("served manifest matches the frozen manifest", False,
               man.get("error") or f"HTTP {man.get('status')}")

    side = fetch(base + "manifest.json.sha256")
    if side.get("status") == 200 and side["body"].split():
        recorded = side["body"].decode("utf-8", "replace").split()[0]
        record("served sidecar matches the served manifest",
               served_manifest_sha is not None and recorded == served_manifest_sha,
               f"sidecar {recorded[:16]}… served manifest "
               f"{(served_manifest_sha or 'not-retrieved')[:16]}…")
        record("served sidecar matches the frozen manifest", recorded == local_manifest_sha,
               f"sidecar {recorded[:16]}… frozen {local_manifest_sha[:16]}…")
    else:
        record("served sidecar matches the served manifest", False,
               f"HTTP {side.get('status')}")
        record("served sidecar matches the frozen manifest", False,
               f"HTTP {side.get('status')}")

    # 4. Every object the manifest names, at its canonical path, byte for byte.
    served = {}
    for o in manifest["objects"]:
        r = fetch(base + o["path"])
        if r.get("error") or r["status"] != 200:
            record(f"served {o['path']}", False, r.get("error") or f"HTTP {r['status']}")
            continue
        got = hashlib.sha256(r["body"]).hexdigest()
        ctype = (r["headers"].get("Content-Type") or "").split(";")[0].strip()
        served[o["path"]] = {"sha256": got, "bytes": len(r["body"]),
                             "content_type": ctype, "status": 200,
                             "cache_control": r["headers"].get("Cache-Control"),
                             "etag": r["headers"].get("ETag"),
                             "last_modified": r["headers"].get("Last-Modified")}
        record(f"digest {o['path']}", got == o["sha256"],
               f"manifest {o['sha256'][:16]}… served {got[:16]}…")
        record(f"bytes {o['path']}", len(r["body"]) == o["bytes"],
               f"manifest {o['bytes']} served {len(r['body'])}")
        want = EXPECTED_TYPE.get(o["mime_type"])
        record(f"content-type {o['path']}", ctype == want,
               f"expected {want}, served {ctype or 'none'}")

    # 5. A path that must NOT exist. A host answering everything with a generic
    #    page makes every retrieval check meaningless.
    control = fetch(base + "definitely-not-here")
    record("control path 404s", control.get("status") == 404, f"status {control.get('status')}")

    # 6. The deploy root serves the pointer, not a directory listing.
    apex_base = base.rsplit("/charter/", 1)[0] + "/"
    apex = fetch(apex_base)
    apex_body = apex["body"].decode("utf-8", "replace")
    record("deploy root serves the pointer page",
           apex.get("status") == 200 and "/charter/" in apex_body,
           f"status {apex.get('status')}")
    record("deploy root is not a directory listing", "Index of /" not in apex_body,
           "directory listing served" if "Index of /" in apex_body else "not a listing")

    # 7. Internal files must not be reachable, from either level.
    for internal in INTERNAL:
        for candidate in (base + internal, apex_base + internal):
            r = fetch(candidate)
            record(f"internal file not served: {candidate[len(apex_base):]}",
                   r.get("status") in (403, 404), f"status {r.get('status')}")

    passed = not findings

    # PRODUCTION APPROVAL is stricter than "every check passed". It is what
    # record_publication.py requires, and it is withheld from any run that was
    # not against the frozen release at the canonical address over HTTPS.
    canonical = manifest["canonical_uri"]
    blockers = []
    if rehearsal:
        blockers.append("rehearsal over plain HTTP")
    if frozen is None:
        blockers.append("the local release is not frozen")
    if drift:
        blockers.append(drift)
    if base != canonical:
        blockers.append(f"verified {base}, canonical address is {canonical}")
    if not passed:
        blockers.append(f"{len(findings)} check(s) failed")
    approval = not blockers

    out = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "base": base,
        "canonical_uri": canonical,
        "rehearsal": rehearsal,
        "release": release_name,
        "release_frozen": frozen is not None and not drift,
        "release_sequence": (frozen or {}).get("sequence"),
        "release_date": (frozen or {}).get("release_date"),
        "manifest_sha256": local_manifest_sha,
        "served_manifest_sha256": served_manifest_sha,
        "builder": manifest["builder"],
        "passed": passed,
        "production_approval": approval,
        "approval_blockers": blockers,
        "checks_not_exercised": not_exercised,
        "checks": checks,
        "findings": findings,
        "served": served,
        "bound": ("REHEARSAL over plain HTTP. Not evidence about the canonical venue. "
                  if rehearsal else "")
                 + "This verifies that what is served now matches the frozen manifest. "
                   "It does not establish continuity: that requires the acceptance "
                   "suite's accepted baseline and repeated observation over time.",
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = out["verified_at"].replace(":", "").replace("-", "")[:15]
    path = os.path.join(OUT_DIR, f"live_verification_{stamp}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)

    for c in checks:
        print(f"  {'PASS' if c['passed'] else 'FAIL'}  {c['check']:<58} {c['detail']}")
    print(f"\n  {len([c for c in checks if c['passed']])}/{len(checks)} checks passed")
    if not_exercised:
        print("  NOT EXERCISED by this run, and therefore not evidence about the "
              "canonical venue:")
        for n in not_exercised:
            print(f"    - {n}")
    print(f"  PRODUCTION APPROVAL: {'GRANTED' if approval else 'WITHHELD'}")
    for b in blockers:
        print(f"    - {b}")
    print(f"  evidence -> {os.path.relpath(path, HERE)}")
    if not passed:
        print("\n  DO NOT ARCHIVE. Archival would capture a record that does not match "
              "the manifest.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
