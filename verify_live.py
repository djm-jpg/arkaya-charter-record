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

MULTIPLE RECORDS, 28 September 2026. A release built by `build_release.py` carries
more than one record (see `records.py`): the Charter, carried byte-identical from
the published release, and the disclosure record. Such a release is recognised
by its freeze marker and verified from the deploy root:

    python3 verify_live.py --release=<release name>              # https://record.arkayarisk.com/
    python3 verify_live.py --release=<release name> https://host/

Each namespace is verified against ITS OWN frozen manifest with every check the
Charter has always had: transport, landing page body, served manifest fetched
and hashed, sidecar against the served and the frozen manifest, every object's
digest, size and content type, a control path that must 404, and internal files
not served. The deploy root must link every record. And the Charter has an
identity check of its own, in both modes: the served Charter manifest must hash
to the PUBLISHED digest registered in `records.py`, and every served Charter
object must be the published object. A venue with the Charter absent or altered,
or with any namespace failing, is not approved.
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
sys.path.insert(0, HERE)
import records  # noqa: E402

# Where evidence is written. The override exists so the multi-namespace tests do
# not leave rehearsal evidence in the working tree; the default is unchanged.
OUT_DIR = os.path.abspath(os.environ.get("PVR_LIVE_OUT_DIR",
                                         os.path.join(HERE, "verification", "live")))

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


def internal_paths(release_name):
    """Every internal file that must not be reachable, for this release.

    The original list, plus the release builder, the registry, every namespace's
    own ledgers, and this release's freeze marker.
    """
    extra = ["build_release.py", "records.py", f"releases/{release_name}.json"]
    for ns in records.NAMESPACES:
        extra += [ns["first_publication_ledger"], ns["index_ledger"]]
    out = []
    for p in list(INTERNAL) + extra:
        if p not in out:
            out.append(p)
    return out


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


class Checks:
    """Every check a run makes, in order, and the findings among them."""

    def __init__(self):
        self.checks, self.findings = [], []

    def record(self, name, ok, detail):
        self.checks.append({"check": name, "passed": bool(ok), "detail": detail})
        if not ok:
            self.findings.append(f"{name}: {detail}")

    def failed_with_prefix(self, prefix):
        return [f for f in self.findings if f.startswith(prefix)]


def check_transport(chk, base, prefix, rehearsal, not_exercised):
    """HTTPS, the redirect destination and HSTS. Returns the landing response.

    A record served over plain HTTP, or downgraded on redirect, is not the
    record its manifest describes.
    """
    root = fetch(base)
    if not rehearsal:
        chk.record(f"{prefix}https reachable",
                   root.get("status") == 200 and root["final_url"].startswith("https://"),
                   root.get("error") or f"status {root.get('status')}, final URL {root['final_url']}")

        plain = fetch("http://" + base[len("https://"):])
        # Destination equality, not merely "ends up on https somewhere".
        chk.record(f"{prefix}http redirects to the same https address",
                   plain.get("status") == 200 and plain["final_url"] == base,
                   plain.get("error") or f"status {plain.get('status')}, "
                                         f"final URL {plain['final_url']}, expected {base}")

        hsts = root["headers"].get("Strict-Transport-Security")
        chk.record(f"{prefix}strict-transport-security present", bool(hsts),
                   hsts or "header absent")
    else:
        not_exercised += [f"{prefix}https reachable",
                          f"{prefix}http redirects to the same https address",
                          f"{prefix}strict-transport-security present"]
        chk.record(f"{prefix}index reachable", root.get("status") == 200,
                   root.get("error") or f"status {root.get('status')}")
    return root


def verify_record(chk, base, prefix, root, manifest, local_manifest_sha, index_html_sha):
    """One record against its own frozen manifest. Returns (served, served manifest sha).

    The same checks for every record, the Charter's own since DM's finding 3.
    """
    # 2. THE LANDING PAGE ITSELF. The address people visit must serve the page
    #    that was built, not merely something with a 200 status.
    if root.get("status") == 200:
        served_root_sha = hashlib.sha256(root["body"]).hexdigest()
        chk.record(f"{prefix}landing page body matches index.html",
                   served_root_sha == index_html_sha,
                   f"expected {index_html_sha[:16]}… served {served_root_sha[:16]}…")
        rtype = (root["headers"].get("Content-Type") or "").split(";")[0].strip()
        chk.record(f"{prefix}landing page content-type", rtype == "text/html",
                   f"expected text/html, served {rtype or 'none'}")
    else:
        chk.record(f"{prefix}landing page body matches index.html", False,
                   f"landing page not retrieved: status {root.get('status')}")

    # 3. THE SERVED MANIFEST. It is not in `objects` because it cannot contain
    #    its own digest, which is exactly why it went unfetched. A venue serving
    #    a wrong manifest with a consistent sidecar passed the previous version.
    man = fetch(base + "manifest.json")
    served_manifest_sha = None
    if man.get("status") == 200:
        served_manifest_sha = hashlib.sha256(man["body"]).hexdigest()
        chk.record(f"{prefix}served manifest matches the frozen manifest",
                   served_manifest_sha == local_manifest_sha,
                   f"frozen {local_manifest_sha[:16]}… served {served_manifest_sha[:16]}…")
    else:
        chk.record(f"{prefix}served manifest matches the frozen manifest", False,
                   man.get("error") or f"HTTP {man.get('status')}")

    side = fetch(base + "manifest.json.sha256")
    if side.get("status") == 200 and side["body"].split():
        recorded = side["body"].decode("utf-8", "replace").split()[0]
        chk.record(f"{prefix}served sidecar matches the served manifest",
                   served_manifest_sha is not None and recorded == served_manifest_sha,
                   f"sidecar {recorded[:16]}… served manifest "
                   f"{(served_manifest_sha or 'not-retrieved')[:16]}…")
        chk.record(f"{prefix}served sidecar matches the frozen manifest",
                   recorded == local_manifest_sha,
                   f"sidecar {recorded[:16]}… frozen {local_manifest_sha[:16]}…")
    else:
        chk.record(f"{prefix}served sidecar matches the served manifest", False,
                   f"HTTP {side.get('status')}")
        chk.record(f"{prefix}served sidecar matches the frozen manifest", False,
                   f"HTTP {side.get('status')}")

    # 4. Every object the manifest names, at its canonical path, byte for byte.
    served = {}
    for o in manifest["objects"]:
        r = fetch(base + o["path"])
        if r.get("error") or r["status"] != 200:
            chk.record(f"{prefix}served {o['path']}", False, r.get("error") or f"HTTP {r['status']}")
            continue
        got = hashlib.sha256(r["body"]).hexdigest()
        ctype = (r["headers"].get("Content-Type") or "").split(";")[0].strip()
        served[o["path"]] = {"sha256": got, "bytes": len(r["body"]),
                             "content_type": ctype, "status": 200,
                             "cache_control": r["headers"].get("Cache-Control"),
                             "etag": r["headers"].get("ETag"),
                             "last_modified": r["headers"].get("Last-Modified")}
        chk.record(f"{prefix}digest {o['path']}", got == o["sha256"],
                   f"manifest {o['sha256'][:16]}… served {got[:16]}…")
        chk.record(f"{prefix}bytes {o['path']}", len(r["body"]) == o["bytes"],
                   f"manifest {o['bytes']} served {len(r['body'])}")
        want = EXPECTED_TYPE.get(o["mime_type"])
        chk.record(f"{prefix}content-type {o['path']}", ctype == want,
                   f"expected {want}, served {ctype or 'none'}")

    # 5. A path that must NOT exist. A host answering everything with a generic
    #    page makes every retrieval check meaningless.
    control = fetch(base + "definitely-not-here")
    chk.record(f"{prefix}control path 404s", control.get("status") == 404,
               f"status {control.get('status')}")
    return served, served_manifest_sha


def verify_charter_identity(chk, base, served, local_manifest_sha, served_manifest_sha):
    """Is the Charter being served the Charter that was published?

    Checked against the digest registered in `records.py` and the published
    manifest's own snapshot, not against the local release, so a release that
    altered the Charter consistently (objects, manifest, sidecar and marker all
    rewritten to agree) still fails here.
    """
    want = records.CHARTER["published_manifest_sha256"]
    published = records.published_charter_manifest()
    chk.record("charter identity: the published Charter manifest snapshot is available",
               published is not None,
               f"{records.CHARTER['published_manifest_snapshot']} "
               + ("hashes to the registered digest" if published is not None
                  else "is absent or does not hash to the registered digest"))
    chk.record("charter identity: local Charter manifest is the published manifest",
               local_manifest_sha == want,
               f"published {want[:16]}… local {str(local_manifest_sha)[:16]}…")
    chk.record("charter identity: served Charter manifest is the published manifest",
               served_manifest_sha == want,
               f"published {want[:16]}… served {str(served_manifest_sha or 'not-retrieved')[:16]}…")
    wrong = []
    for o in (published or {}).get("objects", []):
        got = served.get(o["path"])
        if got is None:
            r = fetch(base + o["path"])
            if r.get("error") or r["status"] != 200:
                wrong.append(f"{o['path']} not served")
                continue
            got = {"sha256": hashlib.sha256(r["body"]).hexdigest(), "bytes": len(r["body"])}
        if got["sha256"] != o["sha256"] or got["bytes"] != o["bytes"]:
            wrong.append(f"{o['path']} is not the published object")
    chk.record("charter identity: every served Charter object is the published object",
               published is not None and not wrong,
               "; ".join(wrong) if wrong else
               ("all published objects served unchanged" if published is not None
                else "no published manifest to compare against"))
    return published is not None and not wrong and local_manifest_sha == want \
        and served_manifest_sha == want


def check_internal(chk, bases, apex_base, release_name):
    """Internal files must not be reachable, from any level."""
    for internal in internal_paths(release_name):
        for b in bases:
            candidate = b + internal
            r = fetch(candidate)
            chk.record(f"internal file not served: {candidate[len(apex_base):]}",
                       r.get("status") in (403, 404), f"status {r.get('status')}")


def write_evidence(out, chk, not_exercised, blockers, approval):
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = out["verified_at"].replace(":", "").replace("-", "")[:15]
    path = os.path.join(OUT_DIR, f"live_verification_{stamp}.json")
    # Two runs within one second must not overwrite each other's evidence.
    n = 1
    while os.path.exists(path):
        n += 1
        path = os.path.join(OUT_DIR, f"live_verification_{stamp}_{n}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)

    for c in chk.checks:
        print(f"  {'PASS' if c['passed'] else 'FAIL'}  {c['check']:<58} {c['detail']}")
    print(f"\n  {len([c for c in chk.checks if c['passed']])}/{len(chk.checks)} checks passed")
    if not_exercised:
        print("  NOT EXERCISED by this run, and therefore not evidence about the "
              "canonical venue:")
        for n_ in not_exercised:
            print(f"    - {n_}")
    print(f"  PRODUCTION APPROVAL: {'GRANTED' if approval else 'WITHHELD'}")
    for b in blockers:
        print(f"    - {b}")
    try:
        shown = os.path.relpath(path, HERE)
    except ValueError:
        shown = path
    print(f"  evidence -> {shown}")
    if chk.findings:
        print("\n  DO NOT ARCHIVE. Archival would capture a record that does not match "
              "the manifest.")


BOUND = ("This verifies that what is served now matches the frozen manifest. "
         "It does not establish continuity: that requires the acceptance "
         "suite's accepted baseline and repeated observation over time.")


def main_single(argv, release_name, args):
    """One record, the Charter, verified from /charter/. The original interface."""
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

    chk, not_exercised = Checks(), []

    # 0. What this run is verifying against.
    chk.record("local release is frozen", frozen is not None and not drift,
               drift or (f"frozen release, sequence {frozen['sequence']}, manifest "
                         f"{local_manifest_sha[:16]}…" if frozen else
                         "no freeze marker: exploratory run against an unfrozen directory"))

    # 1. Transport.
    root = check_transport(chk, base, "", rehearsal, not_exercised)

    # 2 to 5. The record against its frozen manifest.
    served, served_manifest_sha = verify_record(chk, base, "", root, manifest,
                                                local_manifest_sha, index_html_sha)

    # 5a. The Charter against its PUBLICATION, not only against the local release.
    identity = verify_charter_identity(chk, base, served, local_manifest_sha,
                                       served_manifest_sha)

    # 6. The deploy root serves the pointer, not a directory listing.
    apex_base = base.rsplit("/charter/", 1)[0] + "/"
    apex = fetch(apex_base)
    apex_body = apex["body"].decode("utf-8", "replace")
    chk.record("deploy root serves the pointer page",
               apex.get("status") == 200 and "/charter/" in apex_body,
               f"status {apex.get('status')}")
    chk.record("deploy root is not a directory listing", "Index of /" not in apex_body,
               "directory listing served" if "Index of /" in apex_body else "not a listing")

    # 7. Internal files must not be reachable, from either level.
    check_internal(chk, (base, apex_base), apex_base, release_name)

    passed = not chk.findings

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
    if not identity:
        blockers.append("the Charter is absent or altered: what is served or held is not "
                        "the published Charter")
    if not passed:
        blockers.append(f"{len(chk.findings)} check(s) failed")
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
        "charter_identity": {
            "published_manifest_sha256": records.CHARTER["published_manifest_sha256"],
            "passed": identity,
        },
        "builder": manifest["builder"],
        "passed": passed,
        "production_approval": approval,
        "approval_blockers": blockers,
        "checks_not_exercised": not_exercised,
        "checks": chk.checks,
        "findings": chk.findings,
        "served": served,
        "bound": ("REHEARSAL over plain HTTP. Not evidence about the canonical venue. "
                  if rehearsal else "") + BOUND,
    }
    write_evidence(out, chk, not_exercised, blockers, approval)
    return 0 if passed else 1


def load_namespace(release_name, ns):
    """The local frozen record for one namespace, or None if the release lacks it."""
    record = os.path.join(HERE, release_name, ns["path"])
    manifest_path = os.path.join(record, "manifest.json")
    index_path = os.path.join(record, "index.html")
    if not (os.path.isfile(manifest_path) and os.path.isfile(index_path)):
        return None
    with open(manifest_path, "rb") as f:
        raw = f.read()
    try:
        manifest = json.loads(raw)
    except ValueError:
        return None
    with open(index_path, "rb") as f:
        index_html_sha = hashlib.sha256(f.read()).hexdigest()
    return manifest, hashlib.sha256(raw).hexdigest(), index_html_sha


def main_multi(argv, release_name, args, meta):
    """Every record in a multi-namespace release, each against its own manifest."""
    base = (args[0] if args else records.CANONICAL_ROOT)
    if not base.endswith("/"):
        base += "/"
    for ns in records.NAMESPACES:
        if base.endswith("/" + ns["path"] + "/"):
            print(f"REFUSED: release {release_name} carries more than one record and is "
                  f"verified from the deploy root, not from /{ns['path']}/.")
            return 2

    rehearsal = os.environ.get("PVR_ALLOW_PLAIN_HTTP") == "1"
    if not base.startswith("https://") and not rehearsal:
        print("REFUSED: the canonical venue must be verified over HTTPS.")
        return 2

    chk, not_exercised = Checks(), []
    blockers = []

    reg_problems = records.registry_problems()
    chk.record("registry describes a valid release", not reg_problems,
               "; ".join(reg_problems) or f"{len(records.NAMESPACES)} namespaces, Charter carried")

    # 0. What this run is verifying against: every namespace frozen and undrifted.
    marker_ns = meta.get("namespaces") or {}
    local, drift = {}, []
    for ns in records.NAMESPACES:
        loaded = load_namespace(release_name, ns)
        local[ns["name"]] = loaded
        recorded = (marker_ns.get(ns["name"]) or {}).get("manifest_sha256")
        if loaded is None:
            drift.append(f"{ns['name']}: the release holds no {ns['path']}/ record")
        elif recorded != loaded[1]:
            drift.append(f"{ns['name']}: the release directory no longer matches its freeze "
                         f"marker ({loaded[1][:16]}… vs {str(recorded)[:16]}…)")
    chk.record("local release is frozen", not drift,
               "; ".join(drift) or f"frozen release {release_name}, "
                                   f"{len(records.NAMESPACES)} namespaces, dated "
                                   f"{meta.get('release_date')}")
    carries_charter = local.get("charter") is not None and "charter" in marker_ns
    chk.record("the release carries the Charter", carries_charter,
               "charter/ present and frozen" if carries_charter else
               "the release has no Charter. No release may omit the carried Charter")

    # 1. The deploy root: transport, and the pointer linking every record.
    apex = check_transport(chk, base, "[root] ", rehearsal, not_exercised)
    apex_body = apex["body"].decode("utf-8", "replace")
    unlinked = [ns["path"] for ns in records.NAMESPACES if f"/{ns['path']}/" not in apex_body]
    chk.record("deploy root serves the pointer page linking every record",
               apex.get("status") == 200 and not unlinked,
               f"status {apex.get('status')}"
               + (f"; no link to {', '.join('/' + u + '/' for u in unlinked)}" if unlinked else
                  f"; links {', '.join('/' + n['path'] + '/' for n in records.NAMESPACES)}"))
    chk.record("deploy root is not a directory listing", "Index of /" not in apex_body,
               "directory listing served" if "Index of /" in apex_body else "not a listing")
    served_pointer_sha = hashlib.sha256(apex["body"]).hexdigest() if apex.get("status") == 200 \
        else None
    chk.record("deploy root page matches the frozen pointer",
               served_pointer_sha == meta.get("root_pointer_sha256"),
               f"frozen {str(meta.get('root_pointer_sha256'))[:16]}… served "
               f"{str(served_pointer_sha or 'not-retrieved')[:16]}…")

    # 2 to 5, per namespace, each against its own frozen manifest.
    evidence_ns, served_all, bases = {}, {}, [base]
    identity = False
    for ns in records.NAMESPACES:
        name, prefix = ns["name"], f"[{ns['name']}] "
        ns_base = base + ns["path"] + "/"
        bases.append(ns_base)
        loaded = local[name]
        root = check_transport(chk, ns_base, prefix, rehearsal, not_exercised)
        if loaded is None:
            chk.record(f"{prefix}record present in the frozen release", False,
                       f"{release_name}/{ns['path']}/ has no manifest or index")
            served, served_manifest_sha, local_sha = {}, None, None
        else:
            manifest, local_sha, index_html_sha = loaded
            served, served_manifest_sha = verify_record(chk, ns_base, prefix, root, manifest,
                                                        local_sha, index_html_sha)
            if manifest.get("canonical_uri") != ns["canonical_uri"]:
                blockers.append(f"{name}: the frozen manifest names "
                                f"{manifest.get('canonical_uri')}, the registry {ns['canonical_uri']}")
        if name == "charter":
            identity = verify_charter_identity(chk, ns_base, served, local_sha,
                                               served_manifest_sha)
        served_all[name] = served
        evidence_ns[name] = {
            "mode": ns["mode"],
            "base": ns_base,
            "canonical_uri": ns["canonical_uri"],
            "sequence": (marker_ns.get(name) or {}).get("sequence"),
            "manifest_sha256": local_sha,
            "served_manifest_sha256": served_manifest_sha,
        }

    # 7. Internal files must not be reachable, from any level.
    check_internal(chk, bases, base, release_name)

    for ns in records.NAMESPACES:
        failed = chk.failed_with_prefix(f"[{ns['name']}] ")
        if ns["name"] == "charter":
            failed += [f for f in chk.findings if f.startswith("charter identity")]
        evidence_ns[ns["name"]]["passed"] = not failed
        evidence_ns[ns["name"]]["findings"] = failed

    passed = not chk.findings

    canonical = meta.get("canonical_root") or records.CANONICAL_ROOT
    if rehearsal:
        blockers.insert(0, "rehearsal over plain HTTP")
    if drift:
        blockers += drift
    if canonical != records.CANONICAL_ROOT:
        blockers.append(f"the freeze marker names canonical root {canonical}, the registry "
                        f"{records.CANONICAL_ROOT}")
    if base != records.CANONICAL_ROOT:
        blockers.append(f"verified {base}, canonical address is {records.CANONICAL_ROOT}")
    if reg_problems:
        blockers.append("the namespace registry cannot describe a release")
    if not carries_charter:
        blockers.append("the release does not carry the Charter")
    if not identity:
        blockers.append("the Charter is absent or altered: what is served or held is not "
                        "the published Charter")
    for ns in records.NAMESPACES:
        if not evidence_ns[ns["name"]]["passed"]:
            blockers.append(f"namespace {ns['name']} failed "
                            f"{len(evidence_ns[ns['name']]['findings'])} check(s)")
    if meta.get("test_input"):
        blockers.append("the release was built from a TEST INPUT and is never publishable")
    if not passed:
        blockers.append(f"{len(chk.findings)} check(s) failed")
    approval = not blockers

    out = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "base": base,
        "canonical_uri": records.CANONICAL_ROOT,
        "rehearsal": rehearsal,
        "release": release_name,
        "release_schema": meta.get("schema"),
        "release_frozen": not drift,
        "release_date": meta.get("release_date"),
        "test_input": bool(meta.get("test_input")),
        "root_pointer_sha256": meta.get("root_pointer_sha256"),
        "served_root_pointer_sha256": served_pointer_sha,
        "namespaces": evidence_ns,
        "charter_identity": {
            "published_manifest_sha256": records.CHARTER["published_manifest_sha256"],
            "local_manifest_sha256": evidence_ns["charter"]["manifest_sha256"],
            "served_manifest_sha256": evidence_ns["charter"]["served_manifest_sha256"],
            "passed": identity,
        },
        "release_builder": meta.get("release_builder"),
        "passed": passed,
        "production_approval": approval,
        "approval_blockers": blockers,
        "checks_not_exercised": not_exercised,
        "checks": chk.checks,
        "findings": chk.findings,
        "served": served_all,
        "bound": ("REHEARSAL over plain HTTP. Not evidence about the canonical venue. "
                  if rehearsal else "") + BOUND,
    }
    write_evidence(out, chk, not_exercised, blockers, approval)
    return 0 if passed else 1


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    release_name = next((a.split("=", 1)[1] for a in argv if a.startswith("--release=")),
                        "publish")
    meta_path = os.path.join(HERE, "releases", f"{release_name}.json")
    if os.path.isfile(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        if meta.get("schema") == "arkaya-release/2":
            return main_multi(argv, release_name, args, meta)
    return main_single(argv, release_name, args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
