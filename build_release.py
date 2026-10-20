"""Build one multi-namespace release: the Charter CARRIED, the disclosure record BUILT.

WHY A NEW BUILDER, AND NOT AN EDIT TO build_publication_set.py. The published
Charter manifest (sequence 1, 16 September 2026) records the builder that
produced it, `build_publication_set.py`, by SHA-256, and `package.py` checks the
shipped builder against that record. Editing it would leave the repository no
longer holding the builder the published Charter names. It is therefore left
byte-identical, as the Charter's builder of record, and this script builds
every later release.

WHAT A RELEASE IS NOW. A release directory is the whole of what is served:

    <release>/                          <- Netlify publish directory
        index.html                      pointer to every record; part of none
        charter/                        <- CARRIED from publish/charter/, byte for byte
        disclosures/                    <- BUILT here, or CARRIED forward (below)
            index.json index.html manifest.json manifest.json.sha256
            <record-slug>/v<N>/<record-slug>-v<N>.md
        get/                            <- BUILT here, or CARRIED forward (below)
            index.json index.html manifest.json manifest.json.sha256
            <version slug>/<source file name>     bytes exactly as input

The namespaces, their modes, paths and ledgers come from `records.py`.

CARRYING A BUILT RECORD FORWARD (19 October 2026). A built namespace named in
the CARRY REGISTRATION block of `records.py` is not rebuilt: its record is
copied verbatim from the published release named there and proved against the
registered published manifest digest, the namespace's own index ledger, its
immutable snapshot and that release's freeze marker, before promotion and again
after it, exactly as the Charter is. A GET-only release carries the disclosure
record this way; a release with nothing registered as carried builds both.

THE GET SCHEMA RECORD IS OPTIONAL. When records.py registers
GET_REGISTRATION = ABSENT (as it ships), the release has no get/ directory, the
pointer page does not link /get/, and every file of the release except
disclosures/manifest.json and its sidecar is byte-identical to what the builder
at b4e36d3 produced for the same inputs and clock. Those two differ only because
the manifest records the builder's and the registry's source digests, and both
files changed (test_namespaces.TestGetAbsentRegression). Any other value is
validated in full.

Each registered issue is copied from inputs/get/ to
get/<version slug>/<source file name> with its bytes unchanged, and its SHA-256
and byte count are recomputed from the copy against the registration. The
builder never produces /get/1.0 or /get/1.0/: a registration naming version 1.0
is refused by name (GET_PATH), and so is any built path beneath it.

WHY THE CHARTER IS CARRIED AND NEVER REBUILT. A rebuild changes index.json
(as_of, and the sequence if advanced), so the rebuilt Charter is a different
record published under the same name. The Charter is copied verbatim from the
published release, and before promotion the copy is proved against the
published manifest digest registered in `records.py`: the manifest hashes to it,
every object matches it, nothing else is present. The check is repeated after
promotion, before the release is frozen.

Refusals, each with its stage, each before anything is replaced:

    RELEASE_DIR     PVR_RELEASE_DIR unset, publish/ or another published
                    release named, or a directory that is not a release
    FROZEN          the named release is frozen and PVR_REPLACE_RELEASE unset,
                    or is recorded as published and may never be replaced
    REGISTRY        the registry is malformed, a built namespace is not
                    registered (the shipped placeholder), the carry block is
                    malformed, or every built namespace is carried
    CHARTER_CHANGE  a Charter change was requested; no authorised path exists
    CHARTER_CARRY   the carried Charter source is absent or not published
    CHARTER_IDENTITY  any byte of the carried Charter differs from publication
    CARRY           a record registered as carried forward is not the LATEST
                    published release of that record (from its index ledger
                    and the published freeze markers)
    CARRY_IDENTITY  a record registered as carried forward is not, byte for
                    byte, the record its published release published
    GET_PATH        a GET registration or built path would produce /get/1.0
    INPUTS          a registered input absent, altered or unexpected
    TEST_INPUT      a synthetic test input offered without PVR_ALLOW_TEST_INPUT=1
    RELEASE_DATE    as for the Charter builder
    SEQUENCE        a namespace sequence already published, or behind the record
    LEDGER          a ledger that cannot be read

    PVR_RELEASE_DIR=<new release dir> python3 build_release.py

The release directory name is taken from PVR_RELEASE_DIR at execution; nothing
here decides it.
"""

import hashlib
import html
import json
import os
import platform
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _registry_from_source(here):
    """records.py compiled from its SOURCE on every run, never from a bytecode cache.

    Found 19 October 2026: Python reuses a cached records.cpython-*.pyc while the
    source's size and whole-second modification time are unchanged. A
    registration rewritten within one second with a digest of the same length
    (as a test does, and as any scripted edit can) was then read from the stale
    cache: the live verifier compared the served GET bytes with the OLD
    registered digest and passed, while the release recorded the digest of the
    new file. The registry decides what is built, gated, verified and recorded,
    so it is never taken from a cache.
    """
    import types
    path = os.path.join(here, "records.py")
    module = types.ModuleType("records")
    module.__file__ = path
    sys.modules["records"] = module
    with open(path, "rb") as f:
        exec(compile(f.read(), path, "exec"), module.__dict__)
    return module


records = _registry_from_source(HERE)

BUILDER_VERSION = "2026-09-28.1"
BUILDER_SOURCE_PATH = "build_release.py"

RELEASES = os.path.abspath(os.environ.get("PVR_RELEASE_META_DIR", os.path.join(HERE, "releases")))
RELEASE_DIR_ENV = os.environ.get("PVR_RELEASE_DIR", "").strip()
RELEASE_DATE = os.environ.get("PVR_RELEASE_DATE", datetime.now(timezone.utc).date().isoformat())
REPLACE = os.environ.get("PVR_REPLACE_RELEASE") == "1"
ALLOW_DATE_MISMATCH = os.environ.get("PVR_ALLOW_DATE_MISMATCH") == "1"
DATE_MISMATCH_REASON = os.environ.get("PVR_DATE_MISMATCH_REASON", "").strip()
ALLOW_TEST_INPUT = os.environ.get("PVR_ALLOW_TEST_INPUT") == "1"
DISCLOSURE_SEQUENCE = os.environ.get("PVR_DISCLOSURE_SEQUENCE", "").strip()
GET_SEQUENCE = os.environ.get("PVR_GET_SEQUENCE", "").strip()

# Per built namespace: the noun used in refusals, the sequence override, and
# what the registration block is called.
LABEL = {"disclosures": "disclosure", "get": "GET"}
SEQUENCE_OVERRIDE = {"disclosures": DISCLOSURE_SEQUENCE, "get": GET_SEQUENCE}
REGISTRATION_BLOCK = {"disclosures": ("the disclosure carrier", "DISCLOSURE REGISTRATION"),
                      "get": ("the GET schema", "GET REGISTRATION")}

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

DISCLOSURE_AS_OF_CAVEAT = (
    "as_of states the position asserted by this issue of the disclosure record on "
    "that date. It does not warrant the absence of later disclosures that have not "
    "yet been published to this record."
)

DISCLOSURE_NOT_ASSERTED = (
    "Publication records the documentary state of each disclosure and its "
    "publication metadata. It does not validate the substance of any disclosure, "
    "and it does not establish that any control described in a disclosure "
    "operated as described."
)

DISCLOSURE_RETENTION = (
    "Each published disclosure, publication index and associated integrity record "
    "is retained permanently as part of Arkaya's governance record. Recipients may "
    "retain independent copies for evidential and verification purposes."
)

DISCLOSURE_DEFINITIONS = {
    "document_date":
        "The date printed on that issue of the disclosure. A documentary fact about "
        "the document, not a finding about the period it describes.",
    "published_to_record":
        "The date that issue was released to this disclosure record at its canonical "
        "address. No earlier publication date is asserted. Evidence that the record "
        "was reachable at the canonical address on that date, and matched this "
        "manifest, is retained in this record's own publication ledger. This field is "
        "not itself that evidence.",
    "sequence":
        "The revision number of this disclosure record's index. It is this record's "
        "own counter, advances by one whenever an index differing in any published "
        "field is made current, and is never reused for different content.",
}

DISCLOSURE_PROVENANCE_CLAIM = (
    "The manifest records the release builder and its digest, the namespace registry "
    "and its digest, the registered inputs with their digests, and the build "
    "parameters. Matching digests identify the supplied builder and registry and "
    "show that the shipped objects stand in the expected relationship to the "
    "registered inputs. They do not independently prove that this builder "
    "historically executed."
)

GET_AS_OF_CAVEAT = (
    "as_of states the position asserted by this issue of the GET schema record on "
    "that date. It does not warrant the absence of later schema issues that have not "
    "yet been published to this record."
)

GET_NOT_ASSERTED = (
    "Publication records the documentary state of each schema issue and its "
    "publication metadata. It does not ratify any issue, it does not make a draft "
    "normative, and it does not establish that any implementation conforms to it. "
    "Each issue's status is stated as registered, not inferred."
)

GET_RETENTION = (
    "Each published schema issue, publication index and associated integrity record "
    "is retained permanently as part of Arkaya's governance record. Recipients may "
    "retain independent copies for evidential and verification purposes."
)

GET_DEFINITIONS = {
    "version":
        "The version slug of the issue, which is also its path under this record. A "
        "documentary label, not a claim about compatibility with any other issue.",
    "document_date":
        "The date stated for that issue of the schema. A documentary fact about the "
        "document, not a finding about anything it describes.",
    "status":
        "The status of the issue as registered when it was published, for example a "
        "public draft for comment.",
    "published_to_record":
        "The date that issue was released to this record at its canonical address. No "
        "earlier publication date is asserted. Evidence that the record was reachable "
        "at the canonical address on that date, and matched this manifest, is retained "
        "in this record's own publication ledger. This field is not itself that evidence.",
    "sequence":
        "The revision number of this record's index. It is this record's own counter, "
        "advances by one whenever an index differing in any published field is made "
        "current, and is never reused for different content.",
    "content_digest":
        "The SHA-256 of the file exactly as served. Each schema file is served with its "
        "bytes exactly as registered: no newline, encoding or byte-order-mark change.",
}


class BuildError(Exception):
    """Raised before anything is replaced. Carries the stage that refused."""

    def __init__(self, stage, detail):
        self.stage = stage
        super().__init__(f"[{stage}] {detail}")


def digest(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def tree(root):
    out = {}
    for dirpath, _, names in os.walk(root):
        for n in names:
            p = os.path.join(dirpath, n)
            out[os.path.relpath(p, root)] = digest(p)
    return out


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def load_ledger(path):
    """A ledger that cannot be read is not an empty ledger."""
    if not os.path.exists(path):
        return {"versions": {}}
    try:
        with open(path) as f:
            d = json.load(f)
    except (OSError, ValueError) as exc:
        raise BuildError("LEDGER", f"{os.path.relpath(path, HERE)} is unreadable: {exc}")
    if not isinstance(d, dict) or "versions" not in d:
        raise BuildError("LEDGER", f"{os.path.relpath(path, HERE)} has an unexpected shape")
    return d


# ------------------------------------------------------------------ targets

def release_target():
    """The new release directory, its name and its freeze marker.

    publish/ is published and immutable, and so is any release recorded as
    published. The name comes from PVR_RELEASE_DIR at execution. The directory
    must sit beside publish/, because package.py, verify_live.py and
    record_publication.py address releases by name there.
    """
    if not RELEASE_DIR_ENV:
        raise BuildError(
            "RELEASE_DIR",
            "PVR_RELEASE_DIR is not set. A multi-namespace release is built into a NEW "
            "release directory named at execution; publish/ is published and immutable")
    release_dir = os.path.abspath(RELEASE_DIR_ENV)
    name = os.path.basename(release_dir)
    # Compare resolved paths. On macOS the temporary and home trees can be reached
    # through a symbolic link (/var is /private/var), and the working directory is
    # reported resolved while an environment path may not be. Found 28 September
    # 2026 when the full gate failed 54 tests on the operator's Mac and passed on
    # Linux, where /var is not a link. The rule is unchanged: a release lives
    # directly beside this builder.
    if os.path.realpath(os.path.dirname(release_dir)) != os.path.realpath(HERE):
        raise BuildError(
            "RELEASE_DIR",
            f"{release_dir} is not a release directory beside this builder. Releases are "
            f"addressed by name in {HERE}")
    if not NAME_RE.match(name):
        raise BuildError("RELEASE_DIR", f"'{name}' is not a usable release name")
    carried_from = {ns.get("carried_from_release") for ns in records.NAMESPACES}
    if name in carried_from:
        raise BuildError(
            "RELEASE_DIR",
            f"{name}/ is the published release the Charter is carried from. It is "
            f"immutable and may never be rebuilt or replaced; name a new release directory")
    meta_path = os.path.join(RELEASES, f"{name}.json")
    replaced = None
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            replaced = json.load(f)
        if replaced.get("published"):
            raise BuildError("FROZEN", f"{name} is recorded as published and may not be "
                                       f"replaced, by this or any flag")
        if not REPLACE:
            raise BuildError(
                "FROZEN",
                f"{name} already holds a frozen release dated "
                f"{replaced.get('release_date')}. Package that release, or build a new one "
                f"elsewhere. To discard an UNPUBLISHED release deliberately, set "
                f"PVR_REPLACE_RELEASE=1")
        if replaced.get("schema") != "arkaya-release/2":
            raise BuildError("FROZEN", f"{name} holds a release of another kind; it is not "
                                       f"replaced by this builder")
    elif os.path.exists(release_dir):
        raise BuildError("RELEASE_DIR", f"{name}/ exists and is not a frozen release. Name a "
                                        f"new release directory")
    return release_dir, name, meta_path, replaced


def validate_date(built_at_date):
    if RELEASE_DATE == built_at_date:
        return None
    if not ALLOW_DATE_MISMATCH:
        raise BuildError(
            "RELEASE_DATE",
            f"release date {RELEASE_DATE} is not the build date {built_at_date}. The "
            f"release carries this date on its face. To override deliberately, set "
            f"PVR_ALLOW_DATE_MISMATCH=1 AND PVR_DATE_MISMATCH_REASON")
    if not DATE_MISMATCH_REASON:
        raise BuildError(
            "RELEASE_DATE",
            "PVR_ALLOW_DATE_MISMATCH=1 was set without PVR_DATE_MISMATCH_REASON. An "
            "override without a recorded reason is an unexplained discrepancy")
    return DATE_MISMATCH_REASON


def validate_registry():
    problems = records.registry_problems()
    if problems:
        stage = "CHARTER_CHANGE" if any("not 'carried'" in p for p in problems) else "REGISTRY"
        raise BuildError(stage, "the namespace registry cannot describe a release: "
                                + "; ".join(problems))


def refuse_charter_change():
    """The one Charter change path this pipeline has: a refusal, by name.

    A Charter change is a separately authorised act. Until such an authority and
    its procedure exist, a request for one stops the build here rather than
    being quietly ignored, so nobody mistakes a carried Charter for a changed one.
    """
    if os.environ.get("PVR_CHARTER_CHANGE"):
        raise BuildError(
            "CHARTER_CHANGE",
            "a Charter change was requested (PVR_CHARTER_CHANGE). No authorised Charter "
            "change path exists in this pipeline: /charter/ is carried byte-identical from "
            "the published release in every release. A Charter change needs its own "
            "separately authorised procedure. Nothing was built")


# ------------------------------------------------------------------ charter

def validate_charter_source():
    """The carried Charter's source, proved against publication before copying."""
    ns = records.CHARTER
    src_release = ns["carried_from_release"]
    src = os.path.join(HERE, src_release, ns["path"])
    marker_path = os.path.join(HERE, "releases", f"{src_release}.json")
    if not os.path.isdir(src):
        raise BuildError(
            "CHARTER_CARRY",
            f"the carried Charter source {src_release}/{ns['path']}/ is absent. No release "
            f"may be built without the Charter")
    if not os.path.isfile(marker_path):
        raise BuildError("CHARTER_CARRY", f"releases/{src_release}.json is absent; the "
                                          f"carried Charter's publication cannot be shown")
    with open(marker_path) as f:
        marker = json.load(f)
    if not marker.get("published"):
        raise BuildError("CHARTER_CARRY", f"releases/{src_release}.json is not recorded as "
                                          f"published; only a published Charter is carried")
    if marker.get("manifest_sha256") != ns["published_manifest_sha256"]:
        raise BuildError("CHARTER_IDENTITY",
                         f"releases/{src_release}.json records manifest "
                         f"{str(marker.get('manifest_sha256'))[:16]}…, the registered "
                         f"published Charter manifest is "
                         f"{ns['published_manifest_sha256'][:16]}…")
    ledger = load_ledger(os.path.join(HERE, ns["index_ledger"]))
    entry = ledger["versions"].get(str(ns["published_sequence"]))
    if not entry or entry.get("manifest_sha256") != ns["published_manifest_sha256"]:
        raise BuildError("CHARTER_IDENTITY",
                         f"{ns['index_ledger']} does not record sequence "
                         f"{ns['published_sequence']} with the registered Charter manifest")
    problems = records.charter_record_problems(src)
    if problems:
        raise BuildError("CHARTER_IDENTITY",
                         "the carried Charter source is not the published Charter; it is "
                         "carried, never rebuilt or altered, so nothing was built: "
                         + "; ".join(problems))
    return src, marker


def carry_charter(src, dst):
    """Copy verbatim, then prove the copy. Never regenerate."""
    os.makedirs(dst)
    for dirpath, _, names in os.walk(src):
        rel = os.path.relpath(dirpath, src)
        target = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(target, exist_ok=True)
        for n in names:
            shutil.copyfile(os.path.join(dirpath, n), os.path.join(target, n))
    if tree(dst) != tree(src):
        raise BuildError("CHARTER_IDENTITY", "the carried copy differs from its source")
    problems = records.charter_record_problems(dst)
    if problems:
        raise BuildError("CHARTER_IDENTITY", "the carried copy is not the published Charter: "
                                             + "; ".join(problems))


# -------------------------------------------------------------- disclosures

def validate_registration(ns=None):
    ns = ns or records.DISCLOSURES
    if ns["name"] == "get":
        reserved = records.reserved_get_versions()
        if reserved:
            raise BuildError(
                "GET_PATH",
                f"the GET registration names version {', '.join(repr(v) for v in reserved)}. "
                f"/get/1.0 and /get/1.0/ are refused by name: this pipeline never produces "
                f"them. Nothing was built")
    reg = records.registration_for(ns["name"])
    problems = records.registration_problems_for(ns["name"])
    if problems:
        what, block = REGISTRATION_BLOCK[ns["name"]]
        raise BuildError(
            "REGISTRY",
            f"{what} is not registered in records.py (the block between "
            f"BEGIN and END {block}). An unregistered or placeholder input "
            "cannot be built or published"
            + (". A release without the GET record registers GET_REGISTRATION = ABSENT, "
               "nothing else" if ns["name"] == "get" else "")
            + ": " + "; ".join(problems))
    return reg


def validate_carry_registration():
    problems = records.carry_registration_problems()
    if problems:
        raise BuildError("REGISTRY", "the carry registration in records.py cannot be read: "
                                     + "; ".join(problems))


def validate_inputs(ns, reg):
    """Prove the registered inputs before touching any output."""
    label = LABEL[ns["name"]]
    inputs = os.path.join(HERE, ns["inputs"])
    if not os.path.isdir(inputs):
        raise BuildError("INPUTS", f"input directory not found: {ns['inputs']}/")
    expected = {e["src"]: e for e in reg["entries"]}
    found = {f for f in os.listdir(inputs) if not f.startswith(".")}
    missing = sorted(set(expected) - found)
    if missing:
        raise BuildError("INPUTS", f"missing {label} input(s): {', '.join(missing)}")
    unexpected = sorted(found - set(expected))
    if unexpected:
        raise BuildError("INPUTS", f"unexpected {label} input(s): {', '.join(unexpected)}")
    validated, test_input = {}, False
    for name, e in sorted(expected.items()):
        p = os.path.join(inputs, name)
        if not os.path.isfile(p):
            raise BuildError("INPUTS", f"{name} is not a file")
        got_bytes, got_sha = os.path.getsize(p), digest(p)
        if got_bytes != e["bytes"]:
            raise BuildError("INPUTS", f"{name}: registered {e['bytes']} bytes, found {got_bytes}")
        if got_sha != e["sha256"]:
            raise BuildError("INPUTS", f"{name}: registered sha256 {e['sha256']}, found {got_sha}")
        with open(p, "rb") as f:
            if records.TEST_INPUT_MARKER in f.read():
                test_input = True
        validated[name] = {"path": f"{ns['inputs']}/{name}", "sha256": got_sha,
                           "bytes": got_bytes}
    if test_input and not ALLOW_TEST_INPUT:
        raise BuildError(
            "TEST_INPUT",
            f"a {label} input carries the TEST INPUT marker. Synthetic fixtures are for "
            "the test suite only; set PVR_ALLOW_TEST_INPUT=1 to build one in a sandbox. A "
            "release built from one is marked and is never granted production approval")
    return validated, test_input


def namespace_sequence(ns, index_ledger):
    label, override = LABEL[ns["name"]], SEQUENCE_OVERRIDE[ns["name"]]
    recorded = index_ledger.get("versions", {})
    highest = max((int(k) for k in recorded), default=0)
    seq = int(override) if override else highest + 1
    if str(seq) in recorded:
        raise BuildError("SEQUENCE", f"{label} sequence {seq} has already been published. "
                                     f"Published indexes are immutable; advance the sequence")
    if seq <= highest:
        raise BuildError("SEQUENCE", f"{label} sequence {seq} is not above the highest "
                                     f"published {label} sequence {highest}. An index may "
                                     f"not be made current behind the record")
    return seq


def builder_block():
    """The release builder's identity, as every built manifest and the marker record it."""
    return {"script": os.path.basename(__file__), "source_path": BUILDER_SOURCE_PATH,
            "version": BUILDER_VERSION, "sha256": digest(os.path.abspath(__file__))}


def carry_namespace(ns, source, dst):
    """Copy a published built record verbatim, then prove the copy. Never regenerate."""
    src = source["dir"]
    os.makedirs(dst)
    for dirpath, _, names in os.walk(src):
        rel = os.path.relpath(dirpath, src)
        target = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(target, exist_ok=True)
        for n in names:
            shutil.copyfile(os.path.join(dirpath, n), os.path.join(target, n))
    if tree(dst) != tree(src):
        raise BuildError("CARRY_IDENTITY", f"the carried {ns['name']} copy differs from its "
                                           f"source")
    problems = records.carried_record_problems(dst, ns, source["manifest_sha256"],
                                               source["index_sha256"])
    if problems:
        raise BuildError("CARRY_IDENTITY", f"the carried {ns['name']} copy is not the "
                                           f"published record: " + "; ".join(problems))


def render_disclosure_page(idx):
    """index.html, rendered from index.json by this builder and nothing else."""
    e = html.escape
    rows = "\n".join(
        f"""      <tr{' class="current"' if v['is_current'] else ''}>
        <td><a href="{e(v['entry_url'])}">{e(v['version'])}</a></td>
        <td>{e(v['document_date'])}</td>
        <td>{e(v['published_to_record'])}</td>
        <td>{e(v['status'])}{(' &larr; ' + e(v['superseded_by'])) if v.get('superseded_by') else ''}</td>
        <td>{e(v['reason'] or 'first issue')}</td>
        <td class="d"><code>{e(v['content_digest'].split(':', 1)[1])}</code><br><span class="b">{v['bytes']:,} bytes &middot; {e(v['mime_type'])}</span></td>
      </tr>""" for v in idx["entries"])
    return f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Public disclosure record &middot; {e(idx['record'])}</title>
<style>
 :root{{--ink:#12211f;--mut:#5a6b68;--line:#d8e0de;--bg:#fbfcfc;--teal:#0f3d3a;--bronze:#8a6a3b}}
 *{{box-sizing:border-box}}
 body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
 .wrap{{max-width:60rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}}
 h1{{font-size:1.5rem;margin:0 0 .25rem;color:var(--teal)}}
 .sub{{color:var(--mut);margin:0 0 2rem;font-size:.95rem}}
 h2{{font-size:1rem;margin:2.25rem 0 .6rem;color:var(--teal)}}
 table{{width:100%;border-collapse:collapse;font-size:.9rem}}
 th,td{{text-align:left;padding:.6rem .5rem;border-bottom:1px solid var(--line);vertical-align:top}}
 th{{font-weight:600;color:var(--mut);font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}}
 tr.current td{{background:#f2f7f6}}
 code{{font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;word-break:break-all}}
 .b{{color:var(--mut);font-size:.78rem}}
 .d{{max-width:20rem}}
 .note{{border-left:3px solid var(--bronze);padding:.1rem 0 .1rem .9rem;margin:1rem 0;color:var(--mut);font-size:.9rem}}
 dt{{font-weight:600;font-size:.85rem;margin-top:.7rem}}
 dd{{margin:.15rem 0 0;color:var(--mut);font-size:.88rem}}
 a{{color:var(--teal)}}
 footer{{margin-top:3rem;padding-top:1.25rem;border-top:1px solid var(--line);color:var(--mut);font-size:.82rem}}
 @media(max-width:640px){{.d{{max-width:none}}table,thead,tbody,th,td,tr{{display:block}}th{{display:none}}td{{border:0;padding:.2rem .5rem}}tr{{border-bottom:1px solid var(--line);padding:.6rem 0}}}}
</style></head><body><div class="wrap">
<h1>Public disclosure record</h1>
<p class="sub">{e(idx['record'])} &middot; sequence {idx['sequence']} &middot; as of {e(idx['as_of'])}</p>

<div class="note">{e(idx['as_of_caveat'])}</div>

<h2>Disclosures</h2>
<table><thead><tr><th>Version</th><th>Document date</th><th>Published to this record</th><th>Status</th><th>Reason for revision</th><th>SHA-256</th></tr></thead>
<tbody>
{rows}
</tbody></table>

<h2>What the fields mean</h2>
<dl>
{"".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in idx["definitions"].items())}
</dl>

<h2>What this publication does not assert</h2>
<p>{e(idx['not_asserted'])}</p>

<h2>Retention</h2>
<p>{e(idx['retention'])}</p>

<h2>Verification</h2>
<p>The machine-readable index is at <a href="index.json">index.json</a> and the integrity manifest at
<a href="manifest.json">manifest.json</a>. To verify any disclosure, retrieve it and compare its SHA-256
against the digest published above.</p>

<footer>Arkaya Risk &middot; canonical URI <code>{e(idx['canonical_uri'])}</code></footer>
</div></body></html>
"""


def build_disclosures(out, reg, validated, dates, sequence, now, date_reason, test_input):
    """Build the disclosure namespace into `out`. Copies inputs; never regenerates them."""
    ns = records.DISCLOSURES
    base = ns["canonical_uri"]
    slug = reg["record_slug"]
    entries = reg["entries"]
    os.makedirs(out)
    rows = []
    for i, e in enumerate(entries):
        name = f"{slug}-{e['version']}.md"
        rel = f"{slug}/{e['version']}/{name}"
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst))
        shutil.copyfile(os.path.join(HERE, ns["inputs"], e["src"]), dst)
        got = digest(dst)
        if got != e["sha256"]:
            raise BuildError("COPY", f"{name}: copy digest {got} does not match its input")
        is_current = i == len(entries) - 1
        row = {
            "version": e["version"],
            "document_date": e["document_date"],
            "published_to_record": dates[e["version"]],
            "reason": e.get("reason"),
            "predecessor": entries[i - 1]["version"] if i else None,
            "is_current": is_current,
            "status": "current" if is_current else "superseded",
            "entry_url": rel,
            "canonical_uri": base + rel,
            "mime_type": ns["mime_type"],
            "content_digest": "sha256:" + got,
            "bytes": os.path.getsize(dst),
            "source": validated[e["src"]]["path"],
        }
        if not is_current:
            row["superseded_by"] = entries[i + 1]["version"]
        rows.append(row)

    index = {
        "schema": "arkaya-disclosure-record/1",
        "record": reg["title"],
        "record_slug": slug,
        "namespace": ns["path"],
        "canonical_uri": base,
        "as_of": RELEASE_DATE,
        "as_of_caveat": DISCLOSURE_AS_OF_CAVEAT,
        "sequence": sequence,
        "retention": DISCLOSURE_RETENTION,
        "not_asserted": DISCLOSURE_NOT_ASSERTED,
        "definitions": DISCLOSURE_DEFINITIONS,
        "entries": rows,
    }
    index_path = os.path.join(out, "index.json")
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
    index_sha = digest(index_path)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(render_disclosure_page(index))

    def obj(path, mime):
        full = os.path.join(out, path)
        return {"path": path, "canonical_uri": base + path, "mime_type": mime,
                "bytes": os.path.getsize(full), "sha256": digest(full)}

    manifest = {
        "schema": "arkaya-disclosure-manifest/1",
        "record": reg["title"],
        "namespace": ns["path"],
        "as_of": RELEASE_DATE,
        "sequence": sequence,
        "canonical_uri": base,
        "provenance_claim": DISCLOSURE_PROVENANCE_CLAIM,
        "builder": {
            "script": os.path.basename(__file__),
            "source_path": BUILDER_SOURCE_PATH,
            "version": BUILDER_VERSION,
            "sha256": digest(os.path.abspath(__file__)),
        },
        "registry": {"path": "records.py", "sha256": digest(records.__file__)},
        "build_parameters": {
            "built_at": now,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "PVR_RELEASE_DATE": RELEASE_DATE,
            "sequence": sequence,
            "date_mismatch_reason": date_reason,
            "test_input": test_input,
        },
        "inputs": [validated[e["src"]] | {"version": e["version"]} for e in entries],
        "generated": [
            {"path": "index.html", "generated_from": "index.json", "source_sha256": index_sha,
             "sha256": digest(os.path.join(out, "index.html")),
             "relation": "rendered by builder"},
        ],
        "not_bit_reproducible": {
            "paths": ["manifest.json", "manifest.json.sha256"],
            "reason": "the manifest carries built_at and the platform; its sidecar digests "
                      "the manifest",
        },
        "objects": [dict(obj(r["entry_url"], r["mime_type"]), version=r["version"],
                         status=r["status"]) for r in rows]
                   + [obj("index.json", "application/json"), obj("index.html", "text/html")],
    }
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    manifest_sha = digest(os.path.join(out, "manifest.json"))
    with open(os.path.join(out, "manifest.json.sha256"), "w") as f:
        f.write(manifest_sha + "  manifest.json\n")
    return index, manifest, manifest_sha, index_sha


# ---------------------------------------------------------------------- get

def render_get_page(idx):
    """get/index.html, rendered from get/index.json by this builder and nothing else."""
    e = html.escape
    rows = "\n".join(
        f"""      <tr{' class="current"' if v['is_current'] else ''}>
        <td><a href="{e(v['entry_url'])}">{e(v['version'])}</a></td>
        <td>{e(v['document_date'])}</td>
        <td>{e(v['published_to_record'])}</td>
        <td>{e(v['status'])}<br><span class="b">{'current' if v['is_current'] else 'superseded by ' + e(v['superseded_by'])}</span></td>
        <td>{e(v['reason'])}</td>
        <td class="d"><code>{e(v['content_digest'].split(':', 1)[1])}</code><br><span class="b">{v['bytes']:,} bytes &middot; {e(v['mime_type'])}</span></td>
      </tr>""" for v in idx["entries"])
    return f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Public GET schema record &middot; {e(idx['record'])}</title>
<style>
 :root{{--ink:#12211f;--mut:#5a6b68;--line:#d8e0de;--bg:#fbfcfc;--teal:#0f3d3a;--bronze:#8a6a3b}}
 *{{box-sizing:border-box}}
 body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
 .wrap{{max-width:60rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}}
 h1{{font-size:1.5rem;margin:0 0 .25rem;color:var(--teal)}}
 .sub{{color:var(--mut);margin:0 0 2rem;font-size:.95rem}}
 h2{{font-size:1rem;margin:2.25rem 0 .6rem;color:var(--teal)}}
 table{{width:100%;border-collapse:collapse;font-size:.9rem}}
 th,td{{text-align:left;padding:.6rem .5rem;border-bottom:1px solid var(--line);vertical-align:top}}
 th{{font-weight:600;color:var(--mut);font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}}
 tr.current td{{background:#f2f7f6}}
 code{{font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;word-break:break-all}}
 .b{{color:var(--mut);font-size:.78rem}}
 .d{{max-width:20rem}}
 .note{{border-left:3px solid var(--bronze);padding:.1rem 0 .1rem .9rem;margin:1rem 0;color:var(--mut);font-size:.9rem}}
 dt{{font-weight:600;font-size:.85rem;margin-top:.7rem}}
 dd{{margin:.15rem 0 0;color:var(--mut);font-size:.88rem}}
 a{{color:var(--teal)}}
 footer{{margin-top:3rem;padding-top:1.25rem;border-top:1px solid var(--line);color:var(--mut);font-size:.82rem}}
 @media(max-width:640px){{.d{{max-width:none}}table,thead,tbody,th,td,tr{{display:block}}th{{display:none}}td{{border:0;padding:.2rem .5rem}}tr{{border-bottom:1px solid var(--line);padding:.6rem 0}}}}
</style></head><body><div class="wrap">
<h1>Public GET schema record</h1>
<p class="sub">{e(idx['record'])} &middot; sequence {idx['sequence']} &middot; as of {e(idx['as_of'])}</p>

<div class="note">{e(idx['as_of_caveat'])}</div>

<h2>Schema issues</h2>
<table><thead><tr><th>Version</th><th>Document date</th><th>Published to this record</th><th>Status</th><th>Reason</th><th>SHA-256</th></tr></thead>
<tbody>
{rows}
</tbody></table>

<h2>What the fields mean</h2>
<dl>
{"".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in idx["definitions"].items())}
</dl>

<h2>What this publication does not assert</h2>
<p>{e(idx['not_asserted'])}</p>

<h2>Retention</h2>
<p>{e(idx['retention'])}</p>

<h2>Verification</h2>
<p>The machine-readable index is at <a href="index.json">index.json</a> and the integrity manifest at
<a href="manifest.json">manifest.json</a>. To verify any schema issue, retrieve it and compare the SHA-256
of the bytes received against the digest published above.</p>

<footer>Arkaya Risk &middot; canonical URI <code>{e(idx['canonical_uri'])}</code></footer>
</div></body></html>
"""


def build_get(out, reg, validated, dates, sequence, now, date_reason, test_input):
    """Build the GET schema namespace into `out`.

    Each schema file is copied byte for byte from inputs/get/ to
    <version slug>/<source file name>. Nothing reads, parses or re-encodes it,
    so no newline, encoding or byte-order mark changes, and the copy's SHA-256
    and byte count are recomputed against the registration before anything is
    indexed.
    """
    ns = records.GET
    base = ns["canonical_uri"]
    entries = reg["entries"]
    os.makedirs(out)
    rows = []
    for i, e in enumerate(entries):
        rel = f"{e['version']}/{e['src']}"
        if records.get_path_problems([rel]):
            raise BuildError("GET_PATH", "; ".join(records.get_path_problems([rel])))
        src = os.path.join(HERE, ns["inputs"], e["src"])
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst))
        shutil.copyfile(src, dst)
        got, size = digest(dst), os.path.getsize(dst)
        if got != e["sha256"] or size != e["bytes"]:
            raise BuildError("COPY", f"get/{rel}: copy is {size} bytes, sha256 {got}; the "
                                     f"registration is {e['bytes']} bytes, sha256 {e['sha256']}")
        with open(src, "rb") as a, open(dst, "rb") as b:
            if a.read() != b.read():
                raise BuildError("COPY", f"get/{rel}: the served bytes are not the input bytes")
        is_current = i == len(entries) - 1
        row = {
            "version": e["version"],
            "document_date": e["document_date"],
            "published_to_record": dates[e["version"]],
            "status": e["status"],
            "reason": e["reason"],
            "predecessor": entries[i - 1]["version"] if i else None,
            "is_current": is_current,
            "entry_url": rel,
            "canonical_uri": base + rel,
            "mime_type": e["media_type"],
            "content_digest": "sha256:" + got,
            "bytes": size,
            "source": validated[e["src"]]["path"],
        }
        if not is_current:
            row["superseded_by"] = entries[i + 1]["version"]
        rows.append(row)

    index = {
        "schema": "arkaya-get-record/1",
        "record": ns["title"],
        "namespace": ns["path"],
        "canonical_uri": base,
        "as_of": RELEASE_DATE,
        "as_of_caveat": GET_AS_OF_CAVEAT,
        "sequence": sequence,
        "retention": GET_RETENTION,
        "not_asserted": GET_NOT_ASSERTED,
        "definitions": GET_DEFINITIONS,
        "entries": rows,
    }
    index_path = os.path.join(out, "index.json")
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
    index_sha = digest(index_path)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(render_get_page(index))

    def obj(path, mime):
        full = os.path.join(out, path)
        return {"path": path, "canonical_uri": base + path, "mime_type": mime,
                "bytes": os.path.getsize(full), "sha256": digest(full)}

    manifest = {
        "schema": "arkaya-get-manifest/1",
        "record": ns["title"],
        "namespace": ns["path"],
        "as_of": RELEASE_DATE,
        "sequence": sequence,
        "canonical_uri": base,
        "provenance_claim": DISCLOSURE_PROVENANCE_CLAIM,
        "builder": builder_block(),
        "registry": {"path": "records.py", "sha256": digest(records.__file__)},
        "build_parameters": {
            "built_at": now,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "PVR_RELEASE_DATE": RELEASE_DATE,
            "sequence": sequence,
            "date_mismatch_reason": date_reason,
            "test_input": test_input,
        },
        "inputs": [validated[e["src"]] | {"version": e["version"]} for e in entries],
        "generated": [
            {"path": "index.html", "generated_from": "index.json", "source_sha256": index_sha,
             "sha256": digest(os.path.join(out, "index.html")),
             "relation": "rendered by builder"},
        ],
        "not_bit_reproducible": {
            "paths": ["manifest.json", "manifest.json.sha256"],
            "reason": "the manifest carries built_at and the platform; its sidecar digests "
                      "the manifest",
        },
        "objects": [dict(obj(r["entry_url"], r["mime_type"]), version=r["version"],
                         status=r["status"]) for r in rows]
                   + [obj("index.json", "application/json"), obj("index.html", "text/html")],
    }
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    manifest_sha = digest(os.path.join(out, "manifest.json"))
    with open(os.path.join(out, "manifest.json.sha256"), "w") as f:
        f.write(manifest_sha + "  manifest.json\n")
    problems = records.get_path_problems(tree(out))
    if problems:
        raise BuildError("GET_PATH", "; ".join(problems))
    return index, manifest, manifest_sha, index_sha


BUILDERS = {"disclosures": build_disclosures, "get": build_get}


def root_pointer():
    """The deploy root page. It links every record and is part of none."""
    e = html.escape
    items = "\n".join(
        f'<p>The published record for the {e(ns["title"])} is at '
        f'<a href="/{e(ns["path"])}/">/{e(ns["path"])}/</a>.</p>'
        for ns in records.NAMESPACES)
    return f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Arkaya Risk &middot; public records</title>
<style>body{{margin:0;background:#fbfcfc;color:#12211f;font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
.w{{max-width:36rem;margin:0 auto;padding:4rem 1.25rem}}h1{{font-size:1.25rem;color:#0f3d3a;margin:0 0 .5rem}}
p{{color:#5a6b68}}a{{color:#0f3d3a}}</style></head><body><div class="w">
<h1>Arkaya Risk public records</h1>
{items}
<p>This page is a navigation aid. It is not part of any record and asserts nothing about them.</p>
</div></body></html>
"""


# -------------------------------------------------------------------- build

def build():
    now_dt = datetime.now(timezone.utc)
    # 1. Validate everything, before anything is created or replaced.
    refuse_charter_change()
    validate_registry()
    release_dir, name, meta_path, replaced = release_target()
    date_reason = validate_date(now_dt.date().isoformat())
    charter_src, charter_marker = validate_charter_source()
    validate_carry_registration()
    plans, test_input = [], False
    for ns in records.NAMESPACES:
        if ns["mode"] != "built":
            continue
        # Carrying proves historical identity, not the present GET registration.
        if ns["name"] == "get":
            reg = validate_registration(ns)
            validated, ns_test_input = validate_inputs(ns, reg)
            test_input = test_input or ns_test_input
        if ns["name"] in records.CARRY_REGISTRATION:
            # Only the latest published record may be carried: an earlier
            # publication proves byte for byte and would still serve a
            # superseded index. Where nothing is published yet, the identity
            # proof below refuses with its own reasons.
            _, latest = records.latest_published(ns)
            problems = records.latest_carry_problems(ns) if latest is not None else []
            if problems:
                raise BuildError(
                    "CARRY",
                    f"the {ns['name']} record registered as carried forward is not the latest "
                    f"published {ns['name']} record, so nothing was built: "
                    + "; ".join(problems))
            problems, source = records.carried_source_problems(ns)
            if problems:
                raise BuildError(
                    "CARRY_IDENTITY",
                    f"the {ns['name']} record registered as carried forward is not the "
                    f"record its release published; it is carried, never rebuilt or altered, "
                    f"so nothing was built: " + "; ".join(problems))
            if ns["name"] == "get":
                problems = records.get_record_registration_problems(source["dir"])
                if problems:
                    raise BuildError("GET_REGISTRATION", "; ".join(problems))
            plans.append({"ns": ns, "mode": "carried", "source": source})
            continue
        if ns["name"] != "get":
            reg = validate_registration(ns)
            validated, ns_test_input = validate_inputs(ns, reg)
            test_input = test_input or ns_test_input
        first_ledger = load_ledger(os.path.join(HERE, ns["first_publication_ledger"]))
        index_ledger = load_ledger(os.path.join(HERE, ns["index_ledger"]))
        sequence = namespace_sequence(ns, index_ledger)
        dates, newly = {}, []
        for e in reg["entries"]:
            v = e["version"]
            if v in first_ledger["versions"]:
                dates[v] = first_ledger["versions"][v]["first_published"]
            else:
                dates[v] = RELEASE_DATE
                newly.append(v)
        plans.append({"ns": ns, "mode": "built", "reg": reg, "validated": validated,
                      "test_input": ns_test_input, "sequence": sequence, "dates": dates,
                      "newly": newly})
    if not any(p["mode"] == "built" for p in plans):
        raise BuildError("REGISTRY", "every built namespace is registered as carried forward; "
                                     "the release would publish nothing new")
    now = now_dt.isoformat()

    # 2. Build the whole release in staging, beside its destination.
    staging = os.path.join(HERE, f".staging-{name}")
    if os.path.exists(staging):
        shutil.rmtree(staging)
    os.makedirs(staging)
    built = {}
    try:
        carry_charter(charter_src, os.path.join(staging, records.CHARTER["path"]))
        for p in plans:
            out = os.path.join(staging, p["ns"]["path"])
            if p["mode"] == "carried":
                carry_namespace(p["ns"], p["source"], out)
            else:
                built[p["ns"]["name"]] = BUILDERS[p["ns"]["name"]](
                    out, p["reg"], p["validated"], p["dates"], p["sequence"], now,
                    date_reason, p["test_input"])
        with open(os.path.join(staging, "index.html"), "w") as f:
            f.write(root_pointer())
        membership = set(os.listdir(staging))
        expected = {"index.html"} | {n["path"] for n in records.NAMESPACES}
        if membership != expected:
            raise BuildError("LAYOUT", f"the staged release holds {sorted(membership)}, "
                                       f"expected {sorted(expected)}")

        # 3. Promote. Only now does any previous unpublished release go.
        previous = release_dir + ".previous"
        if os.path.exists(previous):
            shutil.rmtree(previous)
        if os.path.exists(release_dir):
            os.rename(release_dir, previous)
        try:
            os.rename(staging, release_dir)
        except BaseException:
            if os.path.exists(previous) and not os.path.exists(release_dir):
                os.rename(previous, release_dir)
            raise
        if os.path.exists(previous):
            shutil.rmtree(previous)
    finally:
        if os.path.exists(staging):
            shutil.rmtree(staging)

    # 4. Prove the Charter, and every record carried forward, again where it now
    #    stands, before freezing.
    problems = records.charter_record_problems(os.path.join(release_dir, "charter"))
    if problems:
        shutil.rmtree(release_dir)
        raise BuildError("CHARTER_IDENTITY", "after promotion the Charter is not the published "
                                             "Charter; the release was removed: "
                                             + "; ".join(problems))
    for p in plans:
        if p["mode"] != "carried":
            continue
        problems = records.carried_record_problems(
            os.path.join(release_dir, p["ns"]["path"]), p["ns"],
            p["source"]["manifest_sha256"], p["source"]["index_sha256"])
        if problems:
            shutil.rmtree(release_dir)
            raise BuildError("CARRY_IDENTITY", f"after promotion the carried {p['ns']['name']} "
                                               f"record is not the published record; the "
                                               f"release was removed: " + "; ".join(problems))

    # 5. Freeze. The marker lives outside the release directory.
    charter_index = os.path.join(release_dir, "charter", "index.json")
    namespaces = {
        "charter": {
            "mode": "carried",
            "path": records.CHARTER["path"],
            "carried_from_release": records.CHARTER["carried_from_release"],
            "sequence": records.CHARTER["published_sequence"],
            "canonical_uri": records.CHARTER["canonical_uri"],
            "manifest_sha256": records.CHARTER["published_manifest_sha256"],
            "index_sha256": digest(charter_index),
            "versions_awaiting_first_publication": [],
        },
    }
    for p in plans:
        ns = p["ns"]
        if p["mode"] == "carried":
            namespaces[ns["name"]] = {
                "mode": "carried",
                "path": ns["path"],
                "carried_from_release": p["source"]["release"],
                "sequence": p["source"]["sequence"],
                "canonical_uri": ns["canonical_uri"],
                "manifest_sha256": p["source"]["manifest_sha256"],
                "index_sha256": p["source"]["index_sha256"],
                "versions_awaiting_first_publication": [],
            }
        else:
            _, manifest, manifest_sha, index_sha = built[ns["name"]]
            namespaces[ns["name"]] = {
                "mode": "built",
                "path": ns["path"],
                "sequence": p["sequence"],
                "canonical_uri": ns["canonical_uri"],
                "manifest_sha256": manifest_sha,
                "index_sha256": index_sha,
                "builder": manifest["builder"],
                "versions_awaiting_first_publication": p["newly"],
            }
    meta = {
        "schema": "arkaya-release/2",
        "release_dir": name,
        "release_date": RELEASE_DATE,
        "built_at": now,
        "canonical_root": records.CANONICAL_ROOT,
        "root_pointer_sha256": digest(os.path.join(release_dir, "index.html")),
        "release_builder": builder_block(),
        "registry_sha256": digest(records.__file__),
        "date_mismatch_reason": date_reason,
        "test_input": test_input,
        "namespaces": namespaces,
        "published": False,
        "state": "frozen release candidate; not deployed, not published",
    }
    save_json(meta_path, meta)
    return meta, release_dir


if __name__ == "__main__":
    try:
        meta, release_dir = build()
    except BuildError as exc:
        print(f"BUILD REFUSED {exc}")
        print("Nothing was deleted or replaced. Any existing release is intact.")
        raise SystemExit(2)
    print(f"release dir    {release_dir}   (publish directory)")
    print(f"release meta   releases/{meta['release_dir']}.json   FROZEN")
    print(f"state          {meta['state']}")
    print(f"release date   {meta['release_date']}")
    if meta["test_input"]:
        print("TEST INPUT     built from a synthetic test input; never publishable")
    for n, d in meta["namespaces"].items():
        print(f"  {n:<12} {d['mode']:<8} sequence {d['sequence']}  "
              f"manifest {d['manifest_sha256'][:16]}…"
              + (f"  from {d['carried_from_release']}/" if d["mode"] == "carried" else ""))
    print(f"  charter carried byte-identical from "
          f"{meta['namespaces']['charter']['carried_from_release']}/charter/; "
          f"no first-publication dates change")
    if records.get_absent():
        print("  get          absent   GET_REGISTRATION = ABSENT; no /get/ record in this "
              "release")
