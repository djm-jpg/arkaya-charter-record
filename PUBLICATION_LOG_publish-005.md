# Publication log: release publish-005, the conflicted-decisions disclosure record v5

Written at step E5 of `OPS_Disclosures_LiveSequence_Runbook_v4` (build 3, SHA-256 `93e7b3322408124d213b749af02ac3c6ee540fc9e7ddfea826f525eadff3b523`), adopted for this release only under `APPROVE AR-20261020-006-zhzg8v`, 20 October 2026. Fields carry the values observed and reported during execution. An unavailable field is recorded as outstanding, not left blank or inferred. "Operator" means DM on his machine; "session" means the Claude session that holds WORKING.

This release carries `/charter/` byte-identical from the published release, carries disclosure v3 and v4 byte-identical, and publishes disclosure v5 as sequence 3 of the `/disclosures/` record. The Charter's own log is `PUBLICATION_LOG.md`, which this release does not change.

**publish-005 is the retry of publish-004.** `publish-004` was frozen (`release-004`, `e8ddef15b4f37d58bd17121fb8fbe46b12acc0ab`) and deployed, but its deploy went live before the preview checks and the production decision, served nothing at the canonical paths, and was rolled back under the restoration procedure before anything was recorded (Section 10, item 1). It was never published. The retry restarted at B1 with new identifiers under `ACCEPT RETRY-1 (a)`, DM, 15:47 BST.

## 1. Authority and preparation

| Field | Value | Step |
|---|---|---|
| Run date | `ACCEPT RUN-1`, DM, 14:54 BST: the run moved to 20 October | - |
| Runbook adoption | `APPROVE AR-20261020-002-zhzg8v` for `publish-004` only (14:58 BST); `APPROVE AR-20261020-006-zhzg8v` for `publish-005` only (15:49 BST) | - |
| Publication decision | `APPROVE AR-20261020-007-zhzg8v`, DM, 15:51 BST, on the terms of `APPROVE AR-20261020-003-zhzg8v` (15:03 BST, for `publish-004`); recorded in `10-Layer1-Custodian/Governance/OPS_DecisionRecord_PubRecordV5_Publication_publish-005_2026-10-20_v1.md` (SHA-256 `5d022f3e…`) | A1 |
| Part A | run once, for `publish-004`, and relied on for the retry: A2 BASE `b4e36d37491761d143b6dd0a1a33b96c6a4fc2f7` (remote main = `evidence-008`); A3 `package.py --check` on a fresh clone exit 0; A4 to A6 on the operator's machine: already up to date, HEAD equal to BASE, 162 tests `OK`, tracked tree clean; A7 rehearsal (`publish-004-rehearsal`, carrier v5 build 7) build and package exit 0 | A2-A7 |
| BASE for the retry | `e8ddef15b4f37d58bd17121fb8fbe46b12acc0ab`, the `publish-004` freeze commit, frozen and never published | B |
| Retry rehearsal | `publish-005-rehearsal` on `e8ddef1`: build exit 0, `package.py` exit 0; nothing committed, filed or deployed | - |
| PREVIOUS_DEPLOY, PREVIOUS_RELEASE | `6ad10611834ef8909c7a9c79`, `publish-003` (restored to production at 15:41 BST after the `publish-004` incident) | A2, R2 |
| Interval rule (A8) | run against queue v14 for `publish-004`; entries due 22 October carried in v5 within interval; the `Q-2` lapse disclosed; open items after build 8 (V5INC-1 to V5INC-3, CDX-SLATE C3) assigned to the record after v5, due 26 October 2026 | A8 |

## 2. The release

| Field | Value | Step |
|---|---|---|
| Stop point 2 and identifiers | DM, 15:54 BST: `publish-005`, `release-005`, `publication-005`, `evidence-009`, `evidence-010`; publication date 2026-10-20 | B1-B4 |
| PUBLICATION_DATE | 2026-10-20 (UTC) | B2 |
| Carrier | build 10 (publication state, from pre-freeze build 8 `661693b4…be13`), 16,336 bytes, SHA-256 `a4362e1e9fa0ea481f3340d54a9f840dbdf7b4efcab6fef79b5413f0e5a0d1fa`; diff against build 8 confined to the status line (naming AR-20261020-007, 15:51 BST), four Disclosed cells, the closing sequence and the revision row; accepted by DM at 15:54 BST | B5-B6 |
| Carrier filed | `10-Layer1-Custodian/Governance/` as `…_v5.md`, hash-checked on the device; build 9 (`4e62c19b…58ed`, never published) moved to `_Superseded/` as `…_v5_build9_SUPERSEDED_BY_build10_20261020.md` under `APPROVE AR-20261020-009-zhzg8v` | B7 |
| Registration | v5 entry only; reason: "Successor issue: discloses decisions taken since v4, two corrections to v4 and one disclosure-queue lapse. v3's and v4's entries are not repeated and are not superseded; v3 and v4 remain published and unchanged." | B8 |
| Builder | `build_release.py` `2026-09-28.1`, SHA-256 `d973186ccf98bd63a22815cf0eaf8b36915e51caf01e44779bf3555717765f6d` | B9 |
| Registry SHA-256 | `d06577b1d1faea8be0667cc2c6a7f78e40acbc5aa9333c421f861c3010f459b7` | B9 |
| Built at | 2026-10-20T14:54:26Z | B9 |
| Date-mismatch override | none | B9 |
| Root pointer SHA-256 | `5c2a1b8c55c16183d4a94deff459617f48394346ce69254550d33ba2206dd787`, unchanged | B9 |
| Charter manifest (carried) | `b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6`, equal to the published manifest | B9 |
| v3 and v4 objects | `10400912d65cf1bfd584322874d7f178949d209f0157072908be872076926c64` and `27e0f46a33025cd16e4375d965d79f1ddd5e12c63d9b0ffe3d4e321f875c39ec`, equal to their published digests | B9 |
| Disclosures manifest (DISC_MANIFEST) | `9c0c1777479f867a5562532d508874e656acfb56e6d8a341ce5c546c6c07e2b9` | B9 |
| Disclosures index SHA-256 | `6d35a4fa7fdd393e84f795aa4c923d47244d9d5581970f5b9fbfc5c85c232e6a` | B9 |
| FREEZE_TREE | `08f2efddbbb8d00f6681c70deb41bb5f1ec076d2` | B10 |
| FREEZE_PATCH_SHA | `c659b00f83b24e7f2063a2f2641035bc04b3025a23d15ea99efc85ecbd7c047c`, 742,557 bytes; apply-tested on a fresh clone at BASE (`package.py --check` exit 0); filed to DROP under `APPROVE AR-20261020-007-zhzg8v FREEZE FILE manifest ccfeaba1…` and hash-checked on the device | B10 |

## 3. Frozen-release commit, before deployment

| Field | Value | Step |
|---|---|---|
| Tree after `git am` in REPO | equal to FREEZE_TREE | B11 |
| Push | `e8ddef1..a7ebe84 main -> main`; confirmed on a fresh public clone (tree FREEZE_TREE, parent BASE) | B11 |
| **RELEASE_COMMIT** | `a7ebe843aa8fd17e204dad95c404635f8c70401b` | B11 |
| `release-005` | annotated, **unsigned**, on `a7ebe843…`; absent locally and on the remote before creation | B12 |
| Bound (`--bind`) | 2026-10-20T15:09:26Z, exit 0 | B13 |
| VERIFY `~/arkaya-verify-publish-005` at `release-005` | tag peels to RELEASE_COMMIT; both manifests equal; `package.py --check` exit 0 | B14-B16 |

## 4. Deployment

| Field | Value | Step |
|---|---|---|
| Stop point 4 | DM, 16:09 BST | C1 |
| Published deploy before upload | `6ad10611834ef8909c7a9c79` (connector) | C2 |
| Auto publishing | locked before upload; still locked after publication | C3, C8 |
| Upload | Netlify Drop, under click-by-click steps after the `publish-004` incident | C4 |
| **DEPLOY_ID** | `6ad784d07912d63c015c1353`, created 2026-10-20T15:12:16Z | C5 |
| DEPLOY_PERMALINK | https://6ad784d07912d63c015c1353--arkaya-record.netlify.app | C5 |
| Production still PREVIOUS_DEPLOY after upload | yes (connector; `published_at` empty); the deploy serves `disclosures/` at its root | C5 |
| Preview verification (operator) | 106/106 checks; approval withheld solely for the non-canonical address | C6 |
| Preview comparison (session) | root pointer, both manifests, v3, v4 and v5 served byte-identical to the release | C7 |
| Production decision | `APPROVE AR-20261020-010-zhzg8v`, DM, 16:15 BST | C8 |
| Published to production | "Published & locked deploy" observed 16:16 BST | C8 |

## 5. Authoritative live verification and recording

| Field | Value | Step |
|---|---|---|
| Stop point 5 | DM, 16:17 BST | C9 |
| Verified address | `https://record.arkayarisk.com/`, from VERIFY on the operator's machine | C10 |
| Result | 106/106 checks passed, exit 0; **PRODUCTION APPROVAL: GRANTED**; no blockers, no findings, no unexercised checks | C10 |
| EVIDENCE | `verification/live/live_verification_20261020T151749.json`, 23,246 bytes, verified at 2026-10-20T15:17:49Z; filed to DROP under `APPROVE AR-20261020-010-zhzg8v C11 FILE` | C11 |
| EVIDENCE_SHA | `8b8bd6d47aabfebab702c75ceb13c131080eab04a172212c5d43f7a10d46c572`; equal on the operator's copy, the filed copy and WORKING | C13 |
| Evidence fields | canonical base; `rehearsal: false`; `test_input: false`; `passed: true`; `production_approval: true` | C13 |
| Approval accepted; recording authorised | DM, 16:23 BST | C15, D1 |
| Recorded | 2026-10-20T15:24:18Z, exit 0, first attempt | D2 |
| Disclosures first publication | `v5` first published 2026-10-20, disclosures sequence 3, snapshot `ledgers/disclosures/publications/3/`; `v3` and `v4` unchanged | D3 |
| Charter ledgers, snapshots and `publish/` untouched | yes (`git diff --quiet` exit 0) | D3 |
| `releases/publish-005.json` | `published: true` | D3 |
| Package after recording | `OPS_Record_Release_publish-005_2026-10-20.tar.gz`, 1,731,215 bytes, SHA-256 `a25df2a7ad831890…` (not committed) | D4 |

## 6. Publication-evidence commit

| Field | Value | Step |
|---|---|---|
| PUBLICATION_TREE | `e9b66e9d940520f0ae600d7cbcdadce98a716be7` | D4 |
| PUBLICATION_PATCH_SHA | `e43f50e5c98ff197c7d3eb525c7a4f790eab5f2e1db0e9350fdacfda2ea5051e`, 80,719 bytes; apply-tested on a fresh clone at `a7ebe84` (`package.py --check` exit 0); filed to DROP and hash-checked on the device | D4, D5 |
| Tree after `git am` in REPO | equal to PUBLICATION_TREE | D5 |
| Push | `a7ebe84..f5aa2cb main -> main`; confirmed on a fresh public clone (tree PUBLICATION_TREE, parent RELEASE_COMMIT) | D5 |
| **PUBLICATION_COMMIT** | `f5aa2cb0717896a6b8dc41976b6c3b8a896bab86` | D5 |
| Filing and push authority | `APPROVE AR-20261020-007-zhzg8v PUBLICATION FILE manifest fe42a138…`, typed 16:37 BST, ratifying acts run at 16:36 BST (Section 10, item 4) | D5 |
| `publication-005` | annotated, **unsigned**, on `f5aa2cb…`; absent locally and on the remote before creation | D6 |
| Evidence tag noted | exit 0, 2026-10-20T15:38:45Z, written to the disclosures index ledger only | D7 |
| VERIFY2 `~/arkaya-verify2-publish-005` at `publication-005` | tag peels to PUBLICATION_COMMIT; `package.py --check` exit 0 | D8-D9 |

## 7. Commits and tags

| Identifier | Value |
|---|---|
| `release-004` | `e8ddef15b4f37d58bd17121fb8fbe46b12acc0ab`, frozen `publish-004`; **never published** (Section 10, item 1) |
| `release-005` | `a7ebe843aa8fd17e204dad95c404635f8c70401b`, frozen-release commit |
| `publication-005` | `f5aa2cb0717896a6b8dc41976b6c3b8a896bab86`, publication-evidence commit |
| `evidence-009` | the commit carrying this log; named at the close-out, because a commit cannot name itself |
| `evidence-010` | the next-day close-out; named in the closing note |

`publication-004` was never created.

## 8. Preservation

| Capture | Wayback timestamp (UTC) | Step |
|---|---|---|
| `https://record.arkayarisk.com/` | `20261020154404`, reported by Save Page Now ("A snapshot was captured") with the notice that registration is delayed and lookups may redirect to an earlier version for now. Not yet confirmed by a lookup; the root pointer is byte-identical to earlier captures (`5c2a1b8c…d787`) | E2 |
| `/disclosures/` | `20261020154631` | E2 |
| `/disclosures/index.json` | `20261020154705` | E2 |
| `/disclosures/index.html` | `20261020154740` | E2 |
| `/disclosures/manifest.json` | `20261020154818` | E2 |
| `/disclosures/manifest.json.sha256` | `20261020154841` | E2 |
| `/disclosures/conflicted-decisions/v5/conflicted-decisions-v5.md` | `20261020155016` ("First Archive") | E2 |

Each capture is at `https://web.archive.org/web/<timestamp>/https://record.arkayarisk.com/<path>`.

| Field | Value | Step |
|---|---|---|
| Software Heritage "save code now" | origin `https://github.com/djm-jpg/arkaya-charter-record`, type git; request **accepted** ("will be processed as soon as possible"), 16:51 BST (15:51Z), before the commit carrying this log existed | E3 |
| SWHID | outstanding; read at F4 | F4 |

## 9. Charter comparison after deployment

| Field | Value | Step |
|---|---|---|
| Command | the runbook appendix command, unchanged, against `https://record.arkayarisk.com/charter/` | E4 |
| Result | exit 0; live run **12/12 PASS**, current `v3`, 4 versions, no silent revision, entry digests match, membership retained | E4 |
| Baseline | advanced, clean observation at 2026-10-20T15:43:02Z; `verification/live/pvr_snapshot_live.json` now `3fc98fbb316cad7b2c3c727a6bb8ec64853bb6e1535d63d83081ffd375eb7a27` | E4 |
| Full output | `verification/live/charter_comparison_publish-005_E4.txt` | E4 |

## 10. Deviations and findings

1. **The `publish-004` deployment went live unchecked and was rolled back.** The session's C4 instruction was not clear enough: the operator dragged the whole checking clone rather than the release folder, and the resulting deploy `6ad77b99fee3b2e44359b1a0` was published to production at 14:35:50Z, before C6, C7 and any production decision (`AR-20261020-005` was never typed and is void). It served the release one folder too deep, so the canonical paths returned 404 from 14:35:50Z to about 14:41Z (about six minutes). R0 confirmed nothing had been recorded; R2 republished `6ad10611…` (15:41 BST); R3 and R4 (`publish-003`, 103/103, approval granted) confirmed restoration; R5 failure note `OPS_FailureNote_publish-004_Restoration_2026-10-20_v1.md` (SHA-256 `ec3866ac…`) filed to DROP under `APPROVE AR-20261020-003-zhzg8v R5 FILE`. The retry used click-by-click Netlify steps. Recorded as a control failure in disclosure queue v16.
2. **`release-004` and the never-published freeze remain in the history.** Under S3 no tag is moved or deleted; `publish-005` is built on `release-004`'s commit as BASE.
3. **The `publish-005` freeze was pushed before B7 and the queue v16 filing.** The runbook places B7 before B8. The operator pushed the freeze (16:02 BST) before the filing under `AR-20261020-009` had run; the session had not held the push for confirmation. The filing completed at 16:04 BST, hash-checked on the device. The released bytes were unaffected: the carrier in the freeze is the build 10 accepted at B6.
4. **The D5 filing and push ran before the typed authority.** The operator ran the publication-patch filing and Block G/P at 16:36 BST; the typed line naming the pack manifest arrived at 16:37 BST, ratifying them. Every value matched what was presented (PATCH_SHA, PUBLICATION_TREE, BASE).
5. **Request-ID irregularity.** The generator skipped `AR-20261020-008` once and issued it later; `008` was voided unused and never presented. `005` is void (issued for `publish-004` C8, never typed).
6. **The session's first D5 download step assumed `~/Downloads`.** The pack saved to the home folder; a replacement command found it. Nothing was run on a wrong file.
7. **Evidence placed in WORKING by reconstruction.** The session could not stage the filed evidence directly; it rebuilt the file from the Drive copy and checked it byte for byte (SHA-256 and size equal to EVIDENCE_SHA) before recording.
8. **Local test by-products excluded.** Nine `verification/live/live_verification_20261020T1524*.json` files written by `package.py`'s test stages against `127.0.0.1` are not committed (S10). The E4 run's tracked acceptance-suite cache changes were reverted (`git checkout -- vendor`); it also left four untracked cache files (`vendor/acceptance_suite/__pycache__/*.cpython-313.pyc`), which `package.py` refused as unrecorded (exit 2) and which were removed before packaging, as for `publish-003`.
9. **v3 and v4 labelled "superseded" in the public index.** As for `publish-003`: the builder marks every earlier version superseded. v5 does not supersede v3's or v4's entries; the registration reason says so, and AR-20261020-003 accepted the label. A pipeline change for successor-type records remains a finding for a later work order.
10. **This log is not in the package.** `package.py` packages `PUBLICATION_LOG.md` by name, not this file. Its integrity rests on this commit and on the `.sha256` sidecar filed at F7.

## 11. Next-day checks (Part F)

Outstanding at the time of writing: F1 canonical verification, F2 evidence check, F3 Charter comparison re-run, F4 SWHID, and any capture outstanding in Section 8.
