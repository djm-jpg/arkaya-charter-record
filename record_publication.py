"""Record that a release was published, from evidence that it was.

DM's finding 5 of 16 September 2026: the builder wrote first-publication dates
and marked the set "published" before Netlify, DNS or any live observation, so a
failed or delayed deployment left a false publication record. Publication is an
observed event, not a build parameter. This script is the only thing in the
package that writes the publication ledgers, and it writes them only against a
passing, approved live verification of the frozen release at the canonical
address.

Two further findings of 17 September answered here:

  4. It validated the manifest FILE's hash but not the files the manifest
     describes. With synthetic approved evidence and the local `index.json`
     replaced by `{}`, the evidence check returned no problems, so it would have
     snapshotted an index inconsistent with its own recorded digest. Every
     release object, the sidecar and the relevant freeze-marker fields are now
     validated immediately before recording, and only that validated set is
     copied into the snapshot.

  5. It created `publications/<sequence>/` and only then loaded and updated the
     ledgers. A failure in between left partial state that could not be retried,
     because the snapshot directory already existed. The transaction is now
     staged and committed by an atomic rename, the ledger writes are idempotent,
     and an interrupted publication is distinguishable from a completed one and
     can be resumed.

DM's point of 17 September, treated as a defect because it is one: valid approval
evidence could in principle be attached to the WRONG frozen release. The manifest
digest was already bound; the COMMIT was not. It was free text, recorded but never
checked against anything. The release is now bound to its commit and tag in a
separate, deliberate step, before deployment, and recording refuses unless the
commit and tag it is given are exactly the ones bound to this frozen release.

    python3 record_publication.py --bind \\
        --commit <frozen-release commit sha> --tag release-001

    python3 record_publication.py \\
        --evidence verification/live/live_verification_<stamp>.json \\
        --deploy-id <netlify deploy id> \\
        --deploy-permalink https://<id>--arkaya-record.netlify.app \\
        --commit <the bound commit> --tag release-001

    python3 record_publication.py --resume ...   complete an interrupted recording

**The bound limit.** This binds the recorder to a commit identifier supplied by the
operator at the moment the release was committed. It cannot verify that the commit
exists in any repository, or that the repository holds these bytes. What it removes
is the looser failure: approval evidence for one frozen release being recorded
against another. Step B7 of DEPLOY.md, a fresh clone at the tag passing
`package.py --check`, is what tests the other half.

`publication-001` is NOT the published object. It is the evidence record that
publication occurred, and it necessarily post-dates the deployment it records.
`release-001` identifies the bytes that were deployed.

MULTIPLE RECORDS, 28 September 2026. A release built by `build_release.py`
carries the Charter, carried byte-identical from the published release, and the
disclosure record (see `records.py`). Recording such a release is per namespace:

  - Only a namespace NEWLY PUBLISHED by this release gets first-publication
    entries, an index-ledger entry and a snapshot, each in its OWN locations as
    registered. For the disclosure record these are under `ledgers/disclosures/`.
  - The Charter is recorded as CARRIED UNCHANGED at its existing sequence. No
    Charter ledger is written, no first-publication date is added or moved, and
    `publications/1/` is untouched. The carriage is stated in the new
    publication's snapshot, which holds both manifests and the live evidence.
  - The evidence must be an approved multi-namespace verification that found
    the served Charter identical to the published Charter.

What it writes, for a single-record release:

    first_publication.json     first-publication date per version, never changed
    published_indexes.json     the index made current at each sequence
    publications/<sequence>/   IMMUTABLE SNAPSHOT of the index, the manifest, its
                               sidecar, the release metadata and the live
                               evidence. A ledger of hashes is not a retained
                               record: without the files themselves, a later
                               holder of the hash has nothing to compare against.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import records  # noqa: E402

RELEASES = os.path.join(HERE, "releases")
LEDGER = os.path.join(HERE, "first_publication.json")
INDEX_LEDGER = os.path.join(HERE, "published_indexes.json")
PUBLICATIONS = os.path.join(HERE, "publications")

SNAPSHOT_FILES = ("index.json", "manifest.json", "manifest.json.sha256")

ALLOW_TEST_INPUT = os.environ.get("PVR_ALLOW_TEST_INPUT") == "1"


class RecordError(Exception):
    pass


def valid_commit(value):
    v = (value or "").strip().lower()
    return len(v) == 40 and all(c in "0123456789abcdef" for c in v)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load(path, what):
    if not os.path.exists(path):
        raise RecordError(f"{what} not found: {path}")
    try:
        with open(path) as f:
            return json.load(f)
    except ValueError as exc:
        raise RecordError(f"{what} is unreadable: {exc}")


def load_or_empty(path, note):
    if not os.path.exists(path):
        return {"note": note, "versions": {}}
    d = load(path, os.path.basename(path))
    if not isinstance(d, dict) or "versions" not in d:
        raise RecordError(f"{os.path.basename(path)} has an unexpected shape")
    return d


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


# ------------------------------------------------------------- validation

def validate_record(record, want_manifest_sha, want_index_sha, where=""):
    """One record directory against its manifest and its freeze-marker digests.

    Shared by the single-record and multi-namespace paths, so every record is
    held to the same standard. Returns (problems, manifest or None).
    """
    problems = []
    manifest_path = os.path.join(record, "manifest.json")
    if not os.path.isfile(manifest_path):
        return [f"{where}the release has no manifest"], None

    manifest_sha = sha(manifest_path)
    if manifest_sha != want_manifest_sha:
        problems.append(f"{where}the release directory no longer matches its freeze marker "
                        f"({manifest_sha[:16]}… vs {str(want_manifest_sha)[:16]}…)")
    manifest = load(manifest_path, "manifest")

    for o in manifest["objects"]:
        p = os.path.join(record, o["path"])
        if not os.path.isfile(p):
            problems.append(f"{where}{o['path']}: named in the manifest, not on disk")
            continue
        if sha(p) != o["sha256"]:
            problems.append(f"{where}{o['path']}: {sha(p)[:16]}… does not match the manifest's "
                            f"{o['sha256'][:16]}…")
        elif os.path.getsize(p) != o["bytes"]:
            problems.append(f"{where}{o['path']}: {os.path.getsize(p)} bytes, manifest says "
                            f"{o['bytes']}")

    named = {o["path"] for o in manifest["objects"]} | {"manifest.json", "manifest.json.sha256"}
    on_disk = set()
    for dirpath, _, names in os.walk(record):
        for n in names:
            on_disk.add(os.path.relpath(os.path.join(dirpath, n), record))
    for extra in sorted(on_disk - named):
        problems.append(f"{where}{extra}: present in the release but not named in the manifest")

    sidecar = os.path.join(record, "manifest.json.sha256")
    if not os.path.isfile(sidecar):
        problems.append(f"{where}manifest.json.sha256 is missing")
    else:
        with open(sidecar) as f:
            parts = f.read().split()
        if not parts or parts[0] != manifest_sha:
            problems.append(f"{where}manifest.json.sha256 does not match manifest.json")

    index = os.path.join(record, "index.json")
    if os.path.isfile(index) and sha(index) != want_index_sha:
        problems.append(f"{where}index.json does not match the index digest in the freeze marker")
    return problems, manifest


def validate_release(release_dir, meta):
    """The WHOLE release, not just the manifest file. Finding 4.

    Checking the manifest's own hash says the manifest has not been edited. It
    says nothing about whether the objects it describes are still what it says
    they are. An `index.json` replaced by `{}` passed the previous check.

    Since 28 September 2026 the Charter is also checked against its PUBLISHED
    manifest digest, registered in `records.py`, not only against the local
    freeze marker: a release whose Charter was rebuilt or altered, however
    consistently, is not recorded.
    """
    if is_multi(meta):
        return validate_multi_release(release_dir, meta)
    record = os.path.join(release_dir, "charter")
    problems, manifest = validate_record(record, meta["manifest_sha256"], meta["index_sha256"])
    if manifest is None:
        return problems, None

    pointer = os.path.join(release_dir, "index.html")
    if not os.path.isfile(pointer):
        problems.append("the deploy root pointer page is missing")
    elif sha(pointer) != meta.get("root_pointer_sha256"):
        problems.append("the deploy root pointer page does not match the freeze marker")

    if meta["builder"] != manifest.get("builder"):
        problems.append("the freeze marker's builder block differs from the manifest's")
    if meta["release_date"] != manifest.get("as_of"):
        problems.append("the freeze marker's release date differs from the manifest's as_of")

    problems += [f"[CHARTER_IDENTITY] {p}" for p in records.charter_record_problems(record)]
    return problems, manifest


def is_multi(meta):
    return meta.get("schema") == "arkaya-release/2"


def validate_multi_release(release_dir, meta):
    """Every namespace of a multi-namespace release, and the Charter's identity.

    Returns (problems, {namespace: manifest}) or (problems, None) when the
    release cannot be read at all.
    """
    problems = [f"[REGISTRY] {p}" for p in records.registry_problems()]
    marker_ns = meta.get("namespaces") or {}
    registered = [ns["name"] for ns in records.NAMESPACES]
    if sorted(marker_ns) != sorted(registered):
        problems.append(f"[NAMESPACES] the freeze marker names {sorted(marker_ns)}, the "
                        f"registry {sorted(registered)}")
    for required in records.REQUIRED:
        if required not in marker_ns:
            problems.append(f"[CHARTER_CARRY] the release does not carry the {required} "
                            f"namespace. No release may omit the carried Charter")

    manifests = {}
    for ns in records.NAMESPACES:
        m = marker_ns.get(ns["name"]) or {}
        record = os.path.join(release_dir, ns["path"])
        if ns["mode"] == "carried":
            ident = records.charter_record_problems(record)
            problems += [f"[CHARTER_IDENTITY] {p}" for p in ident]
            if (m.get("mode") != "carried"
                    or m.get("manifest_sha256") != ns["published_manifest_sha256"]
                    or m.get("sequence") != ns["published_sequence"]):
                problems.append(f"[CHARTER_IDENTITY] the freeze marker does not record the "
                                f"{ns['name']} as carried at its published sequence and "
                                f"manifest")
            if not ident:
                manifests[ns["name"]] = load(os.path.join(record, "manifest.json"), "manifest")
            continue
        if not m:
            continue
        where = f"{ns['path']}/"
        ns_problems, manifest = validate_record(record, m.get("manifest_sha256"),
                                                m.get("index_sha256"), where)
        problems += ns_problems
        if manifest is None:
            continue
        manifests[ns["name"]] = manifest
        if m.get("builder") != manifest.get("builder"):
            problems.append(f"{where}the freeze marker's builder block differs from the "
                            f"manifest's")
        if meta.get("release_date") != manifest.get("as_of"):
            problems.append(f"{where}the freeze marker's release date differs from the "
                            f"manifest's as_of")
        if m.get("sequence") != manifest.get("sequence"):
            problems.append(f"{where}the freeze marker's sequence differs from the manifest's")
        if manifest.get("canonical_uri") != ns["canonical_uri"]:
            problems.append(f"{where}the manifest's canonical URI is not the registered one")

    if os.path.isdir(release_dir):
        membership = set(os.listdir(release_dir))
        expected = {"index.html"} | {ns["path"] for ns in records.NAMESPACES}
        if membership != expected:
            problems.append(f"[LAYOUT] the deploy root holds {sorted(membership)}, expected "
                            f"{sorted(expected)}")
    pointer = os.path.join(release_dir, "index.html")
    if not os.path.isfile(pointer):
        problems.append("the deploy root pointer page is missing")
    elif sha(pointer) != meta.get("root_pointer_sha256"):
        problems.append("the deploy root pointer page does not match the freeze marker")
    if not manifests:
        return problems, None
    return problems, manifests


def note_evidence_tag(meta, tag, commit):
    """Record the publication-evidence tag, after it exists.

    The tag that identifies the evidence commit cannot be known when publication
    is recorded: that commit is made afterwards, from the files recording writes.
    Without this the production record had to name a tag it could not know, and
    `release-001` and `publication-001` were hard-coded into it. A replacement
    release taking `release-002` would then have generated a contradictory record.

    It is written to the published-index ledger, NOT into the immutable snapshot,
    because the snapshot is what was published and is never edited afterwards.
    """
    if is_multi(meta):
        return note_evidence_tag_multi(meta, tag, commit)
    seq = str(meta["sequence"])
    if not meta.get("published"):
        print(f"NOT RECORDED: sequence {seq} is not recorded as published.")
        return 2
    if not tag:
        print("NOT RECORDED: --evidence-tag is required.")
        return 2
    if commit and not valid_commit(commit):
        print(f"NOT RECORDED: {commit!r} is not a 40-character commit SHA.")
        return 2

    ledger = load_or_empty(INDEX_LEDGER, "")
    entry = ledger["versions"].get(seq)
    if entry is None:
        print(f"NOT RECORDED: sequence {seq} is not in published_indexes.json.")
        return 2
    existing = entry.get("publication_evidence_tag")
    if existing and existing != tag:
        print(f"NOT RECORDED: sequence {seq} already records evidence tag {existing}. "
              f"Tags are not moved; a replacement takes the next identifier.")
        return 2

    entry["publication_evidence_tag"] = tag
    if commit:
        entry["publication_evidence_commit"] = commit.strip().lower()
    entry["evidence_tag_recorded_at"] = datetime.now(timezone.utc).isoformat()
    save_json(INDEX_LEDGER, ledger)
    print(f"  sequence {seq} evidence tag recorded: {tag}")
    if commit:
        print(f"  evidence commit {commit[:12]}…")
    print("  written to published_indexes.json; the immutable snapshot is untouched")
    return 0


def check_binding(meta, commit, tag):
    """The release must be bound to this commit and tag, and to no other.

    Without this the commit was free text: recorded, never checked. Approval
    evidence for one frozen release could be recorded against another.
    """
    problems = []
    bound_commit = meta.get("release_commit")
    bound_tag = meta.get("release_tag")
    if not bound_commit:
        problems.append(
            "this release is not bound to a commit. Create the frozen-release commit "
            "and tag first, then run: record_publication.py --bind --commit <sha> "
            "--tag release-001")
        return problems
    if (commit or "").strip().lower() != bound_commit:
        problems.append(f"the commit given ({(commit or '')[:12]}…) is not the commit bound "
                        f"to this frozen release ({bound_commit[:12]}…)")
    if (tag or "") != (bound_tag or ""):
        problems.append(f"the tag given ({tag or 'none'}) is not the tag bound to this "
                        f"frozen release ({bound_tag or 'none'})")
    return problems


def bind(meta, meta_path, release_dir, commit, tag):
    """Bind the frozen release to its commit and tag. Deliberate, and once only."""
    problems, manifest = validate_release(release_dir, meta)
    if manifest is None or problems:
        print("NOT BOUND. Nothing was written.")
        for p in problems or ["the release could not be validated"]:
            print(f"  - {p}")
        return 2
    if meta.get("published"):
        print("NOT BOUND: this release is already recorded as published.")
        return 2
    if not valid_commit(commit):
        print(f"NOT BOUND: {commit!r} is not a 40-character commit SHA.")
        return 2
    if not tag:
        print("NOT BOUND: --tag is required; it is what the publication log records.")
        return 2

    existing = meta.get("release_commit")
    if existing and (existing != commit.strip().lower() or meta.get("release_tag") != tag):
        print(f"NOT BOUND: this release is already bound to commit {existing[:12]}… "
              f"and tag {meta.get('release_tag')}. A frozen release is bound once. "
              f"If the commit was wrong, rebuild the release and bind the new one.")
        return 2

    meta["release_commit"] = commit.strip().lower()
    meta["release_tag"] = tag
    meta["bound_at"] = datetime.now(timezone.utc).isoformat()
    meta["binding_bound"] = ("binds this frozen release to a commit identifier supplied by "
                            "the operator. It does not verify that the commit exists in any "
                            "repository, or that the repository holds these bytes.")
    save_json(meta_path, meta)
    print(f"  release {meta.get('sequence', meta.get('release_dir'))} bound to commit "
          f"{meta['release_commit'][:12]}… tag {tag}")
    if is_multi(meta):
        for name, d in meta["namespaces"].items():
            print(f"  {name:<15} {d['mode']}, manifest {d['manifest_sha256'][:16]}…")
    else:
        print(f"  manifest        {meta['manifest_sha256'][:16]}…")
    print(f"  bound limit     {meta['binding_bound']}")
    return 0


def check_evidence(evidence, meta, manifest):
    """Every reason this publication might not have happened as claimed."""
    problems = []

    if evidence.get("rehearsal"):
        problems.append("the evidence is a rehearsal over plain HTTP, not an "
                        "observation of the canonical venue")
    if not evidence.get("passed"):
        problems.append(f"the live verification did not pass: "
                        f"{'; '.join(evidence.get('findings', [])) or 'no findings recorded'}")
    if not evidence.get("production_approval"):
        problems.append("the live verification did not grant production approval; "
                        "it was not run against the frozen release at the canonical address")

    canonical = manifest["canonical_uri"]
    if evidence.get("base") != canonical:
        problems.append(f"the evidence is for {evidence.get('base')}, not the canonical "
                        f"address {canonical}")
    if evidence.get("manifest_sha256") != meta["manifest_sha256"]:
        problems.append(f"the evidence was taken against manifest "
                        f"{str(evidence.get('manifest_sha256'))[:16]}…, the frozen release "
                        f"is {meta['manifest_sha256'][:16]}…")
    served = evidence.get("served_manifest_sha256")
    if served is not None and served != meta["manifest_sha256"]:
        problems.append(f"the venue served manifest {str(served)[:16]}…, the frozen release "
                        f"is {meta['manifest_sha256'][:16]}…")

    verified_date = str(evidence.get("verified_at", ""))[:10]
    if verified_date != meta["release_date"]:
        problems.append(
            f"the record was verified live on {verified_date or 'an unstated date'}, but the "
            f"set carries {meta['release_date']} on its face. A set may not be recorded as "
            f"published on a date it was not observed at the canonical address. Rebuild at "
            f"the correct date and redeploy")

    return problems


# ------------------------------------------------------------- transaction

def inspect(seq, meta):
    """Absent, incomplete or complete. Finding 5.

    An interrupted recording must be distinguishable from a finished one, or the
    only safe response to a crash is to do nothing for ever.
    """
    snapshot = os.path.join(PUBLICATIONS, str(seq))
    if not os.path.isdir(snapshot):
        return "absent", []
    missing = [f for f in (*SNAPSHOT_FILES, "release.json", "live_verification.json",
                           "publication.json") if not os.path.isfile(os.path.join(snapshot, f))]
    ledger = load_or_empty(LEDGER, "")
    index_ledger = load_or_empty(INDEX_LEDGER, "")
    awaiting = meta.get("versions_awaiting_first_publication", [])
    steps_done = {
        "snapshot": not missing,
        "first_publication": all(v in ledger["versions"] for v in awaiting),
        "published_indexes": str(seq) in index_ledger["versions"],
        "release_marked": bool(meta.get("published")),
    }
    if all(steps_done.values()):
        return "complete", []
    outstanding = [k for k, v in steps_done.items() if not v]
    if missing:
        outstanding.append(f"snapshot files missing: {', '.join(missing)}")
    return "incomplete", outstanding


def stage_snapshot(seq, release_dir, meta, meta_path, evidence_path, payload):
    """Build the snapshot beside its destination, then move it in atomically."""
    record = os.path.join(release_dir, "charter")
    os.makedirs(PUBLICATIONS, exist_ok=True)
    staging = tempfile.mkdtemp(dir=PUBLICATIONS, prefix=f".staging-{seq}-")
    try:
        for name in SNAPSHOT_FILES:
            shutil.copyfile(os.path.join(record, name), os.path.join(staging, name))
        shutil.copyfile(meta_path, os.path.join(staging, "release.json"))
        shutil.copyfile(evidence_path, os.path.join(staging, "live_verification.json"))
        with open(os.path.join(staging, "publication.json"), "w") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        # Read back what was staged before it becomes the retained record.
        for name in SNAPSHOT_FILES:
            if sha(os.path.join(staging, name)) != sha(os.path.join(record, name)):
                raise RecordError(f"{name} did not copy faithfully into the snapshot")
        destination = os.path.join(PUBLICATIONS, str(seq))
        os.rename(staging, destination)
        return destination
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


# ------------------------------------------------------ multiple namespaces

def built_namespaces(meta):
    """The namespaces this release publishes: registered as built, in the marker."""
    return [ns for ns in records.NAMESPACES
            if ns["mode"] == "built" and ns["name"] in (meta.get("namespaces") or {})]


def note_evidence_tag_multi(meta, tag, commit):
    """The evidence tag goes to each published namespace's OWN index ledger.

    Never to the Charter's: the Charter was carried, not published, by this
    release, and its ledgers are not written.
    """
    if not meta.get("published"):
        print(f"NOT RECORDED: release {meta['release_dir']} is not recorded as published.")
        return 2
    if not tag:
        print("NOT RECORDED: --evidence-tag is required.")
        return 2
    if commit and not valid_commit(commit):
        print(f"NOT RECORDED: {commit!r} is not a 40-character commit SHA.")
        return 2
    staged = []
    for ns in built_namespaces(meta):
        seq = str(meta["namespaces"][ns["name"]]["sequence"])
        path = os.path.join(HERE, ns["index_ledger"])
        ledger = load_or_empty(path, "")
        entry = ledger["versions"].get(seq)
        if entry is None:
            print(f"NOT RECORDED: {ns['name']} sequence {seq} is not in {ns['index_ledger']}.")
            return 2
        existing = entry.get("publication_evidence_tag")
        if existing and existing != tag:
            print(f"NOT RECORDED: {ns['name']} sequence {seq} already records evidence tag "
                  f"{existing}. Tags are not moved; a replacement takes the next identifier.")
            return 2
        entry["publication_evidence_tag"] = tag
        if commit:
            entry["publication_evidence_commit"] = commit.strip().lower()
        entry["evidence_tag_recorded_at"] = datetime.now(timezone.utc).isoformat()
        staged.append((path, ledger, ns, seq))
    for path, ledger, ns, seq in staged:
        save_json(path, ledger)
        print(f"  {ns['name']} sequence {seq} evidence tag recorded: {tag}")
    print("  written to each published namespace's own index ledger; the Charter's ledgers "
          "and every immutable snapshot are untouched")
    return 0


def check_evidence_multi(evidence, meta, manifests):
    """Every reason this multi-namespace publication might not have happened as claimed."""
    problems = []
    if evidence.get("rehearsal"):
        problems.append("the evidence is a rehearsal over plain HTTP, not an "
                        "observation of the canonical venue")
    if not evidence.get("passed"):
        problems.append(f"the live verification did not pass: "
                        f"{'; '.join(evidence.get('findings', [])) or 'no findings recorded'}")
    if not evidence.get("production_approval"):
        problems.append("the live verification did not grant production approval; "
                        "it was not run against the frozen release at the canonical address")
    if evidence.get("release_schema") != "arkaya-release/2" or not evidence.get("namespaces"):
        problems.append("the evidence is not a multi-namespace verification of this release")
    if evidence.get("release") != meta["release_dir"]:
        problems.append(f"the evidence is for release {evidence.get('release')}, not "
                        f"{meta['release_dir']}")
    if evidence.get("base") != records.CANONICAL_ROOT:
        problems.append(f"the evidence is for {evidence.get('base')}, not the canonical "
                        f"address {records.CANONICAL_ROOT}")
    # A release built from a synthetic TEST INPUT is never published. The live
    # verifier never approves one; this is the second, independent refusal. The
    # test suite exercises the recorder on such a release, in a sandbox, with the
    # same explicit switch the builder requires, and the result says so.
    if (meta.get("test_input") or evidence.get("test_input")) and not ALLOW_TEST_INPUT:
        problems.append("[TEST_INPUT] the release was built from a TEST INPUT; it is never "
                        "published")

    ev_ns = evidence.get("namespaces") or {}
    for name, m in (meta.get("namespaces") or {}).items():
        e = ev_ns.get(name)
        if e is None:
            problems.append(f"the evidence does not cover the {name} namespace")
            continue
        if e.get("manifest_sha256") != m["manifest_sha256"]:
            problems.append(f"{name}: the evidence was taken against manifest "
                            f"{str(e.get('manifest_sha256'))[:16]}…, the frozen release is "
                            f"{m['manifest_sha256'][:16]}…")
        served = e.get("served_manifest_sha256")
        if served != m["manifest_sha256"]:
            problems.append(f"{name}: the venue served manifest {str(served)[:16]}…, the "
                            f"frozen release is {m['manifest_sha256'][:16]}…")
        if not e.get("passed"):
            problems.append(f"{name}: the namespace did not pass live verification")

    ident = evidence.get("charter_identity") or {}
    published = records.CHARTER["published_manifest_sha256"]
    if not ident.get("passed") or ident.get("served_manifest_sha256") != published:
        problems.append("[CHARTER_IDENTITY] the evidence does not show the published Charter "
                        "served unchanged")

    verified_date = str(evidence.get("verified_at", ""))[:10]
    if verified_date != meta["release_date"]:
        problems.append(
            f"the record was verified live on {verified_date or 'an unstated date'}, but the "
            f"release carries {meta['release_date']} on its face. A release may not be "
            f"recorded as published on a date it was not observed at the canonical address")
    return problems


CARRIED_SNAPSHOT = ("index.json", "manifest.json", "manifest.json.sha256")


def snapshot_dir(ns, seq):
    return os.path.join(HERE, ns["snapshots"], str(seq))


def inspect_multi(meta):
    """Absent, incomplete or complete, across every namespace this release publishes."""
    dirs = [(ns, meta["namespaces"][ns["name"]]) for ns in built_namespaces(meta)]
    present = [ns for ns, m in dirs if os.path.isdir(snapshot_dir(ns, m["sequence"]))]
    if not present and not meta.get("published"):
        return "absent", []
    steps, missing_files = {}, []
    for ns, m in dirs:
        snap = snapshot_dir(ns, m["sequence"])
        wanted = [*SNAPSHOT_FILES, "release.json", "live_verification.json",
                  "publication.json"] + [f"carried/{c['path']}/{f}"
                                         for c in records.NAMESPACES if c["mode"] == "carried"
                                         for f in CARRIED_SNAPSHOT]
        missing = [f for f in wanted if not os.path.isfile(os.path.join(snap, f))]
        if missing:
            missing_files.append(f"{ns['name']}: {', '.join(missing)}")
        first = load_or_empty(os.path.join(HERE, ns["first_publication_ledger"]), "")
        index_ledger = load_or_empty(os.path.join(HERE, ns["index_ledger"]), "")
        steps[f"{ns['name']} snapshot"] = not missing
        steps[f"{ns['name']} first_publication"] = all(
            v in first["versions"] for v in m["versions_awaiting_first_publication"])
        steps[f"{ns['name']} published_indexes"] = str(m["sequence"]) in index_ledger["versions"]
    steps["release_marked"] = bool(meta.get("published"))
    if all(steps.values()):
        return "complete", []
    outstanding = [k for k, v in steps.items() if not v]
    if missing_files:
        outstanding.append(f"snapshot files missing: {'; '.join(missing_files)}")
    return "incomplete", outstanding


def stage_snapshot_multi(ns, seq, release_dir, meta_path, evidence_path, payload):
    """One namespace's snapshot, holding every record's manifest and the evidence.

    Staged beside its destination and moved in atomically, as for the Charter.
    """
    record = os.path.join(release_dir, ns["path"])
    parent = os.path.join(HERE, ns["snapshots"])
    os.makedirs(parent, exist_ok=True)
    staging = tempfile.mkdtemp(dir=parent, prefix=f".staging-{seq}-")
    try:
        pairs = [(os.path.join(record, n), n) for n in SNAPSHOT_FILES]
        for c in records.NAMESPACES:
            if c["mode"] == "carried":
                pairs += [(os.path.join(release_dir, c["path"], n), f"carried/{c['path']}/{n}")
                          for n in CARRIED_SNAPSHOT]
        for src, rel in pairs:
            dst = os.path.join(staging, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
        shutil.copyfile(meta_path, os.path.join(staging, "release.json"))
        shutil.copyfile(evidence_path, os.path.join(staging, "live_verification.json"))
        with open(os.path.join(staging, "publication.json"), "w") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        for src, rel in pairs:
            if sha(os.path.join(staging, rel)) != sha(src):
                raise RecordError(f"{rel} did not copy faithfully into the snapshot")
        destination = snapshot_dir(ns, seq)
        os.rename(staging, destination)
        return destination
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def charter_ledger_bytes():
    """The Charter's ledgers and snapshots, byte for byte, to prove none was written."""
    out = {}
    c = records.CHARTER
    for rel in (c["first_publication_ledger"], c["index_ledger"]):
        p = os.path.join(HERE, rel)
        out[rel] = sha(p) if os.path.isfile(p) else None
    snaps = os.path.join(HERE, c["snapshots"])
    if os.path.isdir(snaps):
        for dirpath, _, names in os.walk(snaps):
            for n in names:
                p = os.path.join(dirpath, n)
                out[os.path.relpath(p, HERE)] = sha(p)
    return out


def record_multi(a, meta, meta_path, release_dir):
    """Record a multi-namespace publication. The Charter is carried, never recorded anew."""
    problems, manifests = validate_release(release_dir, meta)
    if manifests is None:
        print("PUBLICATION NOT RECORDED. Nothing was written.")
        for p in problems or ["the release could not be validated"]:
            print(f"  - {p}")
        return 2
    evidence = load(a.evidence, "live verification evidence")
    problems += check_evidence_multi(evidence, meta, manifests)
    problems += check_binding(meta, a.commit, a.tag)

    # The carried Charter must already be the published Charter in its own ledger.
    c = records.CHARTER
    c_ledger = load_or_empty(os.path.join(HERE, c["index_ledger"]), "")
    c_entry = c_ledger["versions"].get(str(c["published_sequence"]))
    if not c_entry or c_entry.get("manifest_sha256") != c["published_manifest_sha256"]:
        problems.append(f"[CHARTER_IDENTITY] {c['index_ledger']} does not record the carried "
                        f"Charter at sequence {c['published_sequence']}")

    state, outstanding = inspect_multi(meta)
    if state == "complete":
        problems.append(f"release {meta['release_dir']} is already recorded as published; "
                        f"published sequences are immutable")
    elif state == "incomplete" and not a.resume:
        problems.append(f"release {meta['release_dir']} has an INCOMPLETE recording "
                        f"(outstanding: {', '.join(outstanding)}). Re-run with --resume to "
                        f"complete it. Nothing is lost; this is not a published sequence")
    elif state == "absent" and a.resume:
        problems.append(f"--resume was given but release {meta['release_dir']} has no "
                        f"partial recording")
    for ns in built_namespaces(meta):
        seq = meta["namespaces"][ns["name"]]["sequence"]
        idx = load_or_empty(os.path.join(HERE, ns["index_ledger"]), "")
        if state == "absent" and str(seq) in idx["versions"]:
            problems.append(f"{ns['name']} sequence {seq} has already been published; "
                            f"published sequences are immutable")

    if problems:
        print("PUBLICATION NOT RECORDED. Nothing was written.")
        for p in problems:
            print(f"  - {p}")
        return 2

    charter_before = charter_ledger_bytes()
    now = datetime.now(timezone.utc).isoformat()
    cm = meta["namespaces"]["charter"]
    carried = {
        "state": "carried unchanged",
        "carried_from_release": cm["carried_from_release"],
        "sequence": cm["sequence"],
        "manifest_sha256": cm["manifest_sha256"],
        "index_sha256": cm["index_sha256"],
        "first_publication_entries": [],
        "ledgers_written": False,
        "note": "The Charter was carried byte-identical from its published release and "
                "verified live as the published Charter. It was not published again: its "
                "first-publication dates, index ledger and snapshots are unchanged.",
    }

    resumed_from = None
    for ns in built_namespaces(meta):
        m = meta["namespaces"][ns["name"]]
        seq = m["sequence"]
        payload = {
            "schema": "arkaya-publication/2",
            "namespace": ns["name"],
            "sequence": seq,
            "published_on": meta["release_date"],
            "recorded_at": now,
            "release": meta["release_dir"],
            "canonical_uri": ns["canonical_uri"],
            "canonical_root": records.CANONICAL_ROOT,
            "deploy_id": a.deploy_id,
            "deploy_permalink": a.deploy_permalink,
            "release_commit": meta["release_commit"],
            "release_tag": meta["release_tag"],
            "release_bound_at": meta.get("bound_at"),
            "manifest_sha256": m["manifest_sha256"],
            "index_sha256": m["index_sha256"],
            "evidence": os.path.basename(a.evidence),
            "test_input": bool(meta.get("test_input")),
            "namespaces": {
                ns["name"]: {
                    "state": "published at this sequence",
                    "sequence": seq,
                    "manifest_sha256": m["manifest_sha256"],
                    "index_sha256": m["index_sha256"],
                    "first_publication_entries": m["versions_awaiting_first_publication"],
                },
                "charter": carried,
            },
            "basis": "recorded from a passing, approved live verification of every namespace "
                     "of the frozen release at the canonical address on the release date, "
                     "with the Charter verified as the published Charter and every release "
                     "object validated immediately before recording",
        }
        snap = snapshot_dir(ns, seq)
        if not os.path.isdir(snap):
            stage_snapshot_multi(ns, seq, release_dir, meta_path, a.evidence, payload)
        else:
            existing = load(os.path.join(snap, "publication.json"), "partial publication record")
            if existing.get("manifest_sha256") != m["manifest_sha256"]:
                print("PUBLICATION NOT RECORDED. The partial recording is for a different "
                      "release; it must be resolved by hand.")
                return 2
            resumed_from = existing.get("recorded_at")
            payload = existing

        first = load_or_empty(os.path.join(HERE, ns["first_publication_ledger"]),
                              f"First publication date per {ns['name']} version, recorded "
                              f"only by record_publication.py against live evidence. This is "
                              f"the {ns['name']} record's own ledger.")
        for v in m["versions_awaiting_first_publication"]:
            first["versions"].setdefault(v, {
                "first_published": meta["release_date"],
                "sequence": seq,
                "recorded_at": payload["recorded_at"],
                "evidence": f"{ns['snapshots']}/{seq}/live_verification.json",
            })
        save_json(os.path.join(HERE, ns["first_publication_ledger"]), first)

        idx = load_or_empty(os.path.join(HERE, ns["index_ledger"]),
                            f"Every {ns['name']} index made current, with its immutable "
                            f"snapshot under {ns['snapshots']}/. This is the {ns['name']} "
                            f"record's own ledger.")
        idx["versions"][str(seq)] = {
            "index_sha256": m["index_sha256"],
            "manifest_sha256": m["manifest_sha256"],
            "made_current_on": meta["release_date"],
            "recorded_at": payload["recorded_at"],
            "snapshot": f"{ns['snapshots']}/{seq}/",
            "release": meta["release_dir"],
            "deploy_id": payload["deploy_id"],
            "release_commit": payload["release_commit"],
        }
        save_json(os.path.join(HERE, ns["index_ledger"]), idx)

    if charter_ledger_bytes() != charter_before:
        print("PUBLICATION INCOMPLETE: a Charter ledger or snapshot changed during recording. "
              "This must not happen; resolve by hand before anything else.")
        return 2

    meta["published"] = True
    meta["published_on"] = meta["release_date"]
    meta["state"] = "published; recorded from live evidence"
    meta["publication_snapshots"] = {ns["name"]: f"{ns['snapshots']}/"
                                     f"{meta['namespaces'][ns['name']]['sequence']}/"
                                     for ns in built_namespaces(meta)}
    save_json(meta_path, meta)

    final, outstanding = inspect_multi(meta)
    if final != "complete":
        print(f"PUBLICATION INCOMPLETE after recording: {', '.join(outstanding)}")
        return 2

    print(f"  release {meta['release_dir']} recorded as published on {meta['release_date']}"
          + (f"  (resumed from {resumed_from})" if resumed_from else ""))
    for ns in built_namespaces(meta):
        m = meta["namespaces"][ns["name"]]
        print(f"  {ns['name']:<15} sequence {m['sequence']}, first published "
              f"{', '.join(m['versions_awaiting_first_publication']) or 'none new'}, "
              f"snapshot {ns['snapshots']}/{m['sequence']}/")
    print(f"  charter         carried unchanged at sequence {cm['sequence']}; no Charter "
          f"ledger written, no first-publication date added")
    print(f"  release commit  {meta['release_commit']}")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bind", action="store_true",
                    help="bind this frozen release to its commit and tag, before deployment")
    ap.add_argument("--note-evidence-tag", dest="note_evidence_tag", action="store_true",
                    help="record the publication-evidence tag, which exists only after recording")
    ap.add_argument("--evidence-tag", default="",
                    help="the tag on the publication-evidence commit, e.g. publication-001")
    ap.add_argument("--evidence-commit", default="",
                    help="the publication-evidence commit SHA")
    ap.add_argument("--evidence",
                    help="live verification JSON written by verify_live.py")
    ap.add_argument("--release", default="publish", help="release directory name")
    ap.add_argument("--deploy-id")
    ap.add_argument("--deploy-permalink")
    ap.add_argument("--commit", default="",
                    help="the commit that identifies the FROZEN RELEASE, created before "
                         "deployment")
    ap.add_argument("--tag", default="", help="tag on the frozen-release commit")
    ap.add_argument("--resume", action="store_true",
                    help="complete a recording that was interrupted part way")
    a = ap.parse_args(argv)

    meta_path = os.path.join(RELEASES, f"{a.release}.json")
    meta = load(meta_path, "release metadata")
    release_dir = os.path.join(HERE, a.release)

    if a.note_evidence_tag:
        return note_evidence_tag(meta, a.evidence_tag, a.evidence_commit)

    if a.bind:
        if not a.commit:
            print("NOT BOUND: --commit is required.")
            return 2
        return bind(meta, meta_path, release_dir, a.commit, a.tag)

    if not a.commit:
        print("PUBLICATION NOT RECORDED: --commit is required.")
        return 2

    missing = [n for n, v in (("--evidence", a.evidence), ("--deploy-id", a.deploy_id),
                              ("--deploy-permalink", a.deploy_permalink)) if not v]
    if missing:
        print(f"PUBLICATION NOT RECORDED: {', '.join(missing)} required.")
        return 2

    if is_multi(meta):
        return record_multi(a, meta, meta_path, release_dir)

    # 1. Validate EVERYTHING before writing anything at all.
    problems, manifest = validate_release(release_dir, meta)
    if manifest is None:
        print("PUBLICATION NOT RECORDED. Nothing was written.")
        for p in problems:
            print(f"  - {p}")
        return 2
    evidence = load(a.evidence, "live verification evidence")
    problems += check_evidence(evidence, meta, manifest)
    problems += check_binding(meta, a.commit, a.tag)

    seq = meta["sequence"]
    state, outstanding = inspect(seq, meta)
    if state == "complete":
        problems.append(f"sequence {seq} is already recorded as published; published "
                        f"sequences are immutable")
    elif state == "incomplete" and not a.resume:
        problems.append(f"sequence {seq} has an INCOMPLETE recording (outstanding: "
                        f"{', '.join(outstanding)}). Re-run with --resume to complete it. "
                        f"Nothing is lost; this is not a published sequence")
    elif state == "absent" and a.resume:
        problems.append(f"--resume was given but sequence {seq} has no partial recording")

    if problems:
        print("PUBLICATION NOT RECORDED. Nothing was written.")
        for p in problems:
            print(f"  - {p}")
        return 2

    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema": "arkaya-publication/1",
        "sequence": seq,
        "published_on": meta["release_date"],
        "recorded_at": now,
        "canonical_uri": manifest["canonical_uri"],
        "deploy_id": a.deploy_id,
        "deploy_permalink": a.deploy_permalink,
        "release_commit": meta["release_commit"],
        "release_tag": meta["release_tag"],
        "release_bound_at": meta.get("bound_at"),
        "manifest_sha256": meta["manifest_sha256"],
        "index_sha256": meta["index_sha256"],
        "evidence": os.path.basename(a.evidence),
        "basis": "recorded from a passing, approved live verification of the frozen "
                 "release at the canonical address on the release date, with every "
                 "release object validated immediately before recording",
    }

    # 2. Snapshot, staged and moved in atomically.
    snapshot = os.path.join(PUBLICATIONS, str(seq))
    if state == "absent":
        snapshot = stage_snapshot(seq, release_dir, meta, meta_path, a.evidence, payload)
        resumed_from = None
    else:
        existing = load(os.path.join(snapshot, "publication.json"), "partial publication record")
        if existing.get("manifest_sha256") != meta["manifest_sha256"]:
            print("PUBLICATION NOT RECORDED. The partial recording is for a different "
                  "release; it must be resolved by hand.")
            return 2
        resumed_from = existing.get("recorded_at")
        payload = existing

    # 3. Ledgers. Both writes are idempotent, so a resume repeats them safely.
    ledger = load_or_empty(LEDGER, "First publication date per version, recorded only by "
                                   "record_publication.py against live evidence.")
    for v in meta["versions_awaiting_first_publication"]:
        ledger["versions"].setdefault(v, {
            "first_published": meta["release_date"],
            "sequence": seq,
            "recorded_at": payload["recorded_at"],
            "evidence": f"publications/{seq}/live_verification.json",
        })
    save_json(LEDGER, ledger)

    index_ledger = load_or_empty(INDEX_LEDGER, "Every index made current, with its immutable "
                                               "snapshot under publications/.")
    index_ledger["versions"][str(seq)] = {
        "index_sha256": meta["index_sha256"],
        "manifest_sha256": meta["manifest_sha256"],
        "made_current_on": meta["release_date"],
        "recorded_at": payload["recorded_at"],
        "snapshot": f"publications/{seq}/",
        "deploy_id": payload["deploy_id"],
        "release_commit": payload["release_commit"],
    }
    save_json(INDEX_LEDGER, index_ledger)

    # 4. Mark the release last, so an interruption leaves the state visibly
    #    incomplete rather than claiming a publication whose ledgers are missing.
    meta["published"] = True
    meta["published_on"] = meta["release_date"]
    meta["state"] = "published; recorded from live evidence"
    meta["publication_snapshot"] = f"publications/{seq}/"
    save_json(meta_path, meta)

    final, outstanding = inspect(seq, meta)
    if final != "complete":
        print(f"PUBLICATION INCOMPLETE after recording: {', '.join(outstanding)}")
        return 2

    print(f"  sequence {seq} recorded as published on {meta['release_date']}"
          + (f"  (resumed from {resumed_from})" if resumed_from else ""))
    print(f"  snapshot        publications/{seq}/")
    print(f"  first published {', '.join(meta['versions_awaiting_first_publication']) or 'none new'}")
    print(f"  deploy          {payload['deploy_id']}")
    print(f"  release commit  {payload['release_commit']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except RecordError as exc:
        print(f"PUBLICATION NOT RECORDED: {exc}")
        raise SystemExit(2)
