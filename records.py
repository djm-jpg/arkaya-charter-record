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
deploy root, and the pointer page at the deploy root is part of no record.

Two modes, and why there are only two:

    carried   Copied verbatim from a published release, then proved byte for
              byte against the published manifest digest registered here, before
              promotion and again after it. Never rebuilt: a rebuild changes
              index.json (as_of, sequence) and so publishes a different record
              under the same name. The Charter is carried.

    built     Built by build_release.py from inputs whose digests are registered
              below. The disclosure record and the GET schema record are built.

CARRYING A BUILT RECORD FORWARD (19 October 2026). A built record that an
earlier release published, and that has not changed, need not be rebuilt by a
later release: a rebuild would change its index (as_of, sequence) and publish a
different record under the same name. The block between the BEGIN and END
CARRY REGISTRATION markers names, per built namespace, the published release it
is carried from, the sequence that release published and its published manifest
digest. The builder then copies that release's record verbatim and proves it, as
the Charter is proved: against the registered digest, the namespace's own index
ledger, its immutable snapshot and the published release's freeze marker. The
block ships empty, so every built namespace is built unless the operator
registers a carry at freeze.

THE GET SCHEMA RECORD IS OPTIONAL (19 October 2026, round 2). It is
registered in the block between the BEGIN and END GET REGISTRATION markers, and
that block holds exactly one of two things:

    GET_REGISTRATION = ABSENT     the release has no GET namespace. NAMESPACES
                                  then holds the Charter and the disclosure
                                  record only: no /get/ output is built, the
                                  gate, the live verifier and the recorder
                                  require no GET check, and a release builds
                                  byte for byte as it did before GET existed.
                                  This is how the block ships.

    GET_REGISTRATION = {"entries": [...]}
                                  the release has a GET namespace, validated in
                                  full: every entry complete, digests matched,
                                  /get/1.0 refused by name.

Nothing else is read as absent. None, an empty mapping, an empty entries list,
the old placeholder entry or a partly completed one are refused (stage
REGISTRY), so "no GET record" is never inferred from a half-filled block. ABSENT
is also refused once the GET record has been published (its ledgers exist): a
published record is carried or rebuilt, never dropped. Each issue is served at
/get/<version slug>/<source file name>, its bytes exactly as input. The builder
refuses, by name, any registration that would produce /get/1.0 or /get/1.0/,
and the live verifier checks that the venue does not serve /get/1.0 or /get/1.0/
whether or not the release has a GET namespace.

THE CHARTER IS REQUIRED. No release may be built, packaged, verified or recorded
without the carried Charter, and no release may alter it. A Charter change needs
its own separately authorised procedure, which this pipeline does not implement;
asking for one is refused by name (stage CHARTER_CHANGE).

THE SINGLE PLACE WHERE THE DISCLOSURE CARRIER IS REGISTERED is the block between
the BEGIN and END DISCLOSURE REGISTRATION markers below. It shipped as a
placeholder until the first freeze (28 September 2026). It now holds the
carrier's record slug and title and the published v3 and v4 entries, registered
at the freezes of publish-002 and publish-003. A further issue is appended at
its own freeze: source file name, SHA-256, byte count, document date and
reason. The builder REFUSES a placeholder or a partly completed entry (stage
REGISTRY), so an unregistered input cannot be built and therefore cannot be
packaged, verified or published. The test suite registers a synthetic TEST
INPUT the same way, in a private sandbox copy of this file, and never here.
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

# The one value that declares an optional namespace absent from a release. It is
# not a placeholder: a placeholder (UNREGISTERED) is refused, ABSENT is a
# decision. Only the GET namespace is optional.
ABSENT = "ABSENT"

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

GET = {
    "name": "get",
    "path": "get",
    "mode": "built",
    "title": "Arkaya Governance Evidence Taxonomy (GET) schema",
    "canonical_uri": CANONICAL_ROOT + "get/",
    "inputs": "inputs/get",
    "mime_type": "application/schema+json",
    "first_publication_ledger": "ledgers/get/first_publication.json",
    "index_ledger": "ledgers/get/published_indexes.json",
    "snapshots": "ledgers/get/publications",
}

# Every namespace the pipeline knows, in deploy order and pointer-page order.
# NAMESPACES, the ones a release built from this registry carries, is derived
# from it below the GET REGISTRATION block: GET is left out when, and only when,
# GET_REGISTRATION is ABSENT.
ALL_NAMESPACES = (CHARTER, DISCLOSURES, GET)

# Namespaces a release may lack, each only by registering ABSENT.
OPTIONAL = ("get",)

# A release without every one of these is refused at build, package, live
# verification and recording.
REQUIRED = ("charter",)


# BEGIN DISCLOSURE REGISTRATION
# The single place the disclosure carrier is registered. Holds the published v3
# and v4 entries; a new issue is appended at its freeze. The builder refuses
# every UNREGISTERED value and every missing byte count, so a placeholder or a
# partly completed entry is never built.
DISCLOSURE_REGISTRATION = {
    "record_slug": "conflicted-decisions",
    "title": "Founding-period schema decisions taken in concurrent capacities",
    "entries": [
        {"version": "v3", "src": "conflicted-decisions-v3.md",
         "sha256": "10400912d65cf1bfd584322874d7f178949d209f0157072908be872076926c64",
         "bytes": 28593, "document_date": "2026-09-28", "reason": None},
        {"version": "v4", "src": "conflicted-decisions-v4.md",
         "sha256": "27e0f46a33025cd16e4375d965d79f1ddd5e12c63d9b0ffe3d4e321f875c39ec",
         "bytes": 23173, "document_date": "2026-10-15",
         "reason": "Successor issue: discloses decisions taken since v3 and the disclosure misses since. v3's entries are not repeated; v3 remains published and unchanged."},
        {"version": "v5", "src": "conflicted-decisions-v5.md",
         "sha256": "a4362e1e9fa0ea481f3340d54a9f840dbdf7b4efcab6fef79b5413f0e5a0d1fa",
         "bytes": 16336, "document_date": "2026-10-19",
         "reason": "Successor issue: discloses decisions taken since v4, two corrections to v4 and one disclosure-queue lapse. v3's and v4's entries are not repeated and are not superseded; v3 and v4 remain published and unchanged."},
    ],
}
# END DISCLOSURE REGISTRATION


# BEGIN GET REGISTRATION
# The single place a GET schema issue is registered. Ships as ABSENT: releases
# built from this registry have no GET namespace. To publish the GET record,
# replace ABSENT with {"entries": [...]}, each entry holding the version slug
# (the path segment under /get/), the source file name in inputs/get/, its
# SHA-256 and byte count, the document date, the media type, the status string
# and the reason for the issue. Any value other than ABSENT or a complete
# registration (None, {}, {"entries": []}, an UNREGISTERED placeholder entry, a
# partly completed entry) is refused at REGISTRY.
GET_REGISTRATION = {"entries": [
    {"version": "1.0.1-public-draft-v6", "src": "Arkaya_GET_Schema_v6.json",
     "sha256": "c1e1d4f74a5f892d09766235a474046f95f06c5f39f308b81336259ce79c8ae5",
     "bytes": 28325, "document_date": "2026-10-13", "media_type": "application/schema+json",
     "status": "Public draft for comment, 21 days from publication; not approved; not a candidate. The current candidate is editorial revision v5 (normative version 1.0). Published by Arkaya Risk Limited for Arkaya Risk (Holdings) Limited as Temporary Custodian of the Governance Evidence Taxonomy and Founding Assessor, with the author's written permission.",
     "reason": 'Correction-only editorial revision of normative version 1.0, published as a public draft for comment. © David McKibbin 2026. All rights reserved; no licence to implement or redistribute is granted by this publication. Ownership is intended to pass to Arkaya Risk (Holdings) Ltd and thereafter to an independent custodian under the Schema Independence Charter; a licence will accompany the ratified release.'},
]}
# END GET REGISTRATION


def get_absent():
    """True when, and only when, the GET registration is exactly ABSENT."""
    return isinstance(GET_REGISTRATION, str) and GET_REGISTRATION == ABSENT


# The namespaces a release built from this registry carries.
NAMESPACES = tuple(ns for ns in ALL_NAMESPACES
                   if not (ns["name"] == "get" and get_absent()))


# BEGIN CARRY REGISTRATION
# Built namespaces carried forward byte for byte from the release that published
# them, instead of being rebuilt. Empty as shipped: every built namespace is
# built. An entry, keyed by namespace name, is
#   {"carried_from_release": <published release>, "published_sequence": <int>,
#    "published_manifest_sha256": <that release's published manifest digest>}
CARRY_REGISTRATION = {
    "disclosures": {"carried_from_release": "publish-005", "published_sequence": 3,
                    "published_manifest_sha256": "9c0c1777479f867a5562532d508874e656acfb56e6d8a341ce5c546c6c07e2b9"},
}
# END CARRY REGISTRATION


SHA_RE = re.compile(r"^[0-9a-f]{64}$")
VERSION_RE = re.compile(r"^v[1-9][0-9]*$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RELEASE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

# A GET version slug is a dotted number with optional lower-case qualifiers,
# for example 1.0.1-public-draft-v6. It is the path segment under /get/.
GET_VERSION_RE = re.compile(r"^[0-9]+(\.[0-9]+)+(-[a-z0-9]+)*$")
# Paths under /get/ that this pipeline never produces, refused by name.
RESERVED_GET_VERSIONS = ("1.0",)


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
    problems += optional_namespace_problems()
    return problems


def optional_namespace_problems(base=None):
    """An optional namespace is either ABSENT, cleanly, or registered as a mapping.

    ABSENT is refused once the namespace has been published, because a later
    release that dropped it would withdraw a published record from the venue.
    Any other non-mapping value is ambiguous and refused.
    """
    base = HERE if base is None else base
    problems = []
    if get_absent():
        published = [p for p in (GET["first_publication_ledger"], GET["index_ledger"],
                                 GET["snapshots"]) if os.path.exists(os.path.join(base, p))]
        if published:
            problems.append(f"GET_REGISTRATION is ABSENT, but the GET record has been "
                            f"published ({', '.join(published)} exist). A published record "
                            f"is carried forward or rebuilt, never dropped from a release")
        if "get" in (CARRY_REGISTRATION if isinstance(CARRY_REGISTRATION, dict) else {}):
            problems.append("GET_REGISTRATION is ABSENT, but the carry registration names "
                            "'get'. A release without the GET record cannot carry it")
    elif not isinstance(GET_REGISTRATION, dict):
        problems.append(f"GET_REGISTRATION is {GET_REGISTRATION!r}: neither ABSENT nor a "
                        f"registration. Write GET_REGISTRATION = ABSENT for a release without "
                        f"the GET record")
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


def reserved_get_versions(reg=None):
    """Registered GET version slugs that would produce a path refused by name."""
    reg = GET_REGISTRATION if reg is None else reg
    out = []
    if not isinstance(reg, dict) or not isinstance(reg.get("entries"), list):
        return out
    for e in reg["entries"]:
        if not isinstance(e, dict):
            continue
        v = e.get("version")
        if isinstance(v, str) and v.strip().strip("/").strip() in RESERVED_GET_VERSIONS:
            out.append(v)
    return out


def get_path_problems(paths):
    """Any path under /get/ that is, or sits beneath, a reserved path."""
    problems = []
    for p in paths:
        first = p.strip("/").split("/", 1)[0]
        if first in RESERVED_GET_VERSIONS:
            problems.append(f"get/{p}: /get/{first} and /get/{first}/ are never produced "
                            f"by this pipeline")
    return problems


def get_registration_problems(reg=None):
    """Every reason the GET registration cannot be built from.

    The placeholder fails here by design, as the disclosure placeholder does. A
    version slug of 1.0 is refused by name: /get/1.0 and /get/1.0/ are never
    produced.
    """
    reg = GET_REGISTRATION if reg is None else reg
    if isinstance(reg, str) and reg == ABSENT:
        return ["GET_REGISTRATION is ABSENT: the release has no GET record to build"]
    if not isinstance(reg, dict):
        return [f"GET_REGISTRATION is {reg!r}: neither ABSENT nor a registration. Write "
                f"GET_REGISTRATION = ABSENT for a release without the GET record"]
    problems = []
    unknown = sorted(set(reg) - {"entries"})
    if unknown:
        problems.append(f"unknown key(s) {unknown} in the GET registration")
    entries = reg.get("entries")
    if not isinstance(entries, list):
        return problems + [f"entries is {entries!r}: not registered. Write GET_REGISTRATION = "
                           f"ABSENT for a release without the GET record"]
    if not entries:
        problems.append("no entries are registered. An empty registration is not ABSENT; "
                        "write GET_REGISTRATION = ABSENT for a release without the GET record")
    if any(not isinstance(e, dict) for e in entries):
        return problems + ["every entry must be a mapping"]
    reserved = reserved_get_versions(reg)
    seen_versions, seen_src = set(), set()
    for i, e in enumerate(entries):
        where = f"entry {i + 1} ({e.get('version')})"
        v = e.get("version")
        if v in reserved:
            problems.append(f"{where}: version {v!r} is refused by name. /get/1.0 and "
                            f"/get/1.0/ are never produced by this pipeline")
        elif not isinstance(v, str) or not GET_VERSION_RE.match(v):
            problems.append(f"{where}: version slug is {v!r}: not registered")
        elif v in seen_versions:
            problems.append(f"{where}: version registered twice")
        seen_versions.add(v)
        src = e.get("src")
        if (src == UNREGISTERED or not isinstance(src, str) or not src or "/" in src
                or "\\" in src or src.startswith(".")):
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
        if e.get("media_type") != GET["mime_type"]:
            problems.append(f"{where}: media type is {e.get('media_type')!r}, the GET record "
                            f"serves {GET['mime_type']}")
        for field in ("status", "reason"):
            val = e.get(field)
            if val == UNREGISTERED or not isinstance(val, str) or not val.strip():
                problems.append(f"{where}: {field} is {val!r}: not registered")
    return problems


def registration_for(name):
    """The registration block of a built namespace, read when called."""
    return {"disclosures": DISCLOSURE_REGISTRATION, "get": GET_REGISTRATION}.get(name)


def registration_problems_for(name):
    if name == "disclosures":
        return registration_problems()
    if name == "get":
        return get_registration_problems()
    return [f"no registration exists for namespace {name!r}"]


def registered_inputs(name):
    """(input path, sha256, bytes) for every input registered for a built namespace."""
    ns = namespace(name)
    return sorted((f"{ns['inputs']}/{e['src']}", e["sha256"], e["bytes"])
                  for e in registration_for(name)["entries"])


def get_record_registration_problems(record_dir):
    """Prove a carried GET against today's registration as well as publication.

    Historical identity alone cannot validate a changed or incomplete registry.
    This reads the record bytes; it never rebuilds or rewrites a carried record.
    """
    import json
    problems = get_registration_problems()
    if problems:
        return [f"[REGISTRY] GET: {p}" for p in problems]
    paths = [os.path.relpath(os.path.join(d, n), record_dir)
             for d, _, names in os.walk(record_dir) for n in names]
    problems = [f"[GET_PATH] {p}" for p in get_path_problems(paths)]
    try:
        with open(os.path.join(record_dir, "manifest.json")) as f:
            manifest = json.load(f)
        inputs = sorted((i["path"], i["sha256"], i["bytes"])
                        for i in manifest["inputs"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        return problems + [f"[GET_REGISTRATION] cannot read carried GET inputs: {e}"]
    if inputs != registered_inputs("get"):
        problems.append("[GET_REGISTRATION] carried GET manifest inputs differ from the "
                        "present registration")
    for e in GET_REGISTRATION["entries"]:
        rel = f"{e['version']}/{e['src']}"
        path = os.path.join(record_dir, rel)
        if (not os.path.isfile(path) or os.path.getsize(path) != e["bytes"]
                or sha_file(path) != e["sha256"]):
            problems.append(f"[GET_REGISTRATION] get/{rel}: not the registered bytes "
                            f"(sha256 {e['sha256']}, {e['bytes']} bytes)")
    return problems


# ------------------------------------------------------------------ carry

def carry_registration_problems():
    """The carry block must name only built namespaces, each completely."""
    problems = []
    if not isinstance(CARRY_REGISTRATION, dict):
        return ["the carry registration is not a mapping"]
    for name, c in CARRY_REGISTRATION.items():
        ns = namespace(name)
        if ns is None and name in OPTIONAL:
            problems.append(f"carry: {name!r} is registered as ABSENT in this registry; a "
                            f"release without it cannot carry it")
            continue
        if ns is None:
            problems.append(f"carry: {name!r} is not a registered namespace")
            continue
        if ns["mode"] != "built":
            problems.append(f"carry: {name!r} is registered as {ns['mode']}; only a built "
                            f"namespace is carried forward here")
            continue
        rel = (c or {}).get("carried_from_release")
        if not isinstance(rel, str) or not RELEASE_NAME_RE.match(rel) or rel == UNREGISTERED:
            problems.append(f"carry {name}: carried_from_release is {rel!r}: not registered")
        seq = (c or {}).get("published_sequence")
        if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1:
            problems.append(f"carry {name}: published_sequence is {seq!r}: not registered")
        digest = (c or {}).get("published_manifest_sha256")
        if not isinstance(digest, str) or not SHA_RE.match(digest):
            problems.append(f"carry {name}: published_manifest_sha256 is {digest!r}: not "
                            f"registered")
    return problems


def carried_record_problems(record_dir, ns, want_manifest_sha, want_index_sha):
    """Is this directory byte for byte the published record of a carried namespace?

    The same proof the Charter has: the manifest hashes to the published digest,
    every object it names matches, nothing else is present, the sidecar agrees
    and the index is the published index. No tolerance for a byte.
    """
    import json
    where = f"{ns['path']}/"
    if not os.path.isdir(record_dir):
        return [f"the release has no {where} directory to carry"]
    manifest_path = os.path.join(record_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        return [f"{where}manifest.json is missing"]
    problems = []
    got = sha_file(manifest_path)
    if got != want_manifest_sha:
        problems.append(f"{where}manifest.json hashes to {got[:16]}…, the published manifest "
                        f"is {str(want_manifest_sha)[:16]}…")
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except ValueError as exc:
        return problems + [f"{where}manifest.json is unreadable: {exc}"]
    for o in manifest.get("objects", []):
        p = os.path.join(record_dir, o["path"])
        if not os.path.isfile(p):
            problems.append(f"{where}{o['path']}: named in the published manifest, absent")
        elif sha_file(p) != o["sha256"]:
            problems.append(f"{where}{o['path']}: {sha_file(p)[:16]}… is not the published "
                            f"{o['sha256'][:16]}…")
        elif os.path.getsize(p) != o["bytes"]:
            problems.append(f"{where}{o['path']}: {os.path.getsize(p)} bytes, published "
                            f"{o['bytes']}")
    named = {o["path"] for o in manifest.get("objects", [])} | {"manifest.json",
                                                              "manifest.json.sha256"}
    on_disk = set()
    for dirpath, _, names in os.walk(record_dir):
        for n in names:
            on_disk.add(os.path.relpath(os.path.join(dirpath, n), record_dir))
    for extra in sorted(on_disk - named):
        problems.append(f"{where}{extra}: present but not in the published manifest")
    sidecar = os.path.join(record_dir, "manifest.json.sha256")
    if not os.path.isfile(sidecar):
        problems.append(f"{where}manifest.json.sha256 is missing")
    else:
        with open(sidecar) as f:
            parts = f.read().split()
        if not parts or parts[0] != got:
            problems.append(f"{where}manifest.json.sha256 does not match {where}manifest.json")
    index = os.path.join(record_dir, "index.json")
    if not os.path.isfile(index) or sha_file(index) != want_index_sha:
        problems.append(f"{where}index.json is not the published index")
    return problems


def carried_source_problems(ns, base=None):
    """Prove a carry registration against publication. Returns (problems, source).

    `source` is {"release", "sequence", "manifest_sha256", "index_sha256", "dir"}
    when the registration can be read. The published manifest digest registered
    here must be the one the carried-from release's freeze marker records as
    published, the one this namespace's own index ledger records at that
    sequence, and the digest of the immutable snapshot of that sequence; and the
    carried-from release's record must be byte for byte that manifest.
    """
    import json
    base = HERE if base is None else base
    c = CARRY_REGISTRATION.get(ns["name"]) or {}
    rel, seq = c.get("carried_from_release"), c.get("published_sequence")
    want = c.get("published_manifest_sha256")
    problems = []
    marker_path = os.path.join(base, "releases", f"{rel}.json")
    if not os.path.isfile(marker_path):
        return [f"releases/{rel}.json is absent; the carried {ns['name']} record's "
                f"publication cannot be shown"], None
    with open(marker_path) as f:
        marker = json.load(f)
    entry = (marker.get("namespaces") or {}).get(ns["name"]) or {}
    if not marker.get("published"):
        problems.append(f"releases/{rel}.json is not recorded as published; only a published "
                        f"{ns['name']} record is carried")
    if entry.get("manifest_sha256") != want or entry.get("sequence") != seq:
        problems.append(f"releases/{rel}.json does not record {ns['name']} at sequence {seq} "
                        f"with the registered manifest {str(want)[:16]}…")
    ledger_path = os.path.join(base, ns["index_ledger"])
    ledger = {}
    if os.path.isfile(ledger_path):
        with open(ledger_path) as f:
            ledger = json.load(f)
    led = (ledger.get("versions") or {}).get(str(seq)) or {}
    if led.get("manifest_sha256") != want:
        problems.append(f"{ns['index_ledger']} does not record sequence {seq} with the "
                        f"registered manifest {str(want)[:16]}…")
    index_sha = led.get("index_sha256")
    if entry.get("index_sha256") != index_sha:
        problems.append(f"releases/{rel}.json and {ns['index_ledger']} disagree on the "
                        f"published {ns['name']} index")
    snap = os.path.join(base, ns["snapshots"], str(seq), "manifest.json")
    if not os.path.isfile(snap) or sha_file(snap) != want:
        problems.append(f"{ns['snapshots']}/{seq}/manifest.json is absent or does not hash to "
                        f"the registered manifest")
    src = os.path.join(base, rel, ns["path"])
    problems += [f"{rel}/{p}" for p in carried_record_problems(src, ns, want, index_sha)]
    return problems, {"release": rel, "sequence": seq, "manifest_sha256": want,
                      "index_sha256": index_sha, "dir": src}


def latest_published(ns, base=None):
    """The latest published release of a built namespace, from the repository's own records.

    Returns (problems, latest). `latest` is {"release", "sequence",
    "manifest_sha256", "index_sha256", "dir"} for the highest sequence in the
    namespace's own index ledger, the release recorded there as publishing it.
    That release's freeze marker must be marked published and record the same
    sequence, manifest and index, and no published freeze marker in releases/
    may record the namespace built at a higher sequence than the ledger holds
    (a ledger behind publication is refused, not guessed around). Nothing here
    names a release: the answer comes from the ledger and the markers.
    """
    import glob
    import json
    base = HERE if base is None else base
    name = ns["name"]
    ledger_path = os.path.join(base, ns["index_ledger"])
    if not os.path.isfile(ledger_path):
        return [f"{ns['index_ledger']} is absent: no {name} record has been published, so "
                f"there is nothing to carry"], None
    with open(ledger_path) as f:
        versions = json.load(f).get("versions") or {}
    if not versions:
        return [f"{ns['index_ledger']} records no published {name} sequence"], None
    highest = max(int(k) for k in versions)
    led = versions[str(highest)]
    latest = {"release": led.get("release"), "sequence": highest,
              "manifest_sha256": led.get("manifest_sha256"),
              "index_sha256": led.get("index_sha256"),
              "dir": os.path.join(base, str(led.get("release")), ns["path"])}
    problems = []
    for marker_path in sorted(glob.glob(os.path.join(base, "releases", "*.json"))):
        with open(marker_path) as f:
            marker = json.load(f)
        entry = (marker.get("namespaces") or {}).get(name) or {}
        if (marker.get("published") and entry.get("mode", "built") == "built"
                and isinstance(entry.get("sequence"), int) and entry["sequence"] > highest):
            problems.append(f"releases/{os.path.basename(marker_path)} is published with {name} "
                            f"sequence {entry['sequence']}, above the highest sequence "
                            f"{highest} in {ns['index_ledger']}; the ledger is behind publication")
    rel = latest["release"]
    marker_path = os.path.join(base, "releases", f"{rel}.json")
    if not isinstance(rel, str) or not RELEASE_NAME_RE.match(rel):
        problems.append(f"{ns['index_ledger']} sequence {highest} names no release")
    elif not os.path.isfile(marker_path):
        problems.append(f"releases/{rel}.json, the release {ns['index_ledger']} records as "
                        f"publishing {name} sequence {highest}, is absent")
    else:
        with open(marker_path) as f:
            marker = json.load(f)
        entry = (marker.get("namespaces") or {}).get(name) or {}
        if (not marker.get("published") or entry.get("sequence") != highest
                or entry.get("manifest_sha256") != latest["manifest_sha256"]
                or entry.get("index_sha256") != latest["index_sha256"]):
            problems.append(f"releases/{rel}.json does not record {name} published at sequence "
                            f"{highest} with the manifest and index in {ns['index_ledger']}")
    return problems, latest


def latest_carry_problems(ns, base=None):
    """A carried built namespace must be carried from its LATEST published release.

    An earlier published release is itself proved byte for byte, so without
    this check a carry entry left pointing at it would serve a superseded index
    and silently withdraw every later issue from the venue.
    """
    problems, latest = latest_published(ns, base)
    if latest is None:
        return problems
    c = CARRY_REGISTRATION.get(ns["name"]) or {}
    got = (c.get("carried_from_release"), c.get("published_sequence"),
           c.get("published_manifest_sha256"))
    want = (latest["release"], latest["sequence"], latest["manifest_sha256"])
    if got != want:
        problems.append(f"the carry entry names {ns['name']} from {got[0]} at sequence {got[1]} "
                        f"with manifest {str(got[2])[:16]}…; the latest published {ns['name']} "
                        f"release is {want[0]} at sequence {want[1]} with manifest "
                        f"{str(want[2])[:16]}…. Only the latest published record is carried")
    return problems


def latest_index_problems(ns, record_dir, base=None):
    """The index a release carries must be the latest published index, byte for byte."""
    problems, latest = latest_published(ns, base)
    if latest is None:
        return problems
    index = os.path.join(record_dir, "index.json")
    source = os.path.join(latest["dir"], "index.json")
    if not os.path.isfile(index):
        return problems + [f"{ns['path']}/index.json is missing"]
    got = sha_file(index)
    if got != latest["index_sha256"]:
        problems.append(f"{ns['path']}/index.json hashes to {got[:16]}…, the latest published "
                        f"{ns['name']} index ({latest['release']}, sequence "
                        f"{latest['sequence']}) is {str(latest['index_sha256'])[:16]}…")
    elif not os.path.isfile(source):
        problems.append(f"{latest['release']}/{ns['path']}/index.json, the latest published "
                        f"{ns['name']} index, is absent")
    else:
        with open(index, "rb") as a, open(source, "rb") as b:
            if a.read() != b.read():
                problems.append(f"{ns['path']}/index.json is not byte for byte "
                                f"{latest['release']}/{ns['path']}/index.json")
    return problems


def carried_namespace_problems(ns, record_dir, marker_entry, base=None):
    """A carried namespace in a release: the source proved, the copy proved, the marker true."""
    problems, source = carried_source_problems(ns, base)
    if source is None:
        return problems
    m = marker_entry or {}
    if (m.get("mode") != "carried" or m.get("carried_from_release") != source["release"]
            or m.get("sequence") != source["sequence"]
            or m.get("manifest_sha256") != source["manifest_sha256"]
            or m.get("index_sha256") != source["index_sha256"]
            or m.get("versions_awaiting_first_publication")):
        problems.append(f"the freeze marker does not record {ns['name']} as carried from "
                        f"{source['release']} at its published sequence, manifest and index")
    problems += carried_record_problems(record_dir, ns, source["manifest_sha256"],
                                        source["index_sha256"])
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
