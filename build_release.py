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
        index.html                      pointer to both records; part of neither
        charter/                        <- CARRIED from publish/charter/, byte for byte
        disclosures/                    <- BUILT here
            index.json index.html manifest.json manifest.json.sha256
            <record-slug>/v<N>/<record-slug>-v<N>.md

The namespaces, their modes, paths and ledgers come from `records.py`.

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
    REGISTRY        the registry is malformed, or the disclosure carrier is not
                    registered (the shipped placeholder)
    CHARTER_CHANGE  a Charter change was requested; no authorised path exists
    CHARTER_CARRY   the carried Charter source is absent or not published
    CHARTER_IDENTITY  any byte of the carried Charter differs from publication
    INPUTS          a disclosure input absent, altered or unexpected
    TEST_INPUT      a synthetic test input offered without PVR_ALLOW_TEST_INPUT=1
    RELEASE_DATE    as for the Charter builder
    SEQUENCE        a disclosure sequence already published, or behind the record
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
import records  # noqa: E402

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
    if os.path.dirname(release_dir) != HERE:
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

def validate_registration():
    reg = records.DISCLOSURE_REGISTRATION
    problems = records.registration_problems(reg)
    if problems:
        raise BuildError(
            "REGISTRY",
            "the disclosure carrier is not registered in records.py (the block between "
            "BEGIN and END DISCLOSURE REGISTRATION). An unregistered or placeholder input "
            "cannot be built or published: " + "; ".join(problems))
    return reg


def validate_disclosure_inputs(reg):
    """Prove the registered inputs before touching any output."""
    ns = records.DISCLOSURES
    inputs = os.path.join(HERE, ns["inputs"])
    if not os.path.isdir(inputs):
        raise BuildError("INPUTS", f"input directory not found: {ns['inputs']}/")
    expected = {e["src"]: e for e in reg["entries"]}
    found = {f for f in os.listdir(inputs) if not f.startswith(".")}
    missing = sorted(set(expected) - found)
    if missing:
        raise BuildError("INPUTS", f"missing disclosure input(s): {', '.join(missing)}")
    unexpected = sorted(found - set(expected))
    if unexpected:
        raise BuildError("INPUTS", f"unexpected disclosure input(s): {', '.join(unexpected)}")
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
            "a disclosure input carries the TEST INPUT marker. Synthetic fixtures are for "
            "the test suite only; set PVR_ALLOW_TEST_INPUT=1 to build one in a sandbox. A "
            "release built from one is marked and is never granted production approval")
    return validated, test_input


def disclosure_sequence(index_ledger):
    recorded = index_ledger.get("versions", {})
    highest = max((int(k) for k in recorded), default=0)
    seq = int(DISCLOSURE_SEQUENCE) if DISCLOSURE_SEQUENCE else highest + 1
    if str(seq) in recorded:
        raise BuildError("SEQUENCE", f"disclosure sequence {seq} has already been published. "
                                     f"Published indexes are immutable; advance the sequence")
    if seq <= highest:
        raise BuildError("SEQUENCE", f"disclosure sequence {seq} is not above the highest "
                                     f"published disclosure sequence {highest}. An index may "
                                     f"not be made current behind the record")
    return seq


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
    reg = validate_registration()
    validated, test_input = validate_disclosure_inputs(reg)
    ns = records.DISCLOSURES
    first_ledger = load_ledger(os.path.join(HERE, ns["first_publication_ledger"]))
    index_ledger = load_ledger(os.path.join(HERE, ns["index_ledger"]))
    sequence = disclosure_sequence(index_ledger)
    dates, newly = {}, []
    for e in reg["entries"]:
        v = e["version"]
        if v in first_ledger["versions"]:
            dates[v] = first_ledger["versions"][v]["first_published"]
        else:
            dates[v] = RELEASE_DATE
            newly.append(v)
    now = now_dt.isoformat()

    # 2. Build the whole release in staging, beside its destination.
    staging = os.path.join(HERE, f".staging-{name}")
    if os.path.exists(staging):
        shutil.rmtree(staging)
    os.makedirs(staging)
    try:
        carry_charter(charter_src, os.path.join(staging, records.CHARTER["path"]))
        d_index, d_manifest, d_manifest_sha, d_index_sha = build_disclosures(
            os.path.join(staging, ns["path"]), reg, validated, dates, sequence, now,
            date_reason, test_input)
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

    # 4. Prove the Charter again where it now stands, before freezing.
    problems = records.charter_record_problems(os.path.join(release_dir, "charter"))
    if problems:
        shutil.rmtree(release_dir)
        raise BuildError("CHARTER_IDENTITY", "after promotion the Charter is not the published "
                                             "Charter; the release was removed: "
                                             + "; ".join(problems))

    # 5. Freeze. The marker lives outside the release directory.
    charter_index = os.path.join(release_dir, "charter", "index.json")
    meta = {
        "schema": "arkaya-release/2",
        "release_dir": name,
        "release_date": RELEASE_DATE,
        "built_at": now,
        "canonical_root": records.CANONICAL_ROOT,
        "root_pointer_sha256": digest(os.path.join(release_dir, "index.html")),
        "release_builder": d_manifest["builder"],
        "registry_sha256": d_manifest["registry"]["sha256"],
        "date_mismatch_reason": date_reason,
        "test_input": test_input,
        "namespaces": {
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
            "disclosures": {
                "mode": "built",
                "path": ns["path"],
                "sequence": sequence,
                "canonical_uri": ns["canonical_uri"],
                "manifest_sha256": d_manifest_sha,
                "index_sha256": d_index_sha,
                "builder": d_manifest["builder"],
                "versions_awaiting_first_publication": newly,
            },
        },
        "published": False,
        "state": "frozen release candidate; not deployed, not published",
    }
    save_json(meta_path, meta)
    return meta, d_index, d_manifest, release_dir


if __name__ == "__main__":
    try:
        meta, idx, man, release_dir = build()
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
              f"manifest {d['manifest_sha256'][:16]}…")
    print(f"  charter carried byte-identical from "
          f"{meta['namespaces']['charter']['carried_from_release']}/charter/; "
          f"no first-publication dates change")
