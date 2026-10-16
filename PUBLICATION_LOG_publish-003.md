# Publication log: release publish-003, the conflicted-decisions disclosure record v4

Written at step E5 of `OPS_Disclosures_LiveSequence_Runbook_v4` (build 3, SHA-256 `93e7b3322408124d213b749af02ac3c6ee540fc9e7ddfea826f525eadff3b523`, adopted for this run only under `APPROVE AR-20261015-020-e7xrty`), 15 October 2026. Fields carry the values observed and reported during execution. An unavailable field is recorded as outstanding, not left blank or inferred. "Operator" means DM on his machine; "session" means the Claude session that holds WORKING.

This release carries `/charter/` byte-identical from the published release, carries disclosure v3 byte-identical, and publishes disclosure v4 as sequence 2 of the `/disclosures/` record. The Charter's own log is `PUBLICATION_LOG.md`, which this release does not change.

## 1. Authority and preparation

| Field | Value | Step |
|---|---|---|
| Publication decision | `APPROVE AR-20261015-020-e7xrty`, DM, 17:10 BST; recorded in `10-Layer1-Custodian/Governance/OPS_DecisionRecord_PubRecordV4_Publication_2026-10-15_v1` (SHA-256 `895f4acf8a017964041281821c625d93367f9c3162c5aa255237c0b79a3334db`) | A1 |
| BASE | `21fb140542e5ff6c1c1c04ff0cfe362376a9edb3` | A2 |
| PREVIOUS_DEPLOY, PREVIOUS_RELEASE | `6abad9e1000fbe6e7d4aa921`, `publish-002` | A2 |
| `package.py --check` on a fresh clone | exit 0 | A3 |
| Operator pull and HEAD | already up to date; HEAD equal to BASE | A4 |
| Operator test suite | 162 tests, `OK` | A5 |
| Operator tracked tree | clean | A6 |
| Rehearsal build (`rehearsal-20261015`, build 2 registered) | Charter manifest unchanged; v3 byte-identical to its published digest; sequence 1 to 2; `package.py --check` exit 0; nothing committed, filed or deployed | A7 |
| Interval rule | every entry within five business days of its effective date or marked as a miss; reliance dated on every entry that records it; first run under the rule | A8 |

## 2. The release

| Field | Value | Step |
|---|---|---|
| Stop point 2 | DM, 17:29 BST | B1 |
| PUBLICATION_DATE | 2026-10-15 (UTC) | B2 |
| Identifiers | `publish-003`, `release-003`, `publication-003`, `evidence-007`, `evidence-008`; confirmed by DM 17:31 BST | B3-B4 |
| Carrier | build 3 (publication state), 23,173 bytes, SHA-256 `27e0f46a33025cd16e4375d965d79f1ddd5e12c63d9b0ffe3d4e321f875c39ec`; diff against build 2 confined to the status line, 23 Disclosed cells, the closing sequence, the revision row and the footer status; accepted by DM at 17:34 BST on the diff | B5-B6 |
| Carrier filed | `10-Layer1-Custodian/Governance/`, hash-checked on the device; build 2 (`12c509bd…29cc`) preserved in `_Superseded/` | B7 |
| Registration | v4 entry only; reason: "Successor issue: discloses decisions taken since v3 and the disclosure misses since. v3's entries are not repeated; v3 remains published and unchanged." | B8 |
| Builder | `build_release.py` `2026-09-28.1`, SHA-256 `d973186ccf98bd63a22815cf0eaf8b36915e51caf01e44779bf3555717765f6d` | B9 |
| Registry SHA-256 | `78133311589c784eea11aeb1d6acad87fc786b01b2452671e64f1b69ab5cbdbb` | B9 |
| Built at | 2026-10-15T16:34:48Z | B9 |
| Date-mismatch override | none | B9 |
| Root pointer SHA-256 | `5c2a1b8c55c16183d4a94deff459617f48394346ce69254550d33ba2206dd787`, unchanged from `publish-002` | B9 |
| Charter manifest (carried) | `b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6`, equal to the published manifest | B9 |
| v3 object | `10400912d65cf1bfd584322874d7f178949d209f0157072908be872076926c64`, equal to its published digest | B9 |
| Disclosures manifest (DISC_MANIFEST) | `2375cb08ea89b9abd1f5fcf4508fb7e61e43121526a127dc567edfd5e5680fc9` | B9 |
| Disclosures index SHA-256 | `4e719340dfca982fb34f24b7e98def44388b3455f3093c7f636840fbe8203c15` | B9 |
| FREEZE_TREE | `a977424d777d087ed1a58d570cc363ef13d7e840` | B10 |
| FREEZE_PATCH_SHA | `12669aa3bd105ee5e0ce13bb905846ce0563b80eafda4341bcfaa3e41b1cd94a`, 740,604 bytes; apply-tested on a fresh clone at BASE; filed to DROP and hash-checked on the device | B10 |

## 3. Frozen-release commit, before deployment

| Field | Value | Step |
|---|---|---|
| Patch hash on the operator's machine | equal to FREEZE_PATCH_SHA | B11 |
| Tree after `git am` in REPO | equal to FREEZE_TREE | B11 |
| Push | `21fb140..79e90e3 main -> main`; confirmed on a fresh public clone (tree FREEZE_TREE, parent BASE) | B11 |
| **RELEASE_COMMIT** | `79e90e3b43930e26a92f3799a4777ca623b0a9d6` | B11 |
| `release-003` | annotated, **unsigned**, on `79e90e3…`; absent locally and on the remote before creation | B12 |
| Bound (`--bind`) | 2026-10-15T16:44:40Z, exit 0 | B13 |
| VERIFY `~/arkaya-verify-publish-003` at `release-003` | tag peels to RELEASE_COMMIT; both manifests equal; `package.py --check` exit 0 | B14-B16 |

## 4. Deployment

| Field | Value | Step |
|---|---|---|
| Stop point 4 | DM, about 17:50 BST | C1 |
| Published deploy before upload | `6abad9e1000fbe6e7d4aa921`, read by the session through the Netlify connector | C2 |
| Auto publishing | already locked since `publish-002`; still locked after publication | C3, C8 |
| Upload | `publish-003` dragged from VERIFY onto the project by Netlify Drop; "5 new files uploaded" | C4 |
| **DEPLOY_ID** | `6ad10611834ef8909c7a9c79`, created 2026-10-15T16:57:53Z | C5 |
| DEPLOY_PERMALINK | https://6ad10611834ef8909c7a9c79--arkaya-record.netlify.app/ | C5 |
| Production still PREVIOUS_DEPLOY after upload | yes (connector; `published_at` empty) | C5 |
| Preview verification (operator) | 103/103 checks; approval withheld solely for the non-canonical address | C6 |
| Preview comparison (session) | nine served objects (root pointer, both manifests and sidecars, index JSON and HTML, v3, v4) byte-identical to the release | C7 |
| Production decision | `APPROVE AR-20261015-021-e7xrty`, DM, 18:02 BST | C8 |
| Published to production | "Published & locked deploy" observed 18:03 BST; connector shows `6ad10611…` current | C8 |

## 5. Authoritative live verification and recording

| Field | Value | Step |
|---|---|---|
| Verified address | `https://record.arkayarisk.com/`, from VERIFY on the operator's machine | C10 |
| Result | 103/103 checks passed, exit 0; **PRODUCTION APPROVAL: GRANTED**; no blockers, no findings, no unexercised checks | C10 |
| EVIDENCE | `verification/live/live_verification_20261015T170429.json`, 22,281 bytes, verified at 2026-10-15T17:04:29Z | C11 |
| EVIDENCE_SHA | `6ae87a392c5c60886fc8d5fbd83d5fb39143f36e22494428ffa850b52667e8a7`; equal on the filed copy and WORKING | C13 |
| Evidence fields | canonical base; `rehearsal: false`; `test_input: false`; `passed: true`; `production_approval: true` | C13 |
| Approval accepted; recording authorised | DM, 18:06 BST | C15, D1 |
| Recorded | 2026-10-15T17:06:43Z, exit 0, first attempt | D2 |
| Disclosures first publication | `v4` first published 2026-10-15, disclosures sequence 2, snapshot `ledgers/disclosures/publications/2/`; `v3` unchanged at 2026-09-28 | D3 |
| Charter ledgers, snapshots and `publish/` untouched | yes (`git diff --quiet` exit 0) | D3 |
| `releases/publish-003.json` | `published: true` | D3 |
| Package after recording | `OPS_Record_Release_publish-003_2026-10-15.tar.gz`, 1,716,603 bytes, SHA-256 `ba60d8edaad32469621a80582f79d482b23cf84e4b612d4a1897394cabaf95a5` | D4 |

## 6. Publication-evidence commit

| Field | Value | Step |
|---|---|---|
| PUBLICATION_TREE | `cc1933b69e01b89a99987443cbffdd0584f66fca` | D4 |
| PUBLICATION_PATCH_SHA | `ebe0e8571d5dee1b4882069a8cf862a4a337a23a76999dd0c9e84e6127c93279`, 77,099 bytes; apply-tested on a fresh clone at `79e90e3` | D4 |
| Tree after `git am` in REPO | equal to PUBLICATION_TREE | D5 |
| Push | `79e90e3..2670f8b main -> main`; confirmed on a fresh public clone | D5 |
| **PUBLICATION_COMMIT** | `2670f8be1aa03cace74bdd54a13a86d30984c8ba` | D5 |
| `publication-003` | annotated, **unsigned**, on `2670f8b…` | D6 |
| Evidence tag noted | exit 0, 2026-10-15T17:16:40Z, written to the disclosures index ledger only | D7 |
| VERIFY2 `~/arkaya-verify2-publish-003` at `publication-003` | tag peels to PUBLICATION_COMMIT; `package.py --check` exit 0 | D8-D9 |

## 7. Commits and tags

| Identifier | Value |
|---|---|
| `release-003` | `79e90e3b43930e26a92f3799a4777ca623b0a9d6`, frozen-release commit |
| `publication-003` | `2670f8be1aa03cace74bdd54a13a86d30984c8ba`, publication-evidence commit |
| `evidence-007` | `242c9c517488c3cb07db89b3fb056074b5a06a83`, baseline and publication log; annotated, **unsigned**; tagged 2026-10-15 18:46 BST |
| `evidence-008` | the next-day close-out (Part F); named in the closing note, because a commit cannot name itself |

## 8. Preservation

| Capture | Wayback timestamp (UTC) | Step |
|---|---|---|
| `https://record.arkayarisk.com/` | `20261016084520`, reported by Save Page Now ("A snapshot was captured") on DM's resubmission at about 09:45 BST on 16 October, with the notice that registration is delayed and lookups may redirect to an earlier version for now. Not yet confirmed by a lookup. The 15 October attempts resolved only to `20260928214909`. The root pointer served is byte-identical throughout (`5c2a1b8c…d787`, F2) | E2, F |
| `/disclosures/` | `20261015172652` | E2 |
| `/disclosures/index.json` | `20261015172924` | E2 |
| `/disclosures/index.html` | `20261015173039` | E2 |
| `/disclosures/manifest.json` | `20261015173103` | E2 |
| `/disclosures/manifest.json.sha256` | `20261015173313` | E2 |
| `/disclosures/conflicted-decisions/v4/conflicted-decisions-v4.md` | `20261015173347` | E2 |

Each capture is at `https://web.archive.org/web/<timestamp>/https://record.arkayarisk.com/<path>`.

| Field | Value | Step |
|---|---|---|
| Software Heritage "save code now" | origin `https://github.com/djm-jpg/arkaya-charter-record`, type git; request **accepted**, about 18:23 BST (17:23Z) | E3 |
| SWHID | `swh:1:snp:685bfec03904d09cd8a5c27bb2a6b03a75d533b4`: visit 7, status full, 2026-10-15T20:11:21Z, after DM's resubmission at about 21:11 BST. The snapshot holds `refs/heads/main` = `242c9c5` and tags `release-001` to `release-003`, `publication-001` to `publication-003` and `evidence-002` to `evidence-007`. The 17:23Z visit (snapshot `991ed98c43119ab3cd773ca4edfdee0ee5a29bb9`) predates `evidence-007`. Read by the session from the Software Heritage API on 2026-10-16 | F4 |

## 9. Charter comparison after deployment

| Field | Value | Step |
|---|---|---|
| Command | the runbook appendix command, unchanged, against `https://record.arkayarisk.com/charter/` | E4 |
| Result | exit 0; fixture run credited 12/12; live run **12/12 PASS**, current `v3`, 4 versions, no silent revision, entry digests match, membership retained | E4 |
| Baseline | advanced; `verification/live/pvr_snapshot_live.json` now `9d5078d2cad4d9eae4840277c31487554ef42984bf7fea87514c2f825d1db7b3` | E4 |
| Full output | `verification/live/charter_comparison_publish-003_E4.txt` | E4 |

## 10. Deviations and findings

1. **Part A and the publication day.** Part A ran on the publication day, as AR-20261015-020 chose. The single-date rule (S6) ran from the freeze at B1 (17:29 BST); production approval was reached at 18:02 BST the same UTC date.
2. **Session preparation before the decision.** A2, A3 and A7 ran in the session before AR-20261015-020 was typed. They were read-only or scratch; nothing was committed, filed or deployed.
3. **Stop point 4 text pasted into Terminal.** The reply line was pasted into the operator's shell (`zsh: command not found: 0.`). It ran nothing.
4. **C2 read by the session.** The published deploy was read through the Netlify connector, not by the operator in the dashboard. C3 needed no action: auto publishing had stayed locked since `publish-002`.
5. **D6 first attempt.** The tag push was run before the tag was created (`src refspec publication-003 does not match any`, non-zero exit). Nothing was created. The tag was then created and the push repeated (S1, S4).
6. **D9 exit status.** An unexecuted line was cleared with Ctrl+U before `echo $?`; the status read 0. The check output showed every stage ok.
7. **Root capture late.** The E2 root capture did not register on 15 October: two submissions resolved to the 28 September capture. A third submission at the next-day checks reported capture `20261016084520`, with registration delayed; it is recorded as reported, not yet confirmed by a lookup. The root pointer's bytes did not change between the two captures (Section 8).
8. **Local test by-products excluded.** `package.py`'s test stages write `verification/live/live_verification_*.json` files against a local test server; none is committed (S10). The E4 run also left four untracked acceptance-suite cache files (`vendor/acceptance_suite/__pycache__/*.cpython-313.pyc`) in WORKING; `package.py` refused them as unrecorded, and they were removed before packaging.
9. **v3 labelled "superseded" in the public index.** The builder marks every earlier version superseded. v4 does not supersede v3's entries; the registration reason states it. A pipeline change for successor-type records is a finding for a later work order, not made in this run.
10. **The record's build-2 change list is incomplete** (four changes not listed). Disposed as not blocking under R3 by `APPROVE AR-20261015-019-e7xrty`, override limited to change-log completeness; carried to the next disclosure record.
11. **This log is not in the package.** `package.py` packages `PUBLICATION_LOG.md` by name, not this file. Its integrity rests on this commit and on the `.sha256` sidecar filed at F7.

## 11. Next-day checks (Part F)

| Field | Value | Step |
|---|---|---|
| Scheduled | a reminder into the session for 2026-10-16T09:00Z; disabled unfired when DM started Part F at 09:32 BST | E7 |
| Authoritative live verification | VERIFY `~/arkaya-verify-publish-003` on the operator's machine against `https://record.arkayarisk.com/`, 2026-10-16T08:40:41Z: **103/103 checks passed, PRODUCTION APPROVAL: GRANTED**, exit 0 | F1 |
| Evidence | `verification/live/live_verification_20261016T084041.json`, 22,281 bytes, SHA-256 `023ae626dec88af687692cdc51fbfc05ed369286d5c1f7088aeef2617f75fb60`; copied to DROP by the operator (exit 0), hashed on the device, equal in WORKING | F1-F2 |
| Evidence fields | canonical base; `rehearsal: false`; `test_input: false`; `passed: true`; `production_approval: true`; no approval blockers, no findings, no unexercised checks; Charter manifest published, local and served all `b926170e…2ac6`; root pointer served `5c2a1b8c…d787`, unchanged | F2 |
| Charter comparison, re-run unchanged | 2026-10-16 about 08:43Z, after F1: exit 0, live **12/12 PASS**, current `v3`, 4 versions; baseline advanced, `pvr_snapshot_live.json` now `09c444a25555c3c52598405ff2abb6b2263a7adbe3ff25d66a2a7f29242db91f`. Full output `verification/live/charter_comparison_publish-003_F3.txt` (5,371 bytes, SHA-256 `6248a81aacf1dc90bac01a66d9fa254a5046a5f15baaac7a3488a33c7248d8fb`) | F3 |
| SWHID | see Section 8 | F4 |
| Root capture | see Section 8 and deviation 7 | E2, F |

**Result.** The published state held overnight unchanged: both namespaces served their frozen bytes, the Charter passed its acceptance suite, and no finding arose.
