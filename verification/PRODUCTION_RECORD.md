# Charter publication set: production record

Internal record. `OPS_Charter_PublicationSet_2026-09-16_v6`. Release 1, dated 2026-09-16.

**Generated from the frozen release.** This file is produced by `package.py` from
`manifest.json` and the verification results, with no reference to the clock. Packaging
regenerates it and compares byte for byte, so a figure printed against the wrong object is a
different file and is rejected. An earlier version checked only whether a digest appeared
somewhere in the evidence, and passed when v1.1's digest was substituted into v1's row.

**Status: published. Sequence 1 was recorded as published on 2026-09-16, from a passing, approved live verification of this frozen release at https://record.arkayarisk.com/charter/.**

| | |
|---|---|
| Published on | 2026-09-16 |
| Recorded at | 2026-09-16T16:51:28.097252+00:00 |
| Deploy ID | `6aaac22b28ce9dc7b8ecf61d` |
| Deploy permalink | https://6aaac22b28ce9dc7b8ecf61d--arkaya-record.netlify.app/ |
| Frozen-release commit | `89f6e53c65ae8405ed050ab92a9625206a6a819b` |
| Frozen-release tag | `release-001` |
| Live evidence | `live_verification_20260916T164917.json` |
| Immutable snapshot | `publications/1/` |

Recorded from a passing, approved live verification of the frozen release at the canonical address on the release date, with every release object validated immediately before recording.

What that does **not** establish is unchanged by publication, and is set out in section 1.

## 0. Three facts, three artefacts, not to be conflated

| Artefact | What it asserts | What it does not |
|---|---|---|
| `release-001` (tag on the frozen-release commit) | These are the bytes intended for publication | Nothing about whether they were deployed or observed |
| The live verification evidence | These bytes were observed at the canonical venue, matching this manifest object by object | Nothing about the Charter, and nothing about continuity beyond the moment of observation |
| The publication-evidence tag, recorded once it exists | The evidence record **that** publication occurred | **It is not the published object.** It necessarily post-dates the deployment it records, and must not be read as the released set |

The recorder enforces the join between the first two: a release is bound to its commit and tag
before deployment, and publication cannot be recorded unless the approval evidence carries this
manifest digest **and** the commit given is the one bound to this frozen release. The binding is
to an identifier supplied by the operator; it does not verify that the commit exists in any
repository. A fresh clone at the tag passing `package.py --check` is what tests the other half.

## 1. What these runs establish, and what they do not

**They establish that the built set satisfies the specified controls**, and that the shipped
objects stand in the recorded relationship to the recorded inputs.

**On provenance.** The manifest records the builder, its digest, the inputs with their source digests, and the build parameters. Matching digests identify the supplied builder and demonstrate that the shipped objects stand in the expected relationship to the recorded inputs. They do not independently prove that this builder historically executed, and they are not a substitute for the retained build evidence.

**They do not establish publication correctness.** Whether the historical dates are truthful, and
whether the v1.1, v2 and v3 amendments were validly effective from their stated July dates, are
separate questions and remain exactly where they were. No run below touches either.

**They say nothing about the canonical venue.** Local HTTP, one process, one machine. These runs say nothing about the behaviour of record.arkayarisk.com, which does not yet exist.

## 2. The release

| | |
|---|---|
| Release directory | `publish/` |
| Sequence | 1 |
| Release date | 2026-09-16 |
| Canonical base | `https://record.arkayarisk.com/charter` |
| Manifest SHA-256 | `b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6` |
| Index SHA-256 | `8f5fc27deb886815f2394d83d7b676616a473549b79651c1b70fc79d061c848a` |
| Published | true |
| State | published; recorded from live evidence |

The freeze marker lives at `releases/publish.json`, outside the release directory,
so nothing internal is ever served. The release is built once and packaged as built.

### What the shipped files are checked against

The builder, each input, the README source and every file of the retained acceptance suite are
hashed and compared with the identities recorded in the manifest and the verification results.
The v5 archive recorded one builder digest in both the manifest and the freeze marker while
shipping a different builder; the two records agreed with each other, and nothing compared
either of them to the file on disk.

## 3. Build provenance

| | |
|---|---|
| Builder | `build_publication_set.py` |
| Source path in the tagged repository | `build_publication_set.py` |
| Version | `2026-09-16.4` |
| SHA-256 | `311f9f110cd376d37f2d56ddde03930d7d339ae7ab7439a506f947dbeca72346` |
| Python | 3.11.15 |
| Platform | Linux-6.18.44-fc-v33-x86_64-with-glibc2.39 |
| Built at | 2026-09-16T13:47:23.974303+00:00 |

### Inputs, validated before the build touched anything

| Version | Source | SHA-256 | Bytes |
|---|---|---|---|
| v1 | `inputs/charter-v1.pdf` | `03794ff916330d36e551ccb0d98a173c5205e98c27eb35124a7466eedc776e6e` | 137,752 |
| v1.1 | `inputs/charter-v1.1.pdf` | `2d55ac0b81e07fee580e4784126c2d581b7acaec70ee55f84f5f0bec1bac0897` | 145,462 |
| v2 | `inputs/charter-v2.pdf` | `1df3e103e94515c5fbaf8792c5f09f4b539cd919ed65d7d3892d3001fc1ca12b` | 151,068 |
| v3 | `inputs/charter-v3.pdf` | `751972efbfa4fb6070b6c9b36f289211937cfcf97724511743a1e1251d752ba5` | 154,947 |

The builder holds these digests in code and checks them before it deletes or replaces anything.
A build whose inputs do not match refuses and leaves the previous set intact.

### Generated artefacts and their sources

| Shipped | Generated from | Relation | Source digest | Output digest |
|---|---|---|---|---|
| `README.md` | `README_source.md` | verbatim copy | `b666a29e9c69ff87871dd63c17946cf98cec9f3d5d3aa13b0780501c7ff23cbf` | `b666a29e9c69ff87871dd63c17946cf98cec9f3d5d3aa13b0780501c7ff23cbf` |
| `index.html` | `index.json` | rendered by builder | `8f5fc27deb886815f2394d83d7b676616a473549b79651c1b70fc79d061c848a` | `84770dcb5e0d45bca3bc5874129745378f17751925a33d5ec9befea3249127c0` |

## 4. Published objects

| Version | Path | SHA-256 | Bytes |
|---|---|---|---|
| v1 | `v1/charter-v1.pdf` | `03794ff916330d36e551ccb0d98a173c5205e98c27eb35124a7466eedc776e6e` | 137,752 |
| v1.1 | `v1.1/charter-v1.1.pdf` | `2d55ac0b81e07fee580e4784126c2d581b7acaec70ee55f84f5f0bec1bac0897` | 145,462 |
| v2 | `v2/charter-v2.pdf` | `1df3e103e94515c5fbaf8792c5f09f4b539cd919ed65d7d3892d3001fc1ca12b` | 151,068 |
| v3 | `v3/charter-v3.pdf` | `751972efbfa4fb6070b6c9b36f289211937cfcf97724511743a1e1251d752ba5` | 154,947 |

| Path | SHA-256 | Bytes |
|---|---|---|
| `index.json` | `8f5fc27deb886815f2394d83d7b676616a473549b79651c1b70fc79d061c848a` | 5,525 |
| `index.html` | `84770dcb5e0d45bca3bc5874129745378f17751925a33d5ec9befea3249127c0` | 6,678 |
| `README.md` | `b666a29e9c69ff87871dd63c17946cf98cec9f3d5d3aa13b0780501c7ff23cbf` | 5,711 |

`manifest.json`'s own digest is in `manifest.json.sha256`, since a file cannot contain its own
digest. The live verifier fetches and hashes the served manifest against this one, because a
venue serving a wrong manifest with a consistent sidecar would otherwise pass.

## 5. Build-governance corrections carried forward

Each is recorded because it shows the build process was tested, not only its output.

**The README was originally written by hand into the built tree, which the builder deletes and
recreates. The first rebuild silently removed it.** Corrected by moving the README to
`README_source.md` outside the built tree. **A file the build can destroy is not part of the
build.**

**The page renderer was a separate script**, so a set could be built without being rendered.
Folded into the builder.

**The builder deleted the output before validating its inputs.** It now validates first and
builds into a staging directory, promoting only a complete set.

**The confirmed-date check ran after promotion.** A build with a false date produced the set,
promoted it carrying that date, and only then refused. The check now runs before anything is
built. Found by the build tests, not by inspection.

**Packaging rebuilt the release before packaging it**, so the packaged set was not the set that
had been checked, and at sequence 1 the documented step failed outright. Packaging no longer
builds; reproducibility is tested by building into a separate directory.

**The builder recorded publication.** It wrote first-publication dates and marked the set
published before any deployment existed, so a failed deployment left a false record. Publication
is now recorded only by `record_publication.py`, only against live evidence.

## 6. Verification

**The suite that produced these results is retained in the package**, at `vendor/acceptance_suite/`,
12 files, digest of file digests `e86cff6681ee007c13b665b4427a065495c49980220aab09af0587ed74cbf455`.
Source: `OPS_QA_PublicVersionRecord_AcceptanceSuite_v10`.

Every run's command, working directory, exit status, full transcript and resulting baseline store
are retained under `verification/runs/20260916T153701/`. Runs are never overwritten. Spec parameters were set
explicitly for every run; the suite refuses a live run otherwise, so no result was measured
against fixture constants.

```
PVR_LINEAGE=v1,v1.1,v2,v3   PVR_EXPECTED_CURRENT=v3   PVR_ESTABLISHED=2026-09-16
PUBLIC_VERSION_RECORD_URL=http://127.0.0.1:<port>/
PVR_CONTROL_URL=http://127.0.0.1:<port>/definitely-not-here
```

**The frozen release was not mutated by any run.** The mutation and removal tests operate on a
served copy; the release directory is read-only input to the verification.

**The live evidence for this publication is recorded in `publications/1/live_verification.json`.** The runs in this section are local; they are not that evidence.

**Each run declares the outcome it must produce**, in `expectations.py`, which the harness and
this gate both import. The columns below are **re-read from the retained transcripts** by the
gate, not copied from the harness's summary: a summary that disagrees with its own transcript is
a finding, and a transcript that cannot be parsed is a finding. Observed / expected.

| Run | Exit | Checks failed | Baseline | As expected |
|---|---|---|---|---|
| `run01_first_observation` | 1 / 1 | 12, 8 / 12, 8 | baseline established | yes |
| `run02_baseline_established` | 0 / 0 | none / none | baseline advanced | yes |
| `run03_v1_mutation` | 1 / 1 | 11 / 11 | baseline HELD: observation was not clean | yes |
| `run03_v1_1_mutation` | 1 / 1 | 11 / 11 | baseline HELD: observation was not clean | yes |
| `run03_v2_mutation` | 1 / 1 | 11 / 11 | baseline HELD: observation was not clean | yes |
| `run03_v3_mutation` | 1 / 1 | 11 / 11 | baseline HELD: observation was not clean | yes |
| `run04a_object_removed` | 1 / 1 | 10 / 10 | baseline HELD: observation was not clean | yes |
| `run04b_entry_removed_from_index` | 1 / 1 | 12, 3 / 12, 3 | baseline HELD: observation was not clean | yes |
| `run05_after_restoration` | 0 / 0 | none / none | baseline advanced | yes |
| `run06_after_rebuild` | 0 / 0 | none / none | baseline advanced | yes |

### What each run is for

**`run01_first_observation`** — First observation against an empty baseline store. Checks 8 and 12 cannot be satisfied: there is no prior inventory to compare against. This run also ESTABLISHES the baseline, accepting the record as it stands. It shows the suite reporting the absence of comparison rather than passing; it is not evidence that the record was preserved.

**`run02_baseline_established`** — Second observation, record unchanged. All twelve pass because a prior inventory now exists to compare against.

**`run03_v1_mutation`** — Deliberate mutation of charter-v1.pdf in the served copy: 8 bytes appended. 03794ff916330d36e551ccb0d98a173c5205e98c27eb35124a7466eedc776e6e -> d098ec3b44b32e3869aa7d07cce7754905b10b3fe017ad806dd2409ec683d6fc. Check 11 must fail and the baseline must be HELD, so a repeat run against the altered file fails again rather than accepting it.

**`run03_v1_1_mutation`** — Deliberate mutation of charter-v1.1.pdf in the served copy: 8 bytes appended. 2d55ac0b81e07fee580e4784126c2d581b7acaec70ee55f84f5f0bec1bac0897 -> 24ecbb4fd11125bc7114ad45c158cecd06ddfcc6db55082229a7c5269cf9550a. Check 11 must fail and the baseline must be HELD, so a repeat run against the altered file fails again rather than accepting it.

**`run03_v2_mutation`** — Deliberate mutation of charter-v2.pdf in the served copy: 8 bytes appended. 1df3e103e94515c5fbaf8792c5f09f4b539cd919ed65d7d3892d3001fc1ca12b -> 90909bc70f66d81833571e6c57e5d11ddc058f6b766db2f7d9cde67a240326ef. Check 11 must fail and the baseline must be HELD, so a repeat run against the altered file fails again rather than accepting it.

**`run03_v3_mutation`** — Deliberate mutation of charter-v3.pdf in the served copy: 8 bytes appended. 751972efbfa4fb6070b6c9b36f289211937cfcf97724511743a1e1251d752ba5 -> 45602c27b1d3a8083c95a7d83d9a822193ed78618e7e57a21447b37a79dd2a68. Check 11 must fail and the baseline must be HELD, so a repeat run against the altered file fails again rather than accepting it.

**`run04a_object_removed`** — The v1.1 PDF is removed while the index still lists it. Retrievability (check 10) fails. Membership is unaffected because the index has not changed: the two failures are distinct and this run does not exercise check 12.

**`run04b_entry_removed_from_index`** — The v1.1 ENTRY is removed from the published index while the PDF remains in place. This is what a silent removal looks like from outside, and membership retention against the accepted baseline is what detects it.

**`run05_after_restoration`** — The served copy is restored to the frozen release. The run is clean again, which shows the failures above tracked the record rather than latching.

**`run06_after_rebuild`** — Observation against the independently rebuilt set. The index, the page and the four PDFs are bit-identical to the frozen release, so the preservation checks pass against the same accepted baseline.


### Rebuild reproducibility

9 objects compared against an independent rebuild
(a separate directory; the frozen release was not touched), including all 4 PDFs. Membership
identical: true.

`as_of` is a date rather than a build timestamp, so the index and the page reproduce bit for bit.
Only these carry a build time and are expected to differ:
`manifest.json`, `manifest.json.sha256`.
Objects that differed: `manifest.json`, `manifest.json.sha256`.
**Unexpected changes: none.**

## 7. Lineage

**v1, v1.1, v2, v3.** Four versions, and the published set contains no other. Checked
mechanically across every served file: no version outside that lineage is named anywhere in the
record. "v5" in the package name is the package revision, not a Charter version.
