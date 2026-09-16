# Release-sequence rehearsal, from a fresh extraction

Internal record. 16 September 2026, second rehearsal. Written because DM's decisive test for
v6 was the documented sequence run from a clean extraction, **including the successful
recording path and recovery from interruption**, alongside the negative tests. The first
rehearsal stopped at a deliberately refused recording, so it showed only that the gate says no.

**Nothing was deployed.** No Netlify project, DNS record, repository or archive request
exists. The rehearsal ran against the extracted package and, for the recording steps,
**synthetic evidence**.

## 1. Two bounds, stated before the results

**The successful recorder path was tested using synthetic evidence representing an approved
live observation. This demonstrates recorder behaviour given approval; it does not demonstrate
that publication or live verification occurred.** Genuine production approval requires HTTPS at
`record.arkayarisk.com`, which does not exist. The synthetic file carries a `NOTE` field saying
so. The shipped package's `publications/` is empty and the release is unpublished: nothing from
this rehearsal is carried into it.

**Three transport checks are not exercised by any local rehearsal** — HTTPS reachability,
HTTP redirecting to the same HTTPS address, and HSTS. The verifier lists them as *not
exercised* rather than counting them as passes, and withholds production approval from any
rehearsal.

## 2. The documented sequence, from a clean extraction

| Step | Result |
|---|---|
| A1 build | **Refused**, correctly: the shipped release is frozen and already dated today. Nothing deleted |
| A2 verify | 10 acceptance runs, each matching its declared expected outcome; rebuild comparison passed, 9 objects, 4 PDFs, no unexpected change |
| A3 package | Release checked against its freeze marker; builder, 4 inputs, README source and 12 vendored suite files hashed against their recorded identities; 10 runs re-derived from transcripts; rebuild recomputed from retained trees; production record regenerated and compared byte for byte; three suites (30 + 9 + 40 tests) passed |
| Provenance | Builder file, manifest and freeze marker now all read `311f9f11…`. In v5 the file read `311f9f11…` while both records read `faf524a0…` |
| D1 verify_live (local) | 47/47 checks, **PRODUCTION APPROVAL WITHHELD**: rehearsal over plain HTTP, and not the canonical address |
| E1 record, on that rehearsal evidence | **Refused**, naming all three reasons. Nothing written |
| B7 bind | Frozen release bound to its commit and tag; recording refuses any other pair |
| E1 record, on synthetic approved evidence and the bound commit | **Recorded.** Both ledgers written, `publications/1/` holds index, manifest, sidecar, release marker, evidence and deployment identifiers; snapshot index byte-identical to the release index |
| E1 again | **Refused**: already recorded; published sequences are immutable |
| A1 after publication | **Refused**: sequence 1 has been published; published indexes are immutable. `PVR_REPLACE_RELEASE=1` does not override it |
| E3 package after recording | Passed, carrying the ledgers and the snapshot. The release was not rebuilt |

## 2a. The release-to-publication binding

Added after the v6 review, because the commit passed at recording time was free text: written
into the snapshot, checked against nothing. Approval evidence for one frozen release could in
principle have been recorded against another. The manifest digest was already bound; the commit
was not.

| Action | Result |
|---|---|
| Record before binding | **Refused**: this release is not bound to a commit, with the `--bind` command to run |
| `--bind --commit <sha> --tag release-001` | **Bound** to manifest `b926170e…`, and prints its own limit |
| Record with a different commit | **Refused**: the commit given is not the commit bound to this frozen release |
| Record with a different tag | **Refused**: the tag given is not the tag bound |
| Record with the bound commit and tag | **Recorded.** The snapshot carries the bound commit and tag, not whatever was passed |
| Bind twice to different values | **Refused**: a frozen release is bound once; rebuild if the commit was wrong |
| Bind a release that has drifted from its marker | **Refused** |
| Bind a malformed commit | **Refused**: not a 40-character SHA |

**What the binding does not establish.** It binds an identifier supplied by the operator. It
cannot verify that the commit exists in any repository, or that the repository holds these
bytes. Step B8 — a fresh clone at the tag passing `package.py --check` — is what tests the
other half, and it is why the fresh-clone check sits before deployment rather than after it.

## 3. Interruption and recovery

Emulated a crash **after** the snapshot was in place and **before** the ledgers were written —
the exact partial state that was previously unrecoverable, because the snapshot directory
already existed and the recorder refused.

| Action | Result |
|---|---|
| Plain retry | **Refused**, and says why: `sequence 1 has an INCOMPLETE recording (outstanding: first_publication, published_indexes, release_marked). Re-run with --resume to complete it. Nothing is lost; this is not a published sequence` |
| `--resume` | **Completed**, reporting `resumed from <the original recorded_at>`. Both ledgers written, release marked |
| `--resume` again | **Refused**: already recorded |
| Staging directories left behind | none |

The transaction is staged in a temporary directory inside `publications/` and moved into place
with an atomic rename, so the state is always absent, incomplete or complete — never
ambiguous. The ledger writes are idempotent, which is what makes resume safe rather than a
second publication. A refused recording leaves no staging directory: separately tested.

## 4. Negative tests

88 tests: 30 build, 9 live-verifier, 49 gate, binding and publication. Each breaks one thing and
requires the refusal.

| What was broken | What rejects it |
|---|---|
| **The builder edited after freezing** (DM's finding 1) | Gate: the shipped builder hashes to X, the manifest records Y — rebuild and refreeze |
| An input, the README source, or a vendored suite file edited after freezing | Gate: named, with both digests |
| The freeze marker's builder block diverging from the manifest's | Gate: marker differs from manifest |
| **A run's recorded exit set to 99 with a digest failure, `as_expected` untouched** (DM's finding 2) | Gate: summary contradicts its transcript |
| **A transcript replaced with unrelated text** | Gate: transcript unreadable — no EXIT line |
| A transcript altered by one byte since it was written | Gate: altered since it was written |
| A rebuild claimed to pass while the retained trees show a changed PDF | Gate: recomputed from the trees; the claim is a separate finding |
| A required run removed from the evidence | Gate: expected run not present |
| v1.1's digest substituted into v1's row of the production record | Gate: not its deterministic regeneration |
| A sentence added to the production record claiming publication | Gate: same control |
| A served file appended to after freezing; a file served but unnamed; the freeze marker deleted | Gate: each named |
| Evidence claiming a different manifest, in every retained run | Gate: no verification run against the frozen manifest |
| **`index.json` replaced by `{}` before recording** (DM's finding 4) | Recorder: index.json does not match the manifest. Nothing snapshotted |
| An unnamed extra object in the release; a missing pointer page | Recorder: each named |
| A venue that served a different manifest | Recorder: the venue served manifest X |
| Rehearsal evidence, failed evidence, unapproved evidence, another address, another manifest, another day | Recorder: each refused by name |
| A partial recording belonging to a different release | Recorder: refuses to resume it |
| `--resume` with no partial recording | Recorder: refuses |
| Recording before the release is bound, or with a commit or tag other than the bound pair | Recorder: refuses, naming the bound values |
| Binding twice to different values, binding a drifted release, binding a malformed SHA | Recorder: each refused |
| A venue serving a **wrong manifest with a consistent sidecar** | Live verifier: served manifest does not match the frozen manifest, while the sidecar check passes |
| A venue serving **something else at `/charter/`** with `index.html` intact | Live verifier: landing page body does not match index.html |
| A tampered PDF, a missing PDF, a substituted index, a catch-all 200 responder, an exposed internal file | Live verifier: each named, and DO NOT ARCHIVE |
| An altered, missing or unexpected input; a missing README source | Builder: refuses before deleting anything |
| A date that is not the build date; the override without a reason | Builder: refuses, nothing built |
| A published sequence rebuilt, or a sequence behind the record | Builder: refuses |

## 5. Defects this round found, in my own work

**The shipped builder did not match the manifest.** I edited `build_publication_set.py` after
the release was frozen and packaged without rebuilding. The manifest and the freeze marker
both recorded the pre-edit digest and agreed with each other, which is exactly what hid it:
nothing compared either record to the file on disk. The gate now hashes the builder, every
input, the README source and every vendored suite file against their recorded identities, and
this is the first check to run after the release itself.

**The production record printed the recorded label, not the re-derived verdict.** Flipping
`as_expected` in the summary changed the record rather than being caught as a contradiction.
The record's run table is now re-read from the transcripts by the gate.

**Two tests were asserting on the wrong refusal.** Once the gate stopped trusting labels,
editing a label alone no longer caused a refusal — correct behaviour, stale assertions. Rather
than delete them I made the summary's own verdict a checked claim: the gate does not rely on
it, but a summary that ships a false claim is still a finding, because it is what a person
reads.

## 6. What this rehearsal establishes, and what it does not

**Establishes.** That the documented sequence runs from a clean extraction with no unresolved
step dependencies; that the successful recording path completes and is immutable afterwards;
that an interrupted recording is distinguishable, refuses a plain retry, and completes on
resume; that each control refuses the specific defect it claims to catch; and that the
packaged set is the set that was built and checked, by files rather than by labels.

**Disposition.** Frozen release candidate. Architecture and transaction controls rehearsed.
Publication not yet authorised or observed. Not "deployment candidate successfully verified":
the decisive verification requires HTTPS at the canonical venue.

**Does not establish.** Anything about HTTPS, DNS, Netlify, the repository, archival, or the
behaviour of `record.arkayarisk.com`. The recording path was exercised against synthetic
approved evidence, not an observed venue. Nor does any of it bear on the Charter: not §9
compliance, not the historical effectiveness of any amendment, and not constituting authority.
