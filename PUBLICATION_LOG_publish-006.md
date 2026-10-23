# Publication log: release publish-006, GET editorial revision v6 published for comment, 20 October 2026

Sections 0 to 5 written by Claude in session j7bham during and after the live sequence on 20 October 2026; sections 6 and 7 (Parts E and F) to follow. Runbook: `OPS_Disclosures_LiveSequence_Runbook_v4` build 3 (SHA-256 `93e7b3322408124d213b749af02ac3c6ee540fc9e7ddfea826f525eadff3b523`), to be adopted for this release by typed decision at B1. Fields carry values observed; an unavailable field is recorded as outstanding. "Operator" means DM on his Mac; "session" means the Claude session that holds WORKING.

This release will carry `/charter/` and `/disclosures/` byte-identical from their published releases and publish the GET schema record as sequence 1, serving editorial revision v6 build 3 at `/get/1.0.1-public-draft-v6/Arkaya_GET_Schema_v6.json`. It is the first release built by the pipeline's next version (C3).

## 0. The pipeline release, and a departure from the runbook

| Field | Value |
|---|---|
| Authority | `ACCEPT AR-20261020-008-j7bham`, DM, 20:55 BST (release of C3 on the session's re-run evidence; publication of v6 build 3 on D10 and the founder's s177(6)(a) judgement; Simon Hudson not advised) |
| Base | `publication-005`, commit `f5aa2cb0717896a6b8dc41976b6c3b8a896bab86`, 386 files |
| Patch | `C3_next_version_combined.diff`, 217,998 bytes, SHA-256 `53c83949d67c257475def849a9e20ecb57b63627612d8cb50ba97f9832284117`; `git apply --check` clean; 12 files; operator verified hash and file count independently on his Mac (21:41 BST) |
| Session tests | full discovery 219 OK, 322.9 s (pre-rebase); 219 OK, 338.6 s (rebased); focused 25 OK after rebase |
| Branch and PR | `c3-next-version` pushed by the session at `bdcc026bde89dd669af2a91c592812219cbffd47` (rebased onto main's publish-005 close-out `863c2da4`, diff byte-identical to the step 6 check sheet); PR #1 merged by DM, rebase-and-merge, 21:37 BST |
| Merged commit | `789262e5a9b6d050e20b2832b1ccf0c27eb10ccb`, single parent `863c2da4`, tree `a20ce363bcb18eb69ed5f4f15bc736a8931668ba` equal to `bdcc026b`'s tree |
| `release-006` | annotated, unsigned, on `789262e5…`, tagger DM, 21:41 BST (tag object `55ffb822ff6a475a6ab0f7cfd9b401cd864e3153`). Session's own push of the tag was refused HTTP 403 by the `publication-tags` ruleset, as designed; nothing reached the remote from that attempt |
| **Departure** | The runbook places the release tag on the freeze commit (B10 to B12). `release-006` was placed on the pipeline code commit before any freeze, following the session's own 17-step outline in the release record rather than the runbook. Under S3 the tag stays. B3 therefore yields **RELEASE_TAG `release-007`** for the publication freeze; `release-006` is recorded here as the pipeline code release, never itself published, as `release-004` was recorded for the frozen, never-published `publish-004` |
| Identifiers expected at B3 | RELEASE_NAME `publish-006`; RELEASE_TAG `release-007`; PUBLICATION_TAG `publication-006`; EVIDENCE_TAG_1 `evidence-010`; EVIDENCE_TAG_2 `evidence-011` |

## 1. Authority and preparation (Part A, run 20 October 2026 evening)

| Field | Value | Step |
|---|---|---|
| Publication decision | `ACCEPT AR-20261020-008-j7bham` (20:55 BST) naming v6 build 3, SHA-256 `c1e1d4f74a5f892d09766235a474046f95f06c5f39f308b81336259ce79c8ae5`; rights statement fixed by `ACCEPT AR-20261020-005-j7bham` (19:31 BST); placement and slug fixed by `ACCEPT GETV6-7` (21:46 BST). Decision record filed 22:06 BST: `10-Layer1-Custodian/Governance/OPS_DecisionRecord_GETv6_PublicationForComment_publish-006_2026-10-20_v1.md`, SHA-256 `8c8fb2aa7c78066125d3846624383dab947b843a587951ed99db50e01cef7dc5`, hash-checked on the device | A1 |
| BASE | `789262e5a9b6d050e20b2832b1ccf0c27eb10ccb` (remote main = `release-006`) | A2 |
| PREVIOUS_DEPLOY, PREVIOUS_RELEASE | `6ad784d07912d63c015c1353`, `publish-005` (published 16:16 BST, 20 October) | A2 |
| A3 `package.py --check` on a fresh public clone at BASE, tests on | exit 0 (a3_check.log, HEAD `789262e5…`; build, verifier, gate and namespace tests ok) | A3 |
| A4 to A6 | Run in REPO 22:13 BST: `git pull --ff-only` (12 files from the C3 merge), HEAD = BASE, 219 tests OK in 172.7 s, tracked tree clean | A4-A6 |
| A7 rehearsal `publish-006-rehearsal` on `release-006` (scratch clone) | build exit 0; Charter manifest `b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6` unchanged; disclosures **carried** from publish-005 sequence 3, manifest `9c0c1777479f867a5562532d508874e656acfb56e6d8a341ce5c546c6c07e2b9`, byte-identical; GET built sequence 1, manifest `be988c0898de39c6b4addf2726e3d8c604608f8326ee8eadff780aa9c91f2cf3`; schema served byte-exact (`c1e1d4f7…8ae5`, 28,325 bytes); no `/get/1.0`; `package.py` exit 0 (build, verifier, gate, namespace tests all ok); package `OPS_Record_Release_publish-006-rehearsal_2026-10-20.tar.gz` 2,296,037 bytes, `697cac29…`. Rehearsal registry `records.py` SHA-256 `b70ab2fbcdbaa9ee2ebc5d3e7f48fc6707fd7a69d6e25b2160e7d9ef99d3c5cd`: GET entry (version `1.0.1-public-draft-v6`, src `Arkaya_GET_Schema_v6.json`, document date 2026-10-13, `application/schema+json`, Status = publication notice, Reason = AR-005 rights statement) and CARRY_REGISTRATION for disclosures. **Nothing from the rehearsal committed, filed or deployed.** This rehearsal is also the loopback check with the real v6 bytes that the AR-20261020-002 receipt recorded as not reproduced | A7 |
| Interval rule | Checked against `OPS_DisclosureQueue_2026-10-20_v17` (SHA-256 `1a5e965a…`) 22:08 BST: no new disclosure issue in this release (disclosures carried); no j7bham decision yet has a queue row. Rows due for v18: AR-20261020-005, -006, -008 and GETV6-7 (entries, due Tue 27 Oct), -004, -007, -009, -010 (filings and production decision), Q-5 (clause 5, tag before freeze) and Q-6 (clause 5, publish before typed approval). The record after v5 is due Mon 26 October | A8 |

## 2. The freeze (Part B)

| Field | Value | Step |
|---|---|---|
| Stop point 2 | DM, 22:08 BST: "I can complete deployment and live verification today, 20 October 2026 (UTC)"; runbook v4 build 3 adopted for publish-006 only; identifiers publish-006, release-007, publication-006, evidence-010, evidence-011 | B1-B4 |
| PUBLICATION_DATE | 2026-10-20 (UTC) | B2 |
| Carrier | `Arkaya_GET_Schema_v6.json`, 28,325 bytes, SHA-256 `c1e1d4f74a5f892d09766235a474046f95f06c5f39f308b81336259ce79c8ae5`; no publication-state build (the carrier is the schema bytes; the notice and rights statement are registry fields), so B5 to B7 do not apply as written | B5-B7 |
| Registration | GET entry `1.0.1-public-draft-v6` (document date 2026-10-13, `application/schema+json`, Status = publication notice, Reason = AR-005 rights statement) and CARRY_REGISTRATION for disclosures (publish-005, sequence 3, `9c0c1777…2b9`); `git diff records.py` confined to the two blocks; registry SHA-256 `b70ab2fbcdbaa9ee2ebc5d3e7f48fc6707fd7a69d6e25b2160e7d9ef99d3c5cd`, equal to the A7 rehearsal | B8 |
| Build | exit 0; Charter manifest `b926170e…2ac6`; disclosures carried, manifest `9c0c1777…2b9`; GET_MANIFEST `071791cc7c4a9ce27308dac097899b703d33fe9e396ea0ae3f6495d0fae5b2f1`; no `/get/1.0` | B9 |
| Gate | `package.py` exit 0; package `OPS_Record_Release_publish-006_2026-10-20.tar.gz` 2,295,796 bytes, `a1ffa1b6…` | B10 |
| FREEZE_TREE | `ad57dabe92c7e5ccc946c8886c7ca04fbcd35c3f`. A first freeze commit (tree `e897525c…`, patch `bc80f207…`) omitted `verification/RELEASE_RECORD_publish-006.md` and failed Block F step 2 (`package.py --check` exit 2 on the fresh clone); corrected by amending the unpushed local commit; both trees on record | B10 |
| FREEZE_PATCH_SHA | `9cf360dfdf0f9828ecb4be0da1fd55473f4c6b3ff1eed4955ad3b9d6c2f1de6f`, 811,125 bytes; apply-tested on a fresh clone at BASE (tree FREEZE_TREE, `--check` exit 0); filed to DROP and hash-checked on the device | B10, Block F |
| Stop point 3 | Block G and P in REPO, 22:24 BST: HEAD = BASE, clean, patch hash equal, `git am` clean, tree = FREEZE_TREE, push `789262e..678aad8 main -> main` | B11 |
| **RELEASE_COMMIT** | `678aad800ba9849fa26651b927a107de7aa03fd3`; fresh public clone: tree FREEZE_TREE, parent BASE | B11 |
| `release-007` | annotated, unsigned, tagger DM, 22:26 BST, on `678aad80…`; absent locally and remotely before creation | B12 |
| Bound | 22:27 BST, exit 0 | B13 |
| VERIFY `~/arkaya-verify-publish-006` at `release-007` | peels to RELEASE_COMMIT; Charter manifest and GET manifest equal; `package.py --check` exit 0 | B14-B16 |

## 3. Deployment (Part C)

| Field | Value | Step |
|---|---|---|
| Stop point 4 | DM, 22:34 BST | C1 |
| Published deploy before upload | `6ad784d07912d63c015c1353`, "Published & locked"; auto publishing already locked | C2-C3 |
| Uploads | Three. (1) `6ad7df0122dc5ff4e813dde0`, 22:37 BST: the whole VERIFY clone was dragged, not the release folder; preview served the release at `/publish-006/` and repository files (`/ledgers/…` 200); `verify_live.py` 68/123, WITHHELD, 55 failed (evidence `live_verification_20261020T213940.json`, VERIFY); never published. (2) `6ad7e02edba1f12f5de09b83`, 22:42 BST: a multi-item Finder selection was dragged; the deploy served nothing at any path; never published. (3) `6ad7e1575794138d4ceee5ab`, 22:47 BST: a zip of the `publish-006` folder's contents (`zip -r ~/Desktop/publish-006.zip .` inside the folder) was dragged; file browser showed `charter` (9), `disclosures` (7), `get` (5), `index.html` at the root. The runbook's C4 says drag the folder; the zip carried the same bytes and C6/C7 proved the result | C4-C5 |
| **DEPLOY_ID** | `6ad7e1575794138d4ceee5ab` | C5 |
| DEPLOY_PERMALINK | https://6ad7e1575794138d4ceee5ab--arkaya-record.netlify.app | C5 |
| Production still PREVIOUS_DEPLOY after upload | yes | C5 |
| Preview verification | `verify_live.py` on the permalink: 156/156 passed, approval withheld solely for the non-canonical address; session's object comparison: root pointer, both carried manifests, GET manifest, index.json, index.html and schema byte-identical to the release; `/get/1.0`, `/get/1.0/`, `/publish-006/`, `/ledgers/…`, `/records.py` all 404 | C6-C7 |
| Production decision | **The deploy was published at about 22:49 BST before the typed line arrived.** `APPROVE AR-20261020-010-j7bham` was typed at 22:50 BST and is recorded as ratifying. Act before authority: the Q-4 pattern; queued as Q-6 (clause 5) | C8 |
| Published to production | "Published & locked deploy", 10:47 PM deploy, publishing locked | C8 |
| Live verification | `verify_live.py` on `https://record.arkayarisk.com/`: 156/156, PRODUCTION APPROVAL: GRANTED, exit 0, 21:52:50Z; session's canonical fetch 21:50:50Z byte-identical for every object | C10 |
| EVIDENCE | `live_verification_20261020T215250.json`, 32,793 bytes, SHA-256 `104435b2dfd6f42dad211dee506e814a94f12f5a8607fe2cc75896e877231f10`; copied to DROP (exit 0) and hash-checked on the device; base canonical, not a rehearsal, no test input, `passed: true`, `production_approval: true` | C11-C13 |
| Approval | granted 20 October 2026 (UTC), within S6; stop point 6 accepted by DM 22:54 BST | C14-C15 |

## 4. Record (Part D)

| Field | Value | Step |
|---|---|---|
| Stop point 7 | DM, 22:54 BST | D1 |
| `record_publication.py` | exit 0, 21:54:26Z: GET sequence 1 recorded, first published `1.0.1-public-draft-v6` on 2026-10-20, snapshot `ledgers/get/publications/1/`; Charter and disclosures ledgers untouched | D2 |
| D3 | `ledgers/get/first_publication.json` records the version at PUBLICATION_DATE; `git diff --quiet RELEASE_COMMIT -- first_publication.json published_indexes.json publications publish ledgers/disclosures` silent; `releases/publish-006.json` records `published: true` | D3 |
| Gate after recording | `package.py` exit 0; package 2,309,399 bytes, `82447b0d…` | D4 |
| PUBLICATION_TREE | `a092ba009a97d19a48d95667e0400fa848a54ffe`; commit carries only GET ledgers and snapshot, marker, release record and the approval evidence (17 files); nine test by-products excluded (S10) | D4 |
| PUBLICATION_PATCH_SHA | `3ec4f03017741080467288456204b3b0d9b3dd38520dd556e100daaa1000457d`, 108,616 bytes; apply-tested on a fresh clone at RELEASE_COMMIT (`--check` exit 0); filed to DROP, hash-checked | D4, Block F |
| Stop point 8 | Block G and P in REPO, 23:13 BST: all checks held; push `678aad8..98da026 main -> main` | D5 |
| **PUBLICATION_COMMIT** | `98da0263d27e4b55934e3109fc6284714e4ed021`; fresh clone: tree PUBLICATION_TREE, parent RELEASE_COMMIT | D5 |
| `publication-006` | annotated, unsigned, tagger DM, 23:14 BST, on `98da0263…` | D6 |
| Evidence tag noted | exit 0, 23:15 BST; the resulting change to `ledgers/get/published_indexes.json` is carried into the Part E evidence commit | D7 |
| VERIFY2 `~/arkaya-verify2-publish-006` at `publication-006` | peels to PUBLICATION_COMMIT; `package.py --check` exit 0 | D8-D9 |

## 5. What is public

`https://record.arkayarisk.com/get/` serves the GET schema record, sequence 1: editorial revision v6 build 3 at `/get/1.0.1-public-draft-v6/Arkaya_GET_Schema_v6.json` (SHA-256 `c1e1d4f7…8ae5`), Status carrying the publication notice (public draft for comment, 21 days from publication, not approved, not a candidate, v5 remains the current candidate), Reason carrying the AR-005 rights statement in David McKibbin's name. `/get/1.0` is not served. `/charter/` and `/disclosures/` are unchanged. The comment period runs to 10 November 2026.

## 6. Open after tonight

Part E (evidence commit with the D7 ledger change, Software Heritage save, baseline, `evidence-010`) and Part F (next-day comparison, `evidence-011`, publication log filed in Governance, closing note): tomorrow. Queue v18 rows (section 1, A8). The two unpublished preview deploys stay in the Netlify history. The runbook deviations of this run, for the queue and for the next runbook revision: tag before freeze (release-006), production publish before the typed line (Q-6), zip upload in place of the folder drag at C4, and the first freeze commit's omission of the release record.

## 7. Preserve and baseline (Part E, 22 October 2026)

Sections 7 to 9 were written by Claude on 22 October 2026 in a later session. Sections 0 to 6 above are the 20 October draft reproduced byte for byte (SHA-256 `6689186db847dde43bf9f59b219bb3d777149012f558f7f8738b0da9f438036a`, 14,113 bytes) from the `j7bham` session's own record of how it was written. That draft was sent to DM on 20 October but never filed, and the session's working copy no longer exists; the reproduction was checked against both hashes the session reported (Part A `81f3d2ed…68c4`, full draft `6689186d…036a`).

| Field | Value | Step |
|---|---|---|
| Stop point 9 | DM, 13:23 BST, 22 October: `APPROVE P-D7` … "Proceed with Part E now; Part F tomorrow morning before 13:00" | E1 |
| D7 evidence-tag note, lost and re-run | The D7 run of 20 October (23:15 BST, exit 0) wrote its change to `ledgers/get/published_indexes.json` in the `j7bham` session's working copy, which no longer exists; the change was never committed. Under `APPROVE P-D7` it was re-run on 22 October in a fresh public clone at PUBLICATION_COMMIT: `record_publication.py --note-evidence-tag --release publish-006 --evidence-tag publication-006 --evidence-commit 98da0263d27e4b55934e3109fc6284714e4ed021`, exit 0, `evidence_tag_recorded_at` `2026-10-22T12:23:38.602846+00:00`. The ledger entry therefore carries the 22 October time, not 20 October. Recorded as a deviation (section 8) | D7 (re-run) |
| Internet Archive | Seven captures by DM at https://web.archive.org/save, 22 October 2026, each "Done" on first submission: `https://web.archive.org/web/20261022122511/https://record.arkayarisk.com/`; `https://web.archive.org/web/20261022122642/https://record.arkayarisk.com/get/`; `https://web.archive.org/web/20261022122819/https://record.arkayarisk.com/get/index.json`; `https://web.archive.org/web/20261022122927/https://record.arkayarisk.com/get/index.html`; `https://web.archive.org/web/20261022122956/https://record.arkayarisk.com/get/manifest.json`; `https://web.archive.org/web/20261022123116/https://record.arkayarisk.com/get/manifest.json.sha256`; `https://web.archive.org/web/20261022123240/https://record.arkayarisk.com/get/1.0.1-public-draft-v6/Arkaya_GET_Schema_v6.json`. The six `/get/` captures are marked "First Archive". Timestamps are UTC, from the capture links; evidence is DM's screenshots of each confirmation page | E2 |
| Software Heritage | `https://github.com/djm-jpg/arkaya-charter-record`, origin type git, submitted by DM at about 13:33 BST, 22 October: "The 'save code now' request has been accepted and will be processed as soon as possible." A request, not preservation: no SWHID yet. Read at F4 | E3 |
| Charter comparison | Section 6 command of the runbook in the fresh clone, 12:23:48Z: 12 of 12 PASS, "baseline advanced"; output `verification/live/charter_comparison_publish-006_E4.txt`; `verification/live/pvr_snapshot_live.json` updated (observation and baseline `at` 2026-10-22T12:23:48Z); tracked `vendor/` files restored | E4 |
| Evidence commit | `Baseline and publication log, publish-006`: this log, the Charter comparison output and snapshot, and the D7 ledger change. BASELINE_TREE and patch below | E5 |
| BASELINE_TREE, BASELINE_PATCH_SHA | This log is inside the commit it describes, so it cannot name that commit's tree or patch. Both are reported to DM at E5 and entered here at Part F (section 9) | E5, Block F |
| BASELINE_COMMIT, `evidence-010` | Entered at Part F (section 9), from Block G, P and T | E6 |
| Next-day checks | Scheduled for Friday 23 October, before the 13:00 BST publication run | E7 |

## 8. Deviations and findings

1. **Release tag before the freeze** (Q-7): `release-006` on the pipeline commit; the publication carries `release-007` (section 0).
2. **Production publish before the typed line** (Q-6): about 22:49 BST against `APPROVE AR-20261020-010-j7bham` at 22:50 BST (section 3).
3. **Upload by zip** after two wrong drags left two unpublished preview deploys in the Netlify history (section 3).
4. **First freeze commit omitted the release record**; corrected before push (section 2).
5. **The 20 October publication log draft and the D7 ledger change were held only in a session working copy and lost with it.** Neither was filed or committed on 20 October. The log is reproduced byte-exact (section 7); the D7 note was re-run with a true 22 October timestamp.
6. **Parts E and F ran late.** Part E was due on 21 October and ran on 22 October; Part F, the next-day check, was due on 21 October and is scheduled for 23 October. Nothing public changed in the interval; the Charter comparison of 22 October passed 12 of 12. Part F ran on 23 October from 13:49 BST, after the 09:30 slot and after the "before 13:00" set at stop point 9; the 13:00 publication run waited for it.

7. **F3 ran before F1.** The Charter comparison (F3) ran at 12:49:25Z and the authoritative live verification (F1) at 13:18:03Z; the runbook orders F1 first. Both read the same served state: F1 found every one of the 15 served objects byte-identical to the 20 October evidence, so the order changes nothing the checks establish.

## 9. Next-day checks (Part F)

Written by Claude on 23 October 2026.

| Field | Value | Step |
|---|---|---|
| Baseline, from Part E | BASELINE_COMMIT `91a39b81ec9753445aff2daa901e9c526c59a2dc`; BASELINE_TREE `28fdfeb1e2d6f3a178d4085e5ff359ae30b59cc3`; BASELINE_PATCH_SHA `45c06604…` (`OPS_BaselinePatch_publish-006_2026-10-22.patch`, 27,808 bytes, 99-Working), applied by DM at Block G, pushed at Block P | E5, Block F, E6 |
| `evidence-010` | Annotated, unsigned, tag object `af77bb85fc421e5fa61b6728428738d249336e12` on BASELINE_COMMIT; tagger David McKibbin, 2026-10-22T13:08:20Z; pushed by DM at Block T | E6 |
| Authoritative live verification | VERIFY `~/arkaya-verify-publish-006` on the operator's machine against `https://record.arkayarisk.com/`, 2026-10-23T13:18:03Z: **156/156 checks passed, PRODUCTION APPROVAL: GRANTED**, exit 0 | F1 |
| Evidence | `verification/live/live_verification_20261023T131803.json`, 32,793 bytes, SHA-256 `d95e5c19c4f1f0ae48abe25abc05cc17934ebd073d040f74fdc7c9e853201c10`; copied to DROP by the operator, hashed on the device and again in the session, equal | F1-F2 |
| Evidence fields | canonical base; release `publish-006`, frozen; `rehearsal: false`; `test_input: false`; `passed: true`; `production_approval: true`; no approval blockers, no findings, no unexercised checks; root pointer local and served `eaa510f9…73fb`, unchanged from 20 October; manifests published, local and served equal for charter `b926170e…2ac6` (carried), disclosures `9c0c1777…e2b9` (carried from publish-005) and GET `071791cc…b2f1` (built); all 15 served objects byte-identical to `live_verification_20261020T215250.json` | F2 |
| Charter comparison | Section 6 command of the runbook, 2026-10-23T12:49:25Z: exit 0, live **12/12 PASS**, current `v3`, 4 versions; "baseline advanced"; `verification/live/pvr_snapshot_live.json` now `706eede6b74309fc6e2c8e1828654e33031c88ec6d18128f72c97933d4e5dbc4`. Full output `verification/live/charter_comparison_publish-006_F3.txt` (5,378 bytes, SHA-256 `d51d2bf34d443bf8a0ba9dc89c305fef28e3fc8abfd0ed14d72c8b317df22c34`), byte-identical to the E4 output. Ran before F1 (section 8, item 7) | F3 |
| SWHID | Snapshot `swh:1:snp:ffd366d9050226eef723b3d07c8cb96962cb78ac`, visit 2026-10-22T12:33:33Z, read from the Software Heritage archive on 23 October. It holds `main` at `98da026` (PUBLICATION_COMMIT), `release-007`, `publication-006`, `release-006`, `publication-005` and `evidence-009`. It was taken before BASELINE_COMMIT and `evidence-010` were pushed, so it preserves the publication but not this baseline; neither `evidence-010` nor `evidence-011` is preserved there until a later visit | F4 |

**Result.** The published state held unchanged from 20 to 23 October: all three namespaces served their frozen bytes, the Charter passed its acceptance suite, and no finding arose. This commit carries the next-day evidence and is tagged `evidence-011`.
