# Publication log: release publish-007, disclosure record v6, 26 October 2026

Written by Claude in session `k4r9te` during the live sequence on 26 October 2026 (Parts A to E); Part F to follow on 27 October. Runbook: `OPS_Disclosures_LiveSequence_Runbook_v4` build 3 (SHA-256 `93e7b3322408124d213b749af02ac3c6ee540fc9e7ddfea826f525eadff3b523`), adopted for this release by `APPROVE PUB-7` (23 October 2026, 16:45 BST). Fields carry values observed; an unavailable field is recorded as outstanding. "Operator" means DM on his Mac; "session" means the Claude session that holds WORKING. Times are GMT (UK clocks changed on 25 October).

This release publishes disclosure record v6 as disclosures sequence 4, and carries `/charter/` (from `publish/`) and `/get/` (from `publish-006`) byte-identical. It is the fourth disclosures publication and the third run under the disclosure-interval rule.

## 1. Authority and preparation (Part A, run 25 October 2026)

| Field | Value | Step |
|---|---|---|
| Publication decision | `APPROVE PUB-7`, DM, 23 October 2026, 16:45 BST. Decision record `10-Layer1-Custodian/Governance/OPS_DecisionRecord_PubRecordV6_Publication_publish-007_2026-10-23_v1.md`, 3,303 bytes, SHA-256 `6661fbed6fe8e94ff50639fc386633e791ad83e39807900821d6d5efae251665`, naming carrier build 12 `cc8d9db4e17b2484c87d4a927d3200cc0df62c04080e7c40889333cfdbc7e8ee` and queue v24 `a8ec71d9a25f568c8c94397c1d1ae7e3f9c898bfbe29df46b443060423ddea2d` | A1 |
| BASE | `9d12371410feb590840c842e34dedf35583b22cc` ("Next-day checks, publish-006"); unchanged between the 25 October pre-flight and the 26 October run | A2 |
| PREVIOUS_DEPLOY, PREVIOUS_RELEASE | `6ad7e1575794138d4ceee5ab`, `publish-006` (from `PUBLICATION_LOG_publish-006.md`) | A2 |
| A3 | `package.py --check` on a fresh public clone at BASE, tests on: exit 0 (25 October, session `xqmby5`) | A3 |
| A4 to A6 | Run by DM in REPO on 25 October: HEAD = BASE, 219 tests OK, tracked tree clean (reported to session `xqmby5`) | A4-A6 |
| A7 rehearsal | `rehearsal-007` in a scratch clone at BASE, 25 October: Charter manifest unchanged; v3, v4, v5 objects byte-identical to publish-005; sequence 3 to 4; served v6 object `cc8d9db4…e8ee`; GET carried byte-identical (`071791cc…b2f1`); `package.py` and `--check` exit 0. Nothing committed, filed or deployed | A7 |
| Interval rule | Checked against queue v24, 25 October: entries due 26 October (V5INC-1 to V5INC-3, CDX-SLATE (a) C3), 27 October (the 20 October decisions, GETV6-7, STOP-2, WEBPUB-1, Q-10) and 29 October (GETV6-COMMENT) all met by publication on 26 October; no miss. Third run under the rule; the rule's review falls after this run | A8 |
| Pre-run decision D1 (25 October, session `xqmby5`) | `ACCEPT D1 (a)`: step B8 is read as "confined to the two registration blocks" for publish-007, because the freeze must also change the carry block (drop the disclosures carry, now built; add the GET carry from publish-006). Logged to the Action Register on 25 October. Runbook deviation for v5 (section 7) | B8 |

## 2. The freeze (Part B, 26 October 2026)

| Field | Value | Step |
|---|---|---|
| Stop point 2 | DM, 08:46 GMT: "CONFIRM B1: I can complete deployment and live verification today, 26 October 2026 UTC. CONFIRM B4: identifiers publish-007, release-008, publication-007, evidence-013, evidence-014, PUBLICATION_DATE 2026-10-26, BASE 9d12371." Carriers re-verified on the device at 08:46 (record build 12, queue v24, runbook build 3: all equal to PUB-7) | B1-B4 |
| PUBLICATION_DATE | 2026-10-26 (UTC) | B2 |
| Identifiers | RELEASE_NAME `publish-007`; RELEASE_TAG `release-008`; PUBLICATION_TAG `publication-007`; EVIDENCE_TAG_1 `evidence-013`; EVIDENCE_TAG_2 `evidence-014` (`evidence-012` reserved under PF5-1); last tags before the run `release-007`, `publication-006`, `evidence-011` | B3 |
| Publication-state build | Build 13 from build 12. Diff confined to: status line (approved form, naming `APPROVE PUB-7` and release publish-007; "For independent check before the publication run" removed); eight `Disclosed` cells "[publication date]" to "By this publication, 26 Oct 2026"; Section 7 closing sequence "as the next release" to "as release `publish-007`"; revision row for build 13; footer "v6 build 12 · DRAFT" to "v6 · APPROVED FOR PUBLICATION" (the v5 form). Five hunks, 23 changed lines | B5 |
| Stop point B6 | DM, 08:48 GMT: "ACCEPT B6 … CARRIER_SHA 746e4952301b7c56a1b52572a4913c88b67cc1f0a5de1c54a06b855d9979bfbe, CARRIER_BYTES 33133" | B6 |
| CARRIER_SHA, CARRIER_BYTES | `746e4952301b7c56a1b52572a4913c88b67cc1f0a5de1c54a06b855d9979bfbe`, 33,133 | B6 |
| Governance filing | Build 13 filed as `10-Layer1-Custodian/Governance/Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-10-22_v6.md`; build 12 preserved as `_Superseded/…_v6_build12_SUPERSEDED_BY_build13_20261026.md`; both hash-checked on the device (S9) | B7 |
| Registration | v6 entry appended to DISCLOSURE_REGISTRATION (version v6, src `conflicted-decisions-v6.md`, SHA-256 `746e4952…9fbe`, 33,133 bytes, document date 2026-10-22, reason as fixed by PUB-7); CARRY_REGISTRATION: disclosures carry removed, GET carried from publish-006 at sequence 1, manifest `071791cc7c4a9ce27308dac097899b703d33fe9e396ea0ae3f6495d0fae5b2f1`. `git diff records.py`: two hunks (lines 184, 225), both inside the registration markers; published v3, v4, v5 entries unchanged. Registry SHA-256 after the change `ec1a1f59cc52b3ecd0bb2bcb05d6b48cd936609b290cdc138c151ca48fc5f2fc` | B8 |
| Build | `build_release.py` exit 0, 08:49:53Z: charter carried sequence 1 manifest `b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6` (equal to Section 2 of the runbook); disclosures built sequence 4; get carried sequence 1 manifest `071791cc…b2f1`, `diff -r` against publish-006 identical. v3, v4, v5 served objects byte-identical to publish-005 (`cmp`). v6 served object SHA-256 `746e4952…9fbe` | B9 |
| DISC_MANIFEST | `ff0c3dab1ac4fb9a5144298ecec2c52c1882b336beeffc64c0be328ce779b6aa` | B9 |
| Gate | `package.py` exit 0 (build, verifier, gate, namespace tests ok); package `OPS_Record_Release_publish-007_2026-10-26.tar.gz` 2,342,775 bytes, `b4b97df8…` (not committed) | B10 |
| Freeze commit | `Frozen release publish-007, 2026-10-26`: records.py, the v6 input, the `publish-007/` release directory (24 files), `releases/publish-007.json`, `verification/RELEASE_RECORD_publish-007.md`; 27 files. Nine test by-products and the package excluded (S10) | B10 |
| FREEZE_TREE | `f4a22930ac523adea62ba0b7b908cc32f5ef7f10` | B10 |
| FREEZE_PATCH_SHA | `69a3ca9c146782efa8f9b0de4b93138a13de4649ed06fd23023cf6f925914cc1`, 851,512 bytes; apply-tested on a fresh clone at BASE (tree FREEZE_TREE, `--check` exit 0); filed to DROP and hash-checked on the device | B10, Block F |
| Stop point 3 | Block G and P in REPO, about 08:59 GMT: HEAD = BASE, tracked tree clean, patch hash equal, `git am` clean, tree = FREEZE_TREE, push `9d12371..8afb76e main -> main` | B11 |
| **RELEASE_COMMIT** | `8afb76ebf376887a54e03cc94697ecc4b09f6bb4`; fresh public clone: tree FREEZE_TREE, parent BASE | B11 |
| `release-008` | annotated, unsigned, tagger DM, about 09:01 GMT, on `8afb76eb…`; absent locally and remotely before creation; fresh clone peels to RELEASE_COMMIT | B12 |
| Bound | `record_publication.py --bind`, exit 0, 09:02 GMT | B13 |
| VERIFY `~/arkaya-verify-publish-007` at `release-008` | peels to RELEASE_COMMIT; Charter manifest `b926170e…2ac6`; disclosures manifest DISC_MANIFEST; `package.py --check` exit 0 (09:07 GMT) | B14-B16 |

## 3. Deployment (Part C)

| Field | Value | Step |
|---|---|---|
| Stop point 4 | DM, 09:07 GMT: "PROCEED C1" | C1 |
| Published deploy before upload | `6ad7e1575794138d4ceee5ab`, "Published & locked deploy", 20 October; equal to PREVIOUS_DEPLOY. Auto publishing already locked from publish-006 ("Unlock to start auto publishing" shown); not touched | C2-C3 |
| Upload | One. The `publish-007` folder from VERIFY, revealed in Finder by the session and dragged by DM onto the project overview drop area, 09:11 GMT: "5 new files uploaded" (the v6 object, disclosures index.html, index.json, manifest.json, manifest.json.sha256; all other files already held by earlier deploys) | C4 |
| **DEPLOY_ID** | `6adf193bad122299f280d92a` | C5 |
| DEPLOY_PERMALINK | https://6adf193bad122299f280d92a--arkaya-record.netlify.app | C5 |
| Production still PREVIOUS_DEPLOY after upload | yes ("Published on Oct 20", "Publish deploy" offered on the new deploy) | C5 |
| Preview verification | `verify_live.py` on the permalink (DM, VERIFY): 159/159 passed, PRODUCTION APPROVAL: WITHHELD solely for the non-canonical address, evidence `live_verification_20261026T091436.json` (VERIFY, not committed, S10). Session's fetch of the preview: root pointer, Charter manifest, disclosures index.json, index.html, manifest.json, manifest.json.sha256, the v6 object and the GET manifest byte-identical to the release | C6-C7 |
| Production decision | `APPROVE PUB-7-C8-k4r9te`, DM, 09:15 GMT, typed before the deploy was published | C8 |
| Published to production | "Publish deploy" clicked after the typed line; DM confirmed 09:15 GMT: "deploy 6adf193bad122299f280d92a is Published and locked; auto publishing still locked" | C8-C9 |
| Live verification | `verify_live.py` on `https://record.arkayarisk.com/`: 159/159, PRODUCTION APPROVAL: GRANTED, exit 0, 09:17:35Z. Session's canonical fetch at about 09:16Z: seven objects byte-identical to the release | C10 |
| EVIDENCE | `live_verification_20261026T091735.json`, 33,694 bytes, SHA-256 `775195530fe187cc6461af89ff69f5b7e33babcd496224e90e7241952b91800d`; copied to DROP (exit 0) and hash-checked on the device; base canonical, `rehearsal: false`, `test_input: false`, `passed: true`, `production_approval: true` | C11-C13 |
| Approval | granted 26 October 2026 (UTC), within S6; stop point 6 accepted by DM 09:19 GMT | C14-C15 |

## 4. Record (Part D)

| Field | Value | Step |
|---|---|---|
| Stop point 7 | DM, 09:19 GMT: "PROCEED D1" | D1 |
| `record_publication.py` | exit 0, 09:19:43Z: release recorded as published on 2026-10-26; disclosures sequence 4, first published v6, snapshot `ledgers/disclosures/publications/4/`; Charter carried unchanged, no Charter ledger written; GET carried unchanged, none of its ledgers written | D2 |
| D3 | `ledgers/disclosures/first_publication.json` records v6 at 2026-10-26, sequence 4, evidence `ledgers/disclosures/publications/4/live_verification.json`; `git diff --quiet RELEASE_COMMIT -- first_publication.json published_indexes.json publications publish` silent; `releases/publish-007.json` records `published: true` | D3 |
| Gate after recording | `package.py` exit 0; package 2,360,349 bytes, `fb57704b…` (not committed) | D4 |
| Publication commit | `Publication of publish-007, 2026-10-26`: the disclosures first-publication and index ledgers, snapshot 4 (12 files), `releases/publish-007.json`, `verification/RELEASE_RECORD_publish-007.md`, and EVIDENCE under `verification/live/`; 17 files. Sixteen test by-products excluded (S10) | D4 |
| PUBLICATION_TREE | `935a0e1dd5f38ae2d1177ddc35bca0980879f8ae` | D4 |
| PUBLICATION_PATCH_SHA | `9217bd0b395206c820a3e5034b127e2ce8612abecda574ff31a40d804901ee81`, 112,338 bytes; apply-tested on a fresh clone at RELEASE_COMMIT (tree PUBLICATION_TREE, `--check` exit 0); filed to DROP, hash-checked | D4, Block F |
| Stop point 8 | Block G and P in REPO, about 09:27 GMT: all checks held; push `8afb76e..33e9615 main -> main` | D5 |
| **PUBLICATION_COMMIT** | `33e961598610719f5e22efdf415d7d676112f778`; fresh clone: tree PUBLICATION_TREE, parent RELEASE_COMMIT | D5 |
| `publication-007` | annotated, tagger DM, about 09:30 GMT, on `33e96159…`; fresh clone peels to PUBLICATION_COMMIT | D6 |
| Evidence tag noted | exit 0, 09:35 GMT, in WORKING at PUBLICATION_COMMIT: "disclosures sequence 4 evidence tag recorded: publication-007"; the resulting change to `ledgers/disclosures/published_indexes.json` is carried into the Part E evidence commit | D7 |
| VERIFY2 `~/arkaya-verify2-publish-007` at `publication-007` | HEAD `33e9615`; `package.py --check` exit 0 (09:34 GMT) | D8-D9 |

## 5. Preserve and baseline (Part E)

| Field | Value | Step |
|---|---|---|
| Stop point 9 | DM, 09:35 GMT: "PROCEED E1" | E1 |
| Internet Archive | Seven captures by DM at https://web.archive.org/save, 26 October 2026, each "Done": `https://web.archive.org/web/20261026093918/https://record.arkayarisk.com/`; `https://web.archive.org/web/20261026094015/https://record.arkayarisk.com/disclosures/`; `https://web.archive.org/web/20261026094101/https://record.arkayarisk.com/disclosures/index.json`; `https://web.archive.org/web/20261026094130/https://record.arkayarisk.com/disclosures/index.html`; `https://web.archive.org/web/20261026094211/https://record.arkayarisk.com/disclosures/manifest.json`; `https://web.archive.org/web/20261026094630/https://record.arkayarisk.com/disclosures/manifest.json.sha256`; `https://web.archive.org/web/20261026094349/https://record.arkayarisk.com/disclosures/conflicted-decisions/v6/conflicted-decisions-v6.md` (marked "First Archive"). The first attempt at 09:38 GMT returned the Internet Archive's "Temporarily Offline" page and was resubmitted; no capture was skipped. Timestamps are UTC, from the capture links; evidence is DM's screenshots of each confirmation page, read by the session | E2 |
| Software Heritage | `https://github.com/djm-jpg/arkaya-charter-record`, origin type git, submitted by DM at about 09:44 GMT: "The 'save code now' request has been accepted and will be processed as soon as possible." A request, not preservation: no SWHID yet. Read at F4 | E3 |
| Charter comparison | Section 6 command of the runbook in WORKING at PUBLICATION_COMMIT, 09:36 GMT: 12 of 12 PASS, CREDITED 12/12, "baseline advanced"; output `verification/live/charter_comparison_publish-007_E4.txt`; `verification/live/pvr_snapshot_live.json` updated; tracked `vendor/` files restored | E4 |
| Evidence commit | `Baseline and publication log, publish-007`: this log, the Charter comparison output and snapshot, and the D7 ledger change. This log is inside the commit it describes, so BASELINE_TREE and the patch hash are reported to DM at E5 and entered here at Part F | E5 |
| BASELINE_COMMIT, `evidence-013` | Entered at Part F, from Block G, P and T | E6 |
| Next-day checks | Scheduled for Tuesday 27 October 2026 | E7 |

## 6. What is public

`https://record.arkayarisk.com/disclosures/` serves disclosure record v6 as sequence 4: `conflicted-decisions/v6/conflicted-decisions-v6.md` (SHA-256 `746e4952…9fbe`, 33,133 bytes), registered with the reason fixed by PUB-7 ("Successor issue: discloses decisions taken since v5, including the publication of GET v6 for comment, and nine control failures. v3's, v4's and v5's entries are not repeated and are not superseded; v3, v4 and v5 remain published and unchanged."). v3, v4 and v5 are served byte-identical to their published objects. `/charter/` and `/get/` are unchanged.

## 7. Deviations and findings

1. **B8 read as two registration blocks** (D1, 25 October): the carry block had to change as well as the disclosure block, or GET would have been rebuilt under the same name. Decided before the run, rehearsed, logged. For runbook v5: B8 should name both blocks.
2. **Footer changed at B5.** The runbook lists four publication-state items; the footer status word was also changed, following the v5 precedent at publish-005 (build 10). For runbook v5: add the footer to B5's list.
3. **C3 already satisfied.** Auto publishing was still locked from publish-006; the step was observed, not performed.
4. **Upload from the project overview drop area**, not the Deploys page: same drag, same result; the deploy appeared under Deploys as "Deployed with Netlify Drop". No effect on the run.
5. **Terminal screenshots as evidence** for Blocks G, P and T and the VERIFY and VERIFY2 checks (DM's screen, read by the session), in place of pasted output. Every value was independently re-read by the session on a fresh public clone.
6. **Internet Archive outage during E2.** The first save attempt (09:38 GMT) returned "Temporarily Offline"; the captures were resubmitted from 09:39 and all seven completed by 09:46. No capture skipped.

No act preceded its authority in this run. Every push and tag followed the typed line it depended on.

*AKR AIPS · PUBLICATION_LOG_publish-007 · session k4r9te · 26 October 2026*
