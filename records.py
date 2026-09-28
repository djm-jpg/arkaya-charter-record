"""The namespace registry: every record the publication pipeline carries, named once.

WHY THIS EXISTS. Until 28 September 2026 the pipeline carried one record, the
Charter, and its path, ledgers and snapshot location were written into each
script. A second record added beside it would have had to borrow those, or copy
them under a new name, and either way a disclosure could end up inside a Charter
index, manifest or ledger, or the Charter could be rebuilt on the way past. The
registry names each record once, with its own path, its own ledgers and its own
snapshot location, and every script reads it from here.

A NAMESPACE IS ONE RECORD. It has its own index.json, index.html, manifest.json
and manifest.json.sha256, its own first-publication ledger, its own index ledger
and its own snapshot location. Nothing is shared between namespaces except the
deploy root, and the pointer page at the deploy root is part of neither record.

Two modes, and why there are only two:

    carried   Copied verbatim from a published release, then proved byte for
              byte against the published manifest digest registered here, before
              promotion and again after it. Never rebuilt: a rebuild changes
              index.json (as_of, sequence) and so publishes a different record
              under the same name. The Charter is carried.

    built     Built by build_release.py from inputs whose digests are registered
              below. The disclosure record is built.

THE CHARTER IS REQUIRED. No release may be built, packaged, verified or recorded
without the carried Charter, and no release may alter it. A Charter change needs
its own separately authorised procedure, which this pipeline does not implement;
asking for one is refused by name (stage CHARTER_CHANGE).

THE SINGLE PLACE WHERE THE DISCLOSURE CARRIER IS REGISTERED is the block between
the BEGIN and END DISCLOSURE REGISTRATION markers below. It ships holding a
placeholder, and the builder REFUSES to build from a placeholder (stage
REGISTRY), so an unregistered input cannot be built and therefore cannot be
packaged, verified or published. At freeze, the operator replaces the
placeholder with the carrier's record slug, title, and for each version its
source file name, SHA-256, byte count and document date. The test suite
registers a synthetic TEST INPUT the same way, in a private sandbox copy of this
file, and never here.
"""

import hashlib
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# The deploy root. Each namespace is served beneath it at /<path>/.
CANONICAL_ROOT = "https://record.arkayarisk.com/"

# The marker a synthetic test input carries in its bytes. A file carrying it is
# refused by the builder unless the run explicitly allows test inputs, and a
# release built from one is marked and can never be granted production approval.
TEST_INPUT_MARKER = b"ARKAYA-TEST-INPUT"

UNREGISTERED = "UNREGISTERED"

CHARTER = {
    "name": "charter",
    "path": "charter",
    "mode": "carried",
    "title": "Arkaya Schema Independence Charter",
    "canonical_uri": CANONICAL_ROOT + "charter/",
    # Where the carried bytes come from, and what they must hash to. The digest
    # is the published manifest of sequence 1, 16 September 2026, recorded in
    # published_indexes.json and snapshotted in publications/1/.
    "carried_from_release": "publish",
    "published_sequence": 1,
    "published_manifest_sha256":
        "b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6",
    "published_index_sha256":
        "8f5fc27deb886815f2394d83d7b676616a473549b79651c1b70fc79d061c848a",
    "published_manifest_snapshot": "publications/1/manifest.json",
    # The Charter's ledgers and snapshots stay exactly where they were. A
    # multi-namespace publication never writes to any of them.
    "first_publication_ledger": "first_publication.json",
    "index_ledger": "published_indexes.json",
    "snapshots": "publications",
}

DISCLOSURES = {
    "name": "disclosures",
    "path": "disclosures",
    "mode": "built",
    "title": "Arkaya governance disclosure record",
    "canonical_uri": CANONICAL_ROOT + "disclosures/",
    "inputs": "inputs/disclosures",
    "mime_type": "text/markdown",
    "first_publication_ledger": "ledgers/disclosures/first_publication.json",
    "index_ledger": "ledgers/disclosures/published_indexes.json",
    "snapshots": "ledgers/disclosures/publications",
}

# Order is deploy order and pointer-page order.
NAMESPACES = (CHARTER, DISCLOSURES)

# A release without every one of these is refused at build, package, live
# verification and recording.
REQUIRED = ("charter",)


# BEGIN DISCLOSURE REGISTRATION
# The single place the disclosure carrier is registered. Placeholder until
# freeze: the builder refuses every UNREGISTERED value and every missing byte
# count, so nothing can be built from this block as shipped.
DISCLOSURE_REGISTRATION = {
    "record_slug": UNREGISTERED,
    "title": UNREGISTERED,
    "entries": [
        {"version": "v1", "src": UNREGISTERED, "sha256": UNREGISTERED, "bytes": None,
         "document_date": UNREGISTERED, "reason": None},
    ],
}
# END DISCLOSURE REGISTRATION


SHA_RE = re.compile(r"^[0-9a-f]{64}$")
VERSION_RE = re.compile(r"^v[1-9][0-9]*$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def namespace(name):
    for ns in NAMESPACES:
        if ns["name"] == name:
            return ns
    return None


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def registry_problems():
    """The registry itself must describe a release that may exist.

    Checked by every script before it relies on the registry, so an edit that
    drops the Charter, marks it built, or points two records at one ledger is a
    refusal rather than a quiet change of meaning.
    """
    problems = []
    names = [ns["name"] for ns in NAMESPACES]
    paths = [ns["path"] for ns in NAMESPACES]
    if len(set(names)) != len(names):
        problems.append("two namespaces share a name")
    if len(set(paths)) != len(paths):
        problems.append("two namespaces share a path")
    for required in REQUIRED:
        ns = namespace(required)
        if ns is None:
            problems.append(f"the registry has no '{required}' namespace. No release may be "
                            f"built without the carried Charter")
        elif ns["mode"] != "carried":
            problems.append(f"the '{required}' namespace is registered as '{ns['mode']}', "
                            f"not 'carried'. The Charter is carried, never rebuilt")
    if len(NAMESPACES) < 2 or all(ns["mode"] == "carried" for ns in NAMESPACES):
        problems.append("the registry names no built namespace; a release carrying only "
                        "the Charter has nothing to publish")
    ledgers = []
    for ns in NAMESPACES:
        if ns["mode"] not in ("carried", "built"):
            problems.append(f"{ns['name']}: unknown mode '{ns['mode']}'")
        if ns["canonical_uri"] != CANONICAL_ROOT + ns["path"] + "/":
            problems.append(f"{ns['name']}: canonical URI is not beneath the canonical root")
        ledgers += [ns["first_publication_ledger"], ns["index_ledger"], ns["snapshots"]]
    if len(set(ledgers)) != len(ledgers):
        problems.append("two namespaces share a ledger or snapshot location")
    return problems


def registration_problems(reg=None):
    """Every reason the disclosure registration cannot be built from.

    The placeholder fails here by design. So does a half-completed registration,
    because a record built from a partly registered carrier would publish a
    digest nobody checked.
    """
    reg = DISCLOSURE_REGISTRATION if reg is None else reg
    problems = []
    slug = reg.get("record_slug")
    if slug == UNREGISTERED or not isinstance(slug, str) or not SLUG_RE.match(slug):
        problems.append(f"record_slug is {slug!r}: not registered")
    title = reg.get("title")
    if title == UNREGISTERED or not isinstance(title, str) or not title.strip():
        problems.append(f"title is {title!r}: not registered")
    entries = reg.get("entries") or []
    if not entries:
        problems.append("no entries are registered")
    seen_versions, seen_src = set(), set()
    for i, e in enumerate(entries):
        where = f"entry {i + 1} ({e.get('version')})"
        v = e.get("version")
        if not isinstance(v, str) or not VERSION_RE.match(v):
            problems.append(f"{where}: version must be v<N>, a whole integer")
        elif v in seen_versions:
            problems.append(f"{where}: version registered twice")
        seen_versions.add(v)
        src = e.get("src")
        if src == UNREGISTERED or not isinstance(src, str) or not src or "/" in src:
            problems.append(f"{where}: source file name is {src!r}: not registered")
        elif src in seen_src:
            problems.append(f"{where}: source registered twice")
        seen_src.add(src)
        digest = e.get("sha256")
        if digest == UNREGISTERED or not isinstance(digest, str) or not SHA_RE.match(digest):
            problems.append(f"{where}: sha256 is {digest!r}: not registered")
        size = e.get("bytes")
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            problems.append(f"{where}: byte count is {size!r}: not registered")
        date = e.get("document_date")
        if date == UNREGISTERED or not isinstance(date, str) or not DATE_RE.match(date):
            problems.append(f"{where}: document_date is {date!r}: not registered")
    return problems


def published_charter_manifest():
    """The Charter manifest as it was published.

    Read from the immutable snapshot, or failing that from the published
    release, and returned only from a file that hashes to the registered digest. Used by
    the live verifier to check served Charter objects against what was
    published, not against whatever a local release claims.
    """
    import json
    candidates = (CHARTER["published_manifest_snapshot"],
                  f"{CHARTER['carried_from_release']}/{CHARTER['path']}/manifest.json")
    for rel in candidates:
        path = os.path.join(HERE, rel)
        if os.path.isfile(path) and sha_file(path) == CHARTER["published_manifest_sha256"]:
            with open(path) as f:
                return json.load(f)
    return None


def charter_record_problems(record_dir):
    """Is this directory byte for byte the published Charter record?

    The published manifest pins the digest and size of every object, and the
    sidecar is determined by the manifest, so a directory whose manifest hashes
    to the registered digest, whose every named object matches it, and which
    holds nothing else, is the published record exactly. Anything less is a
    refusal: there is no tolerance for a byte.
    """
    import json
    problems = []
    if not os.path.isdir(record_dir):
        return ["the release has no charter/ directory. No release may omit the carried "
                "Charter"]
    manifest_path = os.path.join(record_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        return ["charter/manifest.json is missing"]
    got = sha_file(manifest_path)
    want = CHARTER["published_manifest_sha256"]
    if got != want:
        problems.append(f"charter/manifest.json hashes to {got[:16]}…, the published Charter "
                        f"manifest is {want[:16]}…")
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except ValueError as exc:
        return problems + [f"charter/manifest.json is unreadable: {exc}"]
    for o in manifest.get("objects", []):
        p = os.path.join(record_dir, o["path"])
        if not os.path.isfile(p):
            problems.append(f"charter/{o['path']}: named in the published manifest, absent")
            continue
        if sha_file(p) != o["sha256"]:
            problems.append(f"charter/{o['path']}: {sha_file(p)[:16]}… is not the published "
                            f"{o['sha256'][:16]}…")
        elif os.path.getsize(p) != o["bytes"]:
            problems.append(f"charter/{o['path']}: {os.path.getsize(p)} bytes, published "
                            f"{o['bytes']}")
    named = {o["path"] for o in manifest.get("objects", [])} | {"manifest.json",
                                                              "manifest.json.sha256"}
    on_disk = set()
    for dirpath, _, names in os.walk(record_dir):
        for n in names:
            on_disk.add(os.path.relpath(os.path.join(dirpath, n), record_dir))
    for extra in sorted(on_disk - named):
        problems.append(f"charter/{extra}: present but not in the published manifest")
    sidecar = os.path.join(record_dir, "manifest.json.sha256")
    if not os.path.isfile(sidecar):
        problems.append("charter/manifest.json.sha256 is missing")
    else:
        with open(sidecar) as f:
            parts = f.read().split()
        if not parts or parts[0] != got:
            problems.append("charter/manifest.json.sha256 does not match charter/manifest.json")
    index = os.path.join(record_dir, "index.json")
    if os.path.isfile(index) and sha_file(index) != CHARTER["published_index_sha256"]:
        problems.append("charter/index.json is not the published Charter index")
    return problems
