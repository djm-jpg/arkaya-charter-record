# Publication log: release publish-008, disclosure record v7, 10 November 2026

Written by Claude in session `g6nov9` during the live sequence on 10 November 2026 (Parts B to E); Part F to follow on 11 November. Runbook: `OPS_Disclosures_LiveSequence_Runbook_v4` build 3 (SHA-256 `93e7b3322408124d213b749af02ac3c6ee540fc9e7ddfea826f525eadff3b523`), adopted for this release by PUB-8. Fields carry values observed; an unavailable field is recorded as outstanding. "Operator" means DM on his Mac; "session" means the Claude session that holds WORKING. Times are GMT, which equals UTC on this date.

This release publishes disclosure record v7 as disclosures sequence 5. It carries `/charter/` (from `publish/`) and `/get/` (from `publish-006`) byte-identical. It is the fifth disclosures publication and the fourth run under the disclosure-interval rule.

## 1. Authority and preparation (Part A, run 9 November 2026)

| Field | Value | Step |
|---|---|---|
| Publication decision | `APPROVE AR-20261109-116-g6nov9 (PUB-8)`, DM, 9 November 2026, 10:47 GMT, as amended by AR-20261109-119-g6nov9 (11:15 GMT) and AR-20261109-120-g6nov9 (11:29 GMT), and by `APPROVE AR-20261110-132-g6nov9` (10 November, 13:59 GMT), which moved the window to 14:15 to 18:15 GMT the same day. Decision record `10-Layer1-Custodian/Governance/OPS_DecisionRecord_PubRecordV7_Publication_publish-008_2026-11-10_v4.md`, 7,797 bytes, SHA-256 `5802b6e6405ccd8378898be5587207813d74879a77a2daf3221eabfb4a1b0574`; v3 kept in `_Superseded/` | A1 |
| BASE | `deeba0d8ff231b6dda62cc5f985930cd7b67872a` ("Next-day checks, publish-007"); unchanged between 9 November and the run | A2 |
| PREVIOUS_DEPLOY, PREVIOUS_RELEASE | `6adf193bad122299f280d92a`, `publish-007` | A2 |
| A3 | `package.py --check` on a fresh public clone at BASE: exit 0 (9 November) | A3 |
| A4 to A6 | Recorded as pending from DM in PUB-8 v4. **Outstanding:** no separate report of A4 to A6 is held in this log. Their checks (HEAD = BASE, clean tracked tree) were re-run in REPO by Block G at B11 and held | A4-A6 |
| A7 rehearsal | Run on builds 7, 8 and 9 (9 November). On build 9: Charter manifest unchanged; v3 to v6 byte-identical to their published digests; disclosures sequence 4 to 5; GET carried unchanged; `package.py` and `--check` exit 0. Nothing committed, filed or deployed | A7 |
| Interval rule | Run against the build 9 entry set and queue v27 plus PUB-7: every entry within its interval or disclosed as a miss (PF51-D1). Fourth run under the rule | A8 |

## 2. The freeze (Part B, 10 November 2026)

| Field | Value | Step |
|---|---|---|
| Stop point 2 | DM: "CONFIRM B1: I can complete deployment and live verification today, 10 November 2026 UTC." and "CONFIRM B4: identifiers release-009, publication-008, evidence-015, evidence-016, release name publish-008, publication date 2026-11-10. I want as much of this process automated with my overview." Both typed after AR-132 (13:59) and before the build (14:05:17Z); exact times not retained in the session record | B1-B4 |
| PUBLICATION_DATE | 2026-11-10 (UTC) | B2 |
| Identifiers | RELEASE_NAME `publish-008`; RELEASE_TAG `release-009`; PUBLICATION_TAG `publication-008`; EVIDENCE_TAG_1 `evidence-015`; EVIDENCE_TAG_2 `evidence-016` | B3 |
| Publication-state build | Build 10 from build 9: status line to APPROVED FOR PUBLICATION (PUB-8 as amended by -119, -120 and -132); seven `Disclosed` cells set to "10 Nov 2026"; Section 7 names release `publish-008`; revision row for build 10; footer to "v7 · APPROVED FOR PUBLICATION" | B5 |
| Stop point B6 | DM: "ACCEPT B6: the B5 diff of record v7 build 9 to build 10, plus the footer changed to APPROVED FOR PUBLICATION as part of the status (outside the B5 list, accepted by me), with the revision row updated to say so." | B6 |
| CARRIER_SHA, CARRIER_BYTES | `2a02e74518b45714a09f7d96a7bafaea23829735f8e7c8e2e6a53a45126b747f`, 31,334 | B6 |
| Governance filing | Build 10 filed as `10-Layer1-Custodian/Governance/Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-11-09_v7.md`; build 9 preserved as `Governance/_Superseded/…_v7_build9_SUPERSEDED_BY_build10_20261110.md` (`540a4825…73b4`); both hash-checked on the device (S9) | B7 |
| Registration | v7 entry appended to DISCLOSURE_REGISTRATION (version v7, src `conflicted-decisions-v7.md`, SHA-256 `2a02e745…747f`, 31,334 bytes, document date 2026-11-09, reason as fixed by PUB-8). One hunk in `records.py` (line 188), inside the registration markers; the carry block unchanged (GET still carried from publish-006). Registry SHA-256 after the change `17e63ccbb5430bfe7a5f608281f5d09a0168c85d9f52b74445eb18d8634f64a9` | B8 |
| Build | `build_release.py` exit 0, 14:05:17Z: charter carried sequence 1, manifest `b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6`; disclosures built sequence 5; get carried sequence 1 from publish-006, manifest `071791cc7c4a9ce27308dac097899b703d33fe9e396ea0ae3f6495d0fae5b2f1` | B9 |
| DISC_MANIFEST | `e6dcf5b2923a29e2bba484e12a3d548770a21296b039b89145d58a6ea0997a6e` | B9 |
| Gate | `package.py` exit 0 (build, verifier, gate, namespace tests ok); package 2,387,267 bytes, `776e093f…` (not committed) | B10 |
| Freeze commit | `Frozen release publish-008, 2026-11-10`: records.py, the v7 input, the `publish-008/` release directory (24 files), `releases/publish-008.json`, `verification/RELEASE_RECORD_publish-008.md`; 28 files. Test by-products and the package excluded (S10) | B10 |
| FREEZE_TREE | `e1417eef669daaa6efa98627571e594458a5cd69` | B10 |
| FREEZE_PATCH_SHA | `9a6024f45a66ded1342be09a0220d02bd961727ba909163f598b4dea29469bdb`, 882,209 bytes; apply-tested on a fresh clone at BASE; filed to 99-Working and hash-checked on the device | B10, Block F |
| Stop point 3 | Block G and P in REPO; `git am` committed at 14:18:44Z; push to `91060e8` on `main` | B11 |
| **RELEASE_COMMIT** | `91060e8ad1caf25b47aecb9778c2f173f9aa8b26`; fresh public clone: tree FREEZE_TREE, parent BASE | B11 |
| `release-009` | annotated, unsigned, tagger David McKibbin, 2026-11-10T14:21:18Z, on `91060e8a…`; fresh clone peels to RELEASE_COMMIT | B12 |
| Bound | `record_publication.py --bind`, exit 0, 14:21:46Z | B13 |
| VERIFY `~/arkaya-verify-publish-008` at `release-009` | peels to RELEASE_COMMIT; `package.py --check` exit 0 (operator's screenshot, read by the session) | B14-B16 |

## 3. Deployment (Part C)

| Field | Value | Step |
|---|---|---|
| Published deploy before upload | `6adf193bad122299f280d92a`, equal to PREVIOUS_DEPLOY; auto publishing locked. Read through the Netlify API by the session | C2-C3 |
| Upload | One, by DM by drag and drop, in project `arkaya-record` (site `9f499435-fd4f-4b74-851f-d7659e91ca73`): deploy created 14:36:21Z, "5 new files uploaded", source `drop` | C4 |
| **DEPLOY_ID** | `6af32be53a9d08d0cae6a6db` | C5 |
| DEPLOY_PERMALINK | https://6af32be53a9d08d0cae6a6db--arkaya-record.netlify.app | C5 |
| Preview verification | `verify_live.py` on the permalink (DM, VERIFY): 162/162 passed, PRODUCTION APPROVAL: WITHHELD solely for the non-canonical address; evidence `live_verification_20261110T143830.json` (VERIFY, not committed, S10). Output filed as `00-Group/99-Working/OPS_C6_VerifyPreview_publish-008_2026-11-10.txt` | C6-C7 |
| Published to production | `published_at` 2026-11-10T14:40:03.686Z, `locked: true` (Netlify API). Published by DM **before** the typed production decision; see section 7 item 5 | C8-C9 |
| Production decision | DM, 14:43 GMT: "APPROVE AR-20261110-133-g6nov9 (C8), typed after I published deploy 6af32be53a9d08d0cae6a6db at 14:40 UTC in Netlify project arkaya-record, auto publishing locked. Record the sequence as it happened." | C8 |
| Live verification | `verify_live.py` on `https://record.arkayarisk.com/`: 162/162, PRODUCTION APPROVAL: GRANTED, 14:43:12Z. Output filed as `00-Group/99-Working/OPS_C10_VerifyLive_publish-008_2026-11-10.txt` | C10 |
| EVIDENCE | `live_verification_20261110T144312.json`, 34,659 bytes, SHA-256 `dbadea3e604f1c8da50641b6b812b28aedbbfa72770141277ab7b6e24de05527`; copied to 99-Working and hash-checked in the session; base canonical, `rehearsal: false`, `test_input: false`, `passed: true`, `production_approval: true` | C11-C13 |
| Approval | DM, 14:44 GMT: "ACCEPT C15: production approval for publish-008 … D1: record the publication." Within S6 | C14-C15 |

## 4. Record (Part D)

| Field | Value | Step |
|---|---|---|
| Stop point 7 | DM, 14:44 GMT: "D1: record the publication." | D1 |
| `record_publication.py` | exit 0, 14:46:06Z: release recorded as published on 2026-11-10; disclosures sequence 5, first published v7, snapshot `ledgers/disclosures/publications/5/`; Charter and GET carried unchanged, none of their ledgers written | D2 |
| D3 | `ledgers/disclosures/first_publication.json` records v7 at 2026-11-10, sequence 5, evidence `ledgers/disclosures/publications/5/live_verification.json`; `git diff --quiet RELEASE_COMMIT -- first_publication.json published_indexes.json publications publish` silent at the root (Charter) and in `ledgers/get`; `releases/publish-008.json` records `published: true` | D3 |
| Gate after recording | `PVR_RELEASE=publish-008 package.py` exit 0; package 2,408,124 bytes, `d5a10b7c…` (not committed). A first run without `PVR_RELEASE` gated the Charter instead; see section 7 item 6 | D4 |
| Publication commit | `Publication of publish-008, 2026-11-10`: the disclosures first-publication and index ledgers, snapshot 5, `releases/publish-008.json`, `verification/RELEASE_RECORD_publish-008.md`, and EVIDENCE under `verification/live/`; 17 files. Eighteen test by-products excluded (S10) | D4 |
| PUBLICATION_TREE | `80ee8318c5a6720858d4114abfc1e60ef5918c26` | D4 |
| PUBLICATION_PATCH_SHA | `27ad00f0c782e53ea7c1fb9b72f8f558b64ed0561a820265e5f48cc62f90ec27`, 115,928 bytes (`OPS_Patch_publish-008_Publication_2026-11-10_v1.patch`); apply-tested on a fresh clone at RELEASE_COMMIT (tree PUBLICATION_TREE); filed to 99-Working, hash-checked on the device | D4, Block F |
| Stop point 8 | Block G and P in REPO: G2 to G6 OK; `git am` committed at 14:55:13Z; push `91060e8..d827f7c main -> main` | D5 |
| **PUBLICATION_COMMIT** | `d827f7c9d392bf4be5848d4937edef44d7de2a2c`; fresh clone: tree PUBLICATION_TREE, parent RELEASE_COMMIT | D5 |
| `publication-008` | annotated, unsigned, tagger David McKibbin, 2026-11-10T14:56:55Z, on `d827f7c9…`; absent locally and remotely before creation; fresh clone peels to PUBLICATION_COMMIT | D6 |
| Evidence tag noted | exit 0, 14:57:34Z, in WORKING at PUBLICATION_COMMIT: "disclosures sequence 5 evidence tag recorded: publication-008"; the change to `ledgers/disclosures/published_indexes.json` is carried into the Part E evidence commit | D7 |
| VERIFY2 `~/arkaya-verify2-publish-008` at `publication-008` | peels to `d827f7c9…`; `PVR_RELEASE=publish-008 package.py --check` exit 0, every suite ok (about 15:02 GMT). The session's fresh clone at the tag gave the same result | D8-D9 |

## 5. Preserve and baseline (Part E)

| Field | Value | Step |
|---|---|---|
| Stop point 9 | DM, 15:10 GMT: "E1: proceed to Part E for publish-008." Typed after the captures below; see section 7 item 7 | E1 |
| Internet Archive | Seven captures by DM at https://web.archive.org/save, each "Done": `https://web.archive.org/web/20261110150349/https://record.arkayarisk.com/` (the Archive noted a delay in registering this snapshot); `https://web.archive.org/web/20261110150600/https://record.arkayarisk.com/disclosures/`; `https://web.archive.org/web/20261110150635/https://record.arkayarisk.com/disclosures/index.json`; `https://web.archive.org/web/20261110150704/https://record.arkayarisk.com/disclosures/index.html`; `https://web.archive.org/web/20261110150742/https://record.arkayarisk.com/disclosures/manifest.json`; `https://web.archive.org/web/20261110150803/https://record.arkayarisk.com/disclosures/manifest.json.sha256`; `https://web.archive.org/web/20261110150849/https://record.arkayarisk.com/disclosures/conflicted-decisions/v7/conflicted-decisions-v7.md` (marked "First Archive"). Timestamps are UTC, from the capture links; evidence is DM's screenshots, read by the session. Before submission the session fetched all seven URLs (200) and the served carrier's SHA-256 equalled CARRIER_SHA | E2 |
| Software Heritage | `https://github.com/djm-jpg/arkaya-charter-record`, origin type git, submitted by DM: "accepted and will be processed as soon as possible". Read through the Software Heritage API at 15:10 GMT: request 2636786, 2026-11-10T15:09:28Z, `succeeded`, snapshot `swh:1:snp:dbad6762574dcfadd984d4be559dae81c7885a47`, holding `main` at `d827f7c9…` and `release-009` and `publication-008` (the latter targeting PUBLICATION_COMMIT). It predates `evidence-015` | E3 |
| Charter comparison | Section 6 command of the runbook in WORKING at PUBLICATION_COMMIT, 15:10 GMT: 12 of 12 PASS, CREDITED 12/12, "baseline advanced"; output `verification/live/charter_comparison_publish-008_E4.txt`; `verification/live/pvr_snapshot_live.json` updated; tracked `vendor/` files restored | E4 |
| Evidence commit | `Baseline and publication log, publish-008`: this log, the Charter comparison output and snapshot, and the D7 ledger change. This log is inside the commit it describes, so BASELINE_TREE and the patch hash are reported to DM at E5 and entered here at Part F | E5 |
| BASELINE_COMMIT, `evidence-015` | Outstanding: entered at Part F | E6 |
| Next-day checks | Scheduled for Wednesday 11 November 2026 | E7 |

## 6. What is public

`https://record.arkayarisk.com/disclosures/` serves disclosure record v7 as sequence 5: `conflicted-decisions/v7/conflicted-decisions-v7.md` (SHA-256 `2a02e745…747f`, 31,334 bytes), registered with the reason fixed by PUB-8 ("Successor issue: discloses decisions taken since v6, including the dispositions of the GET v6 comments, formal entries for decisions v6 disclosed in substance, and four control failures, one of them a missed interval. v3's to v6's entries are not repeated and are not superseded; v3 to v6 remain published and unchanged."). v3 to v6 are served byte-identical to their published objects. `/charter/` and `/get/` are unchanged.

## 7. Deviations and findings

1. **Morning window missed.** Stop point 2 was put at 08:46 GMT to the Claude chat only and was not confirmed within 09:00 to 13:00 GMT. AR-20261110-132-g6nov9 (13:59) moved the window to 14:15 to 18:15 GMT the same UTC day (PUB-8 v4); S6 and the 10 November interval were both met. The delivery failure is the subject of AR-20261110-131-g6nov9 (stop-point delivery rule), not yet decided. AR-129 and AR-130 were withdrawn unapproved.
2. **S8 combined blocks.** At DM's direction at B4 ("as much of this process automated with my overview"), Blocks G, P and T and the VERIFY checks were given as single command lines that stop at the first mismatch, not one command per line. Every check named by the block was still run and printed. For runbook v5: provide combined blocks as the standard form.
3. **Footer changed at B5**, outside the B5 list, accepted by DM at B6. Third recurrence (publish-005, publish-007). For runbook v5: add the footer to B5's list.
4. **C2 read through the Netlify API**, not the Deploys page. During C4 DM first opened project `arkaya-risk` (the website); nothing was clicked there and the upload went to `arkaya-record`.
5. **Production publication preceded its typed authority.** The deploy was published at 14:40:03Z; the typed production decision (AR-20261110-133-g6nov9) followed at 14:43 GMT, recording the sequence. The publication followed a passing preview verification (162/162 at 14:38:30Z, approval withheld only for the address), and live verification then passed at the canonical address. This is a control failure against the runbook's C8 order and is queued for the record after v7. For runbook v5: put the C8 line to DM before revealing the "Publish deploy" control, and state that the click is the last act of C8.
6. **D4 gate first run without `PVR_RELEASE`.** The session's first gate gated the Charter default, not publish-008. It changed no tracked file; its archive was deleted and the gate re-run correctly before the commit. For runbook v5: write D4 as `PVR_RELEASE=RELEASE_NAME python3 package.py`.
7. **E2 and E3 submitted before the typed E1.** The session put E1 to DM with the URLs at about 15:02 GMT; DM made the captures from 15:03 and typed E1 at 15:10. The acts were the ones E1 authorises and nothing else ran ahead of it.
8. **Terminal screenshots as evidence** for Blocks G, P and T and the VERIFY and VERIFY2 checks, as at publish-007. Every value was re-read by the session on a fresh public clone.
9. **Part A items A4 to A6** are not separately evidenced in this log (section 1).

Two acts preceded their typed authority in this run (items 5 and 7). Every push and tag followed the line it depended on.

*AKR AIPS · PUBLICATION_LOG_publish-008 · session g6nov9 · 10 November 2026*
