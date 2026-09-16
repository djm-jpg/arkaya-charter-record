"""Build one Charter publication release. Build it once; package that exact output.

Canonical venue is record.arkayarisk.com, Arkaya-controlled. The repository is an
independent provenance and verification layer, NOT the canonical venue. This
script builds the identical object set for both.

WHAT THIS SCRIPT DOES NOT DO, and why.

It does not record publication. DM's finding 5 of 16 September 2026: the previous
version wrote first-publication dates and marked the set "published" at build
time, before Netlify, DNS or any live observation, so a failed or delayed
deployment left a false publication record behind. Publication is now recorded by
`record_publication.py`, only against live evidence from the canonical address.
Nothing this script writes claims the set was published, and no field in the
served bytes narrates its own deployment status.

It does not rebuild over a frozen release. DM's finding 1: `package.py` used to
rebuild before packaging, which changed `as_of` and made the packaged set a
different set from the one that was built and checked. A release is now built
once into `PVR_RELEASE_DIR`, frozen, and packaged as it stands. Rebuild
reproducibility is tested by building into a SEPARATE directory and comparing.

    python3 build_publication_set.py                    # release into publish/
    PVR_RELEASE_DIR=/tmp/rebuild python3 build_publication_set.py

Deploy layout. The release directory is the whole of what is served:

    <release>/                      <- Netlify publish directory
        index.html                  pointer to the record; not part of the record
        charter/                    <- the record
            index.json index.html manifest.json manifest.json.sha256 README.md
            v1/charter-v1.pdf  v1.1/charter-v1.1.pdf
            v2/charter-v2.pdf  v3/charter-v3.pdf

Release metadata and the freeze marker live in `releases/<name>.json`, OUTSIDE the
release directory, so nothing internal is ever served.

Three build disciplines, each of which exists because its absence was a defect:

1.  The inputs are held in `inputs/` with their digests recorded here in code and
    validated BEFORE anything is deleted. A build that cannot prove its inputs
    does not get to destroy the previous output.
2.  The set is built into a staging directory and moved into place only when it
    is complete.
3.  The PDFs are copied, never regenerated. Regeneration would change the bytes
    and so the digest for the same document.
"""

import hashlib
import json
import os
import platform
import shutil
import sys
import tempfile
from datetime import datetime, timezone

BUILDER_VERSION = "2026-09-16.4"

# Where this script lives in the tagged repository. The repository mirrors this
# package's layout exactly, so the builder runs from a clone without path edits.
# DM's finding 6: the previous layout moved scripts into `tools/` without
# adapting their path assumptions.
BUILDER_SOURCE_PATH = "build_publication_set.py"

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "inputs")
LEDGER = os.path.join(HERE, "first_publication.json")
INDEX_LEDGER = os.path.join(HERE, "published_indexes.json")
# Freeze markers live here. A scratch build — the reproducibility comparison, for
# instance — points this at its own temporary directory, so it never writes a
# marker into the package. The first cut did, the marker was packaged, and on a
# fresh extraction the comparison build refused against its own leftover.
RELEASES = os.path.abspath(os.environ.get("PVR_RELEASE_META_DIR", os.path.join(HERE, "releases")))

RELEASE_DIR = os.path.abspath(os.environ.get("PVR_RELEASE_DIR", os.path.join(HERE, "publish")))
RELEASE_NAME = os.path.basename(RELEASE_DIR)
RELEASE_META = os.path.join(RELEASES, f"{RELEASE_NAME}.json")
OUT = os.path.join(RELEASE_DIR, "charter")
STAGING = os.path.join(RELEASE_DIR, ".staging-charter")

CANONICAL_BASE = os.environ.get("PVR_CANONICAL_BASE", "https://record.arkayarisk.com/charter")
RELEASE_DATE = os.environ.get("PVR_RELEASE_DATE",
                              datetime.now(timezone.utc).date().isoformat())
SEQUENCE = int(os.environ.get("PVR_SEQUENCE", "1"))
REPLACE = os.environ.get("PVR_REPLACE_RELEASE") == "1"

# DATE CONTROL, and the override stated honestly.
#
# The release date must be the day the release is built, because it is the date
# the set will carry on its face. The override exists, so the rule is stated with
# it rather than as an unconditional refusal that the code then contradicts
# (DM's finding 5). Using the override requires a reason, and the reason is
# written into the release metadata, the manifest and the production record.
ALLOW_DATE_MISMATCH = os.environ.get("PVR_ALLOW_DATE_MISMATCH") == "1"
DATE_MISMATCH_REASON = os.environ.get("PVR_DATE_MISMATCH_REASON", "").strip()

# Digests of the four filed Charter issues. This map, not the directory listing,
# is what the build treats as authoritative: an input that is absent, altered or
# unexpected stops the build before any output is touched.
EXPECTED_INPUTS = {
    "charter-v1.pdf":   ("03794ff916330d36e551ccb0d98a173c5205e98c27eb35124a7466eedc776e6e", 137752),
    "charter-v1.1.pdf": ("2d55ac0b81e07fee580e4784126c2d581b7acaec70ee55f84f5f0bec1bac0897", 145462),
    "charter-v2.pdf":   ("1df3e103e94515c5fbaf8792c5f09f4b539cd919ed65d7d3892d3001fc1ca12b", 151068),
    "charter-v3.pdf":   ("751972efbfa4fb6070b6c9b36f289211937cfcf97724511743a1e1251d752ba5", 154947),
}

AS_OF_CAVEAT = (
    "as_of states the position asserted by this issue of the record on that date. "
    "It does not warrant the absence of subsequent events that have not yet been "
    "published to this record."
)

RETENTION = (
    "Each published Charter issue, publication index and associated integrity "
    "record is retained permanently as part of Arkaya's governance record. "
    "Publication expressly permits recipients to retain independent copies for "
    "evidential and verification purposes."
)

NOT_ASSERTED = (
    "Publication records the documentary state and the publication metadata. It "
    "does not validate, cure or establish the historical effectiveness of any "
    "amendment to this instrument."
)

DEFINITIONS = {
    "instrument_date":
        "The date printed on the face of that issue of the instrument. A "
        "documentary fact about the document, not a finding about when it took "
        "effect.",
    "published_to_record":
        "The date that issue was released to this record at the canonical "
        "address. It is not a claim that the issue was unpublished before that "
        "date by other means, and no earlier publication date is asserted for "
        "any version. Evidence that the record was reachable at the canonical "
        "address on that date, and matched this manifest, is retained in "
        "Arkaya's publication log. This field is not itself that evidence.",
    "superseded_by":
        "The next issue in the documentary lineage.",
    "superseded_from":
        "DOCUMENTARY CHRONOLOGY ONLY. The instrument date of the succeeding "
        "issue. It records the order and dating of the documents as they are "
        "written. It is not an assertion that supersession took legal effect on "
        "that date, and nothing in this record establishes that it did.",
    "sequence":
        "The revision number of this publication index. It advances by one "
        "whenever an index differing in any published field is made current. "
        "Every index that has been made current is retained in full, as an "
        "immutable snapshot, and a sequence number is never reused for "
        "different content.",
}

PROVENANCE_CLAIM = (
    "The manifest records the builder, its digest, the inputs with their source "
    "digests, and the build parameters. Matching digests identify the supplied "
    "builder and demonstrate that the shipped objects stand in the expected "
    "relationship to the recorded inputs. They do not independently prove that "
    "this builder historically executed, and they are not a substitute for the "
    "retained build evidence."
)

LINEAGE = [
    dict(version="v1", src="charter-v1.pdf", instrument_date="2026-05-19",
         reason=None, predecessor=None,
         superseded_by="v1.1", superseded_from="2026-05-28"),
    dict(version="v1.1", src="charter-v1.1.pdf", instrument_date="2026-05-28",
         reason="Section 7 updated from date-triggered to milestone-gated handover.",
         predecessor="v1",
         superseded_by="v2", superseded_from="2026-07-29"),
    dict(version="v2", src="charter-v2.pdf", instrument_date="2026-07-29",
         reason="Custodian company named; group implementation licence recorded; "
                "Section 8 instrument supplied; four-layer economic model numbering adopted.",
         predecessor="v1.1",
         superseded_by="v3", superseded_from="2026-07-29"),
    dict(version="v3", src="charter-v3.pdf", instrument_date="2026-07-29",
         reason="Section 7.6 extended with the transition-conflict discipline, the "
                "enforcement statement and the constitutional cross-reference for "
                "custodian governance mechanics.",
         predecessor="v2",
         superseded_by=None, superseded_from=None),
]


class BuildError(Exception):
    """Raised before anything is destroyed. Carries the stage that refused."""

    def __init__(self, stage, detail):
        self.stage = stage
        super().__init__(f"[{stage}] {detail}")


def digest(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


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


def load_ledger(path, empty):
    """A ledger that cannot be read is not an empty ledger."""
    if not os.path.exists(path):
        return dict(empty)
    try:
        with open(path) as f:
            d = json.load(f)
    except (OSError, ValueError) as exc:
        raise BuildError("LEDGER", f"{os.path.basename(path)} is unreadable: {exc}")
    if not isinstance(d, dict) or "versions" not in d:
        raise BuildError("LEDGER", f"{os.path.basename(path)} has an unexpected shape")
    return d


# ---------------------------------------------------------------- validation

def validate_inputs():
    """Prove the inputs before touching any output."""
    if not os.path.isdir(INPUTS):
        raise BuildError("INPUTS", f"input directory not found: {INPUTS}")

    found = {f for f in os.listdir(INPUTS) if f.lower().endswith(".pdf")}
    missing = sorted(set(EXPECTED_INPUTS) - found)
    if missing:
        raise BuildError("INPUTS", f"missing input(s): {', '.join(missing)}")
    unexpected = sorted(found - set(EXPECTED_INPUTS))
    if unexpected:
        raise BuildError("INPUTS", f"unexpected input(s): {', '.join(unexpected)}")

    validated = {}
    for name, (want_sha, want_bytes) in sorted(EXPECTED_INPUTS.items()):
        p = os.path.join(INPUTS, name)
        got_bytes = os.path.getsize(p)
        got_sha = digest(p)
        if got_bytes != want_bytes:
            raise BuildError("INPUTS", f"{name}: expected {want_bytes} bytes, found {got_bytes}")
        if got_sha != want_sha:
            raise BuildError("INPUTS", f"{name}: expected sha256 {want_sha}, found {got_sha}")
        validated[name] = {"path": f"inputs/{name}", "sha256": got_sha, "bytes": got_bytes}
    return validated


def validate_readme_source():
    src = os.path.join(HERE, "README_source.md")
    if not os.path.isfile(src):
        raise BuildError("INPUTS", "README_source.md not found; the built README has no source")
    return src


def validate_date(built_at_date):
    if RELEASE_DATE == built_at_date:
        return None
    if not ALLOW_DATE_MISMATCH:
        raise BuildError(
            "RELEASE_DATE",
            f"release date {RELEASE_DATE} is not the build date {built_at_date}. "
            f"The set carries this date on its face, so build it on the day it "
            f"claims. To override deliberately, set PVR_ALLOW_DATE_MISMATCH=1 AND "
            f"PVR_DATE_MISMATCH_REASON to the reason, which is then recorded in "
            f"the release metadata, the manifest and the production record")
    if not DATE_MISMATCH_REASON:
        raise BuildError(
            "RELEASE_DATE",
            "PVR_ALLOW_DATE_MISMATCH=1 was set without PVR_DATE_MISMATCH_REASON. "
            "An override without a recorded reason is an unexplained discrepancy "
            "in the published dates")
    return DATE_MISMATCH_REASON


def validate_release_dir():
    """A frozen release is not rebuilt over. Finding 1.

    Once a release has been built and frozen it is the artefact that gets
    packaged, deployed, verified and archived. Rebuilding it in place produces a
    different set under the same description, which is how packaging came to ship
    a set that had not been the one checked.
    """
    if not os.path.exists(RELEASE_META):
        return None
    with open(RELEASE_META) as f:
        meta = json.load(f)
    if not REPLACE:
        raise BuildError(
            "FROZEN",
            f"{RELEASE_NAME} already holds a frozen release: sequence "
            f"{meta['sequence']}, {meta['release_date']}, manifest "
            f"{meta['manifest_sha256'][:16]}…. Package that release, or build "
            f"elsewhere with PVR_RELEASE_DIR. To discard and rebuild an "
            f"UNPUBLISHED release deliberately, set PVR_REPLACE_RELEASE=1")
    return meta


def validate_sequence(index_ledger, replaced):
    """A published sequence is never rebuilt or reused for different content."""
    recorded = index_ledger.get("versions", {})
    key = str(SEQUENCE)
    if key in recorded:
        raise BuildError(
            "SEQUENCE",
            f"sequence {SEQUENCE} has already been published "
            f"(recorded {recorded[key].get('recorded_at')}). Published indexes are "
            f"immutable; advance the sequence")
    highest = max((int(k) for k in recorded), default=0)
    if SEQUENCE <= highest:
        raise BuildError(
            "SEQUENCE",
            f"sequence {SEQUENCE} is not above the highest published sequence "
            f"{highest}. An index may not be made current behind the record")
    if replaced and replaced.get("published"):
        raise BuildError(
            "FROZEN",
            "the existing release is recorded as published and may not be replaced")


def publication_dates(ledger):
    """First-publication dates come from the ledger; the builder never writes it.

    A version already published keeps its recorded date across every later
    release. A version not yet published takes this release's date, which becomes
    its first-publication date only when `record_publication.py` records it
    against live evidence.
    """
    recorded = ledger.get("versions", {})
    dates, newly = {}, []
    for e in LINEAGE:
        v = e["version"]
        if v in recorded:
            dates[v] = recorded[v]["first_published"]
        else:
            dates[v] = RELEASE_DATE
            newly.append(v)
    return dates, newly


# --------------------------------------------------------------------- page

def render_page(idx):
    """Render index.html from the published index.

    Folded into the builder at v3. As two scripts, a set could be built without
    being rendered, leaving a stale page beside a fresh index.
    """
    import html
    e = html.escape
    rows = "\n".join(
        f"""      <tr{' class="current"' if v['is_current'] else ''}>
        <td><a href="{e(v['entry_url'])}">{e(v['version'])}</a></td>
        <td>{e(v['instrument_date'])}</td>
        <td>{e(v['published_to_record'])}</td>
        <td>{e(v['status'])}{(' &larr; ' + e(v['superseded_by'])) if v.get('superseded_by') else ''}</td>
        <td>{e(v['reason'] or '&mdash; first issue')}</td>
        <td class="d"><code>{e(v['content_digest'].split(':', 1)[1])}</code><br><span class="b">{v['bytes']:,} bytes &middot; {e(v['mime_type'])}</span></td>
      </tr>""" for v in idx["versions"])

    return f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Public version record &middot; Arkaya Schema Independence Charter</title>
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
<h1>Public version record</h1>
<p class="sub">{e(idx['instrument'])} &middot; sequence {idx['sequence']} &middot; as of {e(idx['as_of'])}</p>

<div class="note">{e(idx['as_of_caveat'])}</div>

<h2>Versions</h2>
<table><thead><tr><th>Version</th><th>Instrument date</th><th>Published to this record</th><th>Status</th><th>Reason for amendment</th><th>SHA-256</th></tr></thead>
<tbody>
{rows}
</tbody></table>

<div class="note"><strong>Instrument date and publication date are different fields.</strong>
Each version's instrument date is the date on its own cover. Its publication date is the date it was
first published to this record. No earlier publication date is asserted for any version.</div>

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
<a href="manifest.json">manifest.json</a>. To verify any version, retrieve it and compare its SHA-256
against the digest published above.</p>

<footer>Arkaya Risk &middot; canonical URI <code>{e(idx['canonical_uri'])}</code></footer>
</div></body></html>
"""


ROOT_POINTER = """<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Arkaya Risk &middot; public version record</title>
<style>body{margin:0;background:#fbfcfc;color:#12211f;font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.w{max-width:36rem;margin:0 auto;padding:4rem 1.25rem}h1{font-size:1.25rem;color:#0f3d3a;margin:0 0 .5rem}
p{color:#5a6b68}a{color:#0f3d3a}</style></head><body><div class="w">
<h1>Arkaya Risk &mdash; public version record</h1>
<p>The published version record for the Arkaya Schema Independence Charter is at
<a href="/charter/">/charter/</a>.</p>
<p>This page is a navigation aid. It is not part of the record and asserts nothing about it.</p>
</div></body></html>
"""


# -------------------------------------------------------------------- build

def build():
    # 1. Validate everything the build consumes and everything it would replace,
    #    before anything is destroyed.
    now_dt = datetime.now(timezone.utc)
    date_reason = validate_date(now_dt.date().isoformat())
    replaced = validate_release_dir()
    validated_inputs = validate_inputs()
    readme_source = validate_readme_source()
    ledger = load_ledger(LEDGER, {"note": "First publication date per version, recorded only "
                                          "by record_publication.py against live evidence.",
                                  "versions": {}})
    index_ledger = load_ledger(INDEX_LEDGER, {"note": "Every index made current, with its "
                                                     "immutable snapshot under publications/.",
                                              "versions": {}})
    validate_sequence(index_ledger, replaced)
    dates, newly = publication_dates(ledger)

    # as_of is the release date, not a build timestamp. index.json and index.html
    # are therefore bit-reproducible: only the manifest and its sidecar carry a
    # build time, which narrows what a reproducibility check has to excuse.
    now = now_dt.isoformat()

    # 2. Build into staging. The live tree is untouched until the set is whole.
    if os.path.exists(STAGING):
        shutil.rmtree(STAGING)
    os.makedirs(STAGING)

    rows = []
    for e in LINEAGE:
        src = os.path.join(INPUTS, e["src"])
        vdir = os.path.join(STAGING, e["version"])
        os.makedirs(vdir)
        name = f"charter-{e['version']}.pdf"
        dst = os.path.join(vdir, name)
        shutil.copyfile(src, dst)          # bytes unchanged, never regenerated
        out_sha = digest(dst)
        if out_sha != EXPECTED_INPUTS[e["src"]][0]:
            raise BuildError("COPY", f"{name}: copy digest {out_sha} does not match its input")
        rel = f"{e['version']}/{name}"
        is_current = e["superseded_by"] is None
        row = {
            "version": e["version"],
            "instrument_date": e["instrument_date"],
            "published_to_record": dates[e["version"]],
            "reason": e["reason"],
            "revision_class": "minor_decimal" if "." in e["version"].lstrip("v") else "whole_integer",
            "predecessor": e["predecessor"],
            "is_current": is_current,
            "status": "current" if is_current else "superseded",
            "entry_url": rel,
            "canonical_uri": f"{CANONICAL_BASE}/{rel}",
            "mime_type": "application/pdf",
            "content_digest": "sha256:" + out_sha,
            "bytes": os.path.getsize(dst),
            "source": validated_inputs[e["src"]]["path"],
        }
        if e["superseded_by"]:
            row["superseded_by"] = e["superseded_by"]
            row["superseded_from"] = e["superseded_from"]
            row["superseded_from_basis"] = (
                "instrument date of the succeeding issue; documentary chronology, "
                "not an assertion of legal effect")
        rows.append(row)

    index = {
        "schema": "arkaya-version-record/2",
        "instrument": "Arkaya Schema Independence Charter",
        "canonical_uri": f"{CANONICAL_BASE}/",
        "as_of": RELEASE_DATE,
        "as_of_caveat": AS_OF_CAVEAT,
        "sequence": SEQUENCE,
        # Every entry carries a dated change event and the index says so. The
        # acceptance suite's check 8 reads this: dropping it in a rewrite is what
        # the expected-outcome enforcement caught on 16 September 2026.
        "change_log_dated": True,
        "retention": RETENTION,
        "not_asserted": NOT_ASSERTED,
        "definitions": DEFINITIONS,
        "versions": rows,
    }
    index_path = os.path.join(STAGING, "index.json")
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
    index_sha = digest(index_path)

    shutil.copyfile(readme_source, os.path.join(STAGING, "README.md"))
    with open(os.path.join(STAGING, "index.html"), "w") as f:
        f.write(render_page(index))

    def obj(path, mime):
        full = os.path.join(STAGING, path)
        return {"path": path, "canonical_uri": f"{CANONICAL_BASE}/{path}",
                "mime_type": mime, "bytes": os.path.getsize(full),
                "sha256": digest(full)}

    manifest = {
        "schema": "arkaya-integrity-manifest/3",
        "instrument": "Arkaya Schema Independence Charter",
        "as_of": RELEASE_DATE,
        "sequence": SEQUENCE,
        "canonical_uri": f"{CANONICAL_BASE}/",
        "provenance_claim": PROVENANCE_CLAIM,
        "builder": {
            "script": os.path.basename(__file__),
            "source_path": BUILDER_SOURCE_PATH,
            "version": BUILDER_VERSION,
            "sha256": digest(os.path.abspath(__file__)),
        },
        "build_parameters": {
            "built_at": now,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "PVR_CANONICAL_BASE": CANONICAL_BASE,
            "PVR_RELEASE_DATE": RELEASE_DATE,
            "PVR_SEQUENCE": SEQUENCE,
            "date_mismatch_reason": date_reason,
        },
        "inputs": [validated_inputs[e["src"]] | {"version": e["version"]} for e in LINEAGE],
        "generated": [
            {"path": "README.md", "generated_from": "README_source.md",
             "source_sha256": digest(readme_source),
             "sha256": digest(os.path.join(STAGING, "README.md")),
             "relation": "verbatim copy"},
            {"path": "index.html", "generated_from": "index.json",
             "source_sha256": index_sha,
             "sha256": digest(os.path.join(STAGING, "index.html")),
             "relation": "rendered by builder"},
        ],
        # as_of is a date, not a timestamp, so the index and the page reproduce
        # bit for bit. Only these two carry a build time.
        "not_bit_reproducible": {
            "paths": ["manifest.json", "manifest.json.sha256"],
            "reason": "the manifest carries built_at and the platform; its sidecar "
                      "digests the manifest",
        },
        "objects": [
            dict(obj(r["entry_url"], r["mime_type"]),
                 version=r["version"], status=r["status"])
            for r in rows
        ] + [
            obj("index.json", "application/json"),
            obj("index.html", "text/html"),
            obj("README.md", "text/markdown"),
        ],
    }
    with open(os.path.join(STAGING, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    manifest_sha = digest(os.path.join(STAGING, "manifest.json"))
    with open(os.path.join(STAGING, "manifest.json.sha256"), "w") as f:
        f.write(manifest_sha + "  manifest.json\n")

    # 3. Promote staging into place. Only now does any previous set go.
    os.makedirs(RELEASE_DIR, exist_ok=True)
    previous = OUT + ".previous"
    if os.path.exists(previous):
        shutil.rmtree(previous)
    if os.path.exists(OUT):
        os.rename(OUT, previous)
    try:
        os.rename(STAGING, OUT)
    except BaseException:
        if os.path.exists(previous) and not os.path.exists(OUT):
            os.rename(previous, OUT)   # put the previous set back
        raise
    if os.path.exists(previous):
        shutil.rmtree(previous)

    with open(os.path.join(RELEASE_DIR, "index.html"), "w") as f:
        f.write(ROOT_POINTER)

    # 4. Freeze. The marker lives outside the release directory so it is never
    #    served, and it is what package.py checks the release against.
    meta = {
        "schema": "arkaya-release/1",
        "release_dir": RELEASE_NAME,
        "sequence": SEQUENCE,
        "release_date": RELEASE_DATE,
        "built_at": now,
        "canonical_base": CANONICAL_BASE,
        "manifest_sha256": manifest_sha,
        "index_sha256": index_sha,
        "root_pointer_sha256": digest(os.path.join(RELEASE_DIR, "index.html")),
        "builder": manifest["builder"],
        "date_mismatch_reason": date_reason,
        "versions_awaiting_first_publication": newly,
        "published": False,
        "state": "frozen release candidate; not deployed, not published",
    }
    save_json(RELEASE_META, meta)
    return index, manifest, meta


if __name__ == "__main__":
    try:
        idx, man, meta = build()
    except BuildError as exc:
        if os.path.isdir(STAGING):
            shutil.rmtree(STAGING)
        print(f"BUILD REFUSED {exc}")
        print("Nothing was deleted or replaced. Any existing release is intact.")
        raise SystemExit(2)

    print(f"canonical      {idx['canonical_uri']}")
    print(f"release dir    {RELEASE_DIR}   (publish directory)")
    print(f"release meta   releases/{RELEASE_NAME}.json   FROZEN")
    print(f"state          {meta['state']}")
    print(f"sequence       {idx['sequence']}   release date {RELEASE_DATE}")
    print(f"builder        {man['builder']['version']}  {man['builder']['sha256'][:16]}…")
    print(f"manifest       {meta['manifest_sha256'][:16]}…")
    if meta["date_mismatch_reason"]:
        print(f"date override  {meta['date_mismatch_reason']}")
    if meta["versions_awaiting_first_publication"]:
        print(f"awaiting       {', '.join(meta['versions_awaiting_first_publication'])} "
              f"-> {RELEASE_DATE} (recorded only by record_publication.py)")
    for r in idx["versions"]:
        print(f"  {r['version']:<5} {r['status']:<10} {r['content_digest'][7:27]}…  "
              f"{r['bytes']:>7} bytes  released {r['published_to_record']}")
