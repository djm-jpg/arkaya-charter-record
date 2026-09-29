# Publication log: release publish-002, the conflicted-decisions disclosure record

Written at step 155 of `OPS_Disclosures_LiveSequence_Runbook_v3`, 28 September 2026. Fields carry
the values observed and reported during execution. An unavailable field is recorded as
outstanding, not left blank or inferred. "Operator" means DM, or an agent acting at his instruction
on his machine; "session" means the Claude session that holds WORKING.

This release carries `/charter/` byte-identical from `release-001` and publishes a second record
namespace, `/disclosures/`, for the first time. The Charter's own log is `PUBLICATION_LOG.md`, which
this release does not change.

## 1. The release

| Field | Value | Step |
|---|---|---|
| Release name and date | `publish-002`, 2026-09-28 (UTC) | 29-32 |
| Pipeline commit | `7edabde1800012dd67c0991cf94c7c6a566e77a5` | 22 |
| Disclosure input | `conflicted-decisions-v3.md`, build 5, 28,593 bytes, SHA-256 `10400912d65cf1bfd584322874d7f178949d209f0157072908be872076926c64`; accepted by DM at 21:57 BST on the diff summary and mechanical checks | 33-38 |
| Builder | `build_release.py` `2026-09-28.1`, SHA-256 `d973186ccf98bd63a22815cf0eaf8b36915e51caf01e44779bf3555717765f6d` | 45 |
| Registry SHA-256 | `99c3038c959310a0a5381eceaab447b8f5aeff85727dabfa927844016f4f1a4a` | 45 |
| Built at | 2026-09-28T20:57:45Z | 45 |
| Date-mismatch override | none | 45 |
| Root pointer SHA-256 | `5c2a1b8c55c16183d4a94deff459617f48394346ce69254550d33ba2206dd787` | 45 |
| Charter manifest (carried) | `b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6`, equal to the published manifest; tree identical to `publish/charter` | 46 |
| Disclosures manifest (DISC_MANIFEST) | `a9775768cd21190023144af907bbb4b81cff72b74ecac0cc7238a3a93dc2af30` | 47 |
| Disclosures index SHA-256 | `6a2ff399d0351393bd438a2cec49d3311b87149293c02e013e4b1b14a7b7728a` | 47 |
| FREEZE_TREE | `e482a57ca7b16efda9cbc032544e9d51e7a559cc` | 52 |
| FREEZE_PATCH_SHA | `dacdde1546b39590baee742def627af899e9e50fe2da8ec30190ac0234d28725`, 720,020 bytes; apply-tested on a fresh clone at `7edabde` | 53 |

## 2. Frozen-release commit, before deployment

| Field | Value | Step |
|---|---|---|
| Patch hash checked on the operator's machine | equal to FREEZE_PATCH_SHA | 56-57 |
| Tree after `git am` in REPO | `e482a57c…`, equal to FREEZE_TREE | 59-61 |
| Push | `7edabde..ce30c9d main -> main` | 62 |
| **RELEASE_COMMIT** | `ce30c9dc4cc2896ee4f2e56fe465de7685993425` | 64 |
| `release-002` | annotated, **unsigned**, on `ce30c9d…` | 65-67 |
| Bound (`--bind`) | 2026-09-28T21:07:52Z, exit 0 | 68-69 |
| Fresh clone at `release-002` (VERIFY) | tag peels to RELEASE_COMMIT; both manifests equal; `package.py --check` exit 0, all four test stages ok | 70-79 |

## 3. Deployment

| Field | Value | Step |
|---|---|---|
| Netlify project | `arkaya-record` | 81 |
| PREVIOUS_DEPLOY | `6aaac22b28ce9dc7b8ecf61d`, as expected | 82-83 |
| Auto publishing | locked before upload, and still locked after publication | 84, 94 |
| **DEPLOY_ID** | `6abad9e1000fbe6e7d4aa921` | 86 |
| DEPLOY_PERMALINK | https://6abad9e1000fbe6e7d4aa921--arkaya-record.netlify.app/ | 86 |
| Production still PREVIOUS_DEPLOY after upload | yes | 87-88 |
| Preview verification | 100/100 checks, exit 0; approval withheld solely for the non-canonical address | 89-91 |
| Production decision | D-PROD-PUBLISH-002, typed APPROVE by DM at 22:24 BST | 92 |
| Published to production | clicked 22:25:10 BST; "Published & locked" observed 22:25:16 BST (21:25:16Z) | 93-94 |

## 4. Authoritative live verification and recording

| Field | Value | Step |
|---|---|---|
| Verified address | `https://record.arkayarisk.com/`, from VERIFY on the operator's machine | 96 |
| Result | 100/100 checks passed, exit 0; Charter identity 4/4; **PRODUCTION APPROVAL: GRANTED** | 96-98 |
| EVIDENCE | `verification/live/live_verification_20260928T212645.json`, 21,316 bytes | 97 |
| EVIDENCE_SHA | `303168a126c940c744407a5d60ceb4a5fb2ac7c4b3871aaea4ec86b60f661975`; equal on the operator's copy, the filed copy and WORKING | 97-102 |
| Approval accepted | DM, 22:29 BST | 99 |
| Recording authorised | DM, 22:32 BST | 103 |
| Recorded | 2026-09-28T21:32:41Z, exit 0, first attempt | 104-105 |
| Disclosures first publication | `v3` first published 2026-09-28, disclosures sequence 1, snapshot `ledgers/disclosures/publications/1/` | 108 |
| Charter ledgers, snapshot and release untouched | yes (`git diff --quiet` exit 0) | 109 |
| `releases/publish-002.json` | `published: true` | 110 |
| Package after recording | `OPS_Record_Release_publish-002_2026-09-28.tar.gz`, 1,693,755 bytes, SHA-256 `757f6ca967de772ded28f67470d3a7ca139f8d6efac658a5408e973c8eca5a3e` | 112-113 |

## 5. Publication-evidence commit

| Field | Value | Step |
|---|---|---|
| PUBLICATION_TREE | `ae6a962250d431111921b477ce27ca0493edbe1c` | 115 |
| PUBLICATION_PATCH_SHA | `6588ba90ab38bf078c1135a4b07080fcdf536d59de4a89c7429b4bf13a3a571b`, 73,722 bytes; apply-tested on a fresh clone at `ce30c9d` | 116-117 |
| Tree after `git am` in REPO | equal to PUBLICATION_TREE | 122-124 |
| Push | `ce30c9d..7822db7 main -> main` | 125 |
| **PUBLICATION_COMMIT** | `7822db77cf8cb6d49c70c432373c6c84e680f711` | 127 |
| `publication-002` | annotated, **unsigned**, on `7822db7…` | 128-130 |
| Evidence tag noted | exit 0, 2026-09-28T21:44:15Z, written to the disclosures index ledger only | 131-132 |
| Fresh clone at `publication-002` (VERIFY2) | `package.py --check` exit 0, all four test stages ok; tag peels to PUBLICATION_COMMIT | 133-138 |

## 6. Commits and tags

| Identifier | Value |
|---|---|
| `release-002` | `ce30c9dc4cc2896ee4f2e56fe465de7685993425`, frozen-release commit |
| `publication-002` | `7822db77cf8cb6d49c70c432373c6c84e680f711`, publication-evidence commit |
| `evidence-005` | `fb38e40a082608b80ee528c6842c73c4bcb75736`, baseline and publication log; annotated, **unsigned**; pushed 2026-09-28 about 23:13 BST |
| `evidence-006` | the next-day close-out (steps 181-195); named in the closing note, because a commit cannot name itself |

A commit cannot name its own identifier. `evidence-005` was added at the close-out (step 180), and
`evidence-006` is recorded in the closing note filed at step 199, outside the repository.

## 7. Preservation

| Capture | Wayback timestamp (UTC) | Step |
|---|---|---|
| `https://record.arkayarisk.com/` | `20260928214909` | 141 |
| `/disclosures/` | `20260928215046` | 142 |
| `/disclosures/index.json` | `20260928215122` | 143 |
| `/disclosures/index.html` | `20260928215209` | 144 |
| `/disclosures/manifest.json` | `20260928215313` | 145 |
| `/disclosures/manifest.json.sha256` | `20260928215417` | 146 |
| `/disclosures/conflicted-decisions/v3/conflicted-decisions-v3.md` | `20260928215504` | 147 |

Each capture is at `https://web.archive.org/web/<timestamp>/https://record.arkayarisk.com/<path>`.
All seven completed on the first submission.

| Field | Value | Step |
|---|---|---|
| Software Heritage "save code now" | origin `https://github.com/djm-jpg/arkaya-charter-record`, type git; request **accepted**, about 23:00 BST (22:00Z) | 149-151 |
| SWHID | `swh:1:snp:48af66b76f7010dfaffecfd9f6e7eabdb0704f86`: save task succeeded, visit full at 2026-09-28T22:00:52Z. The snapshot holds `refs/heads/main` = `7822db7` and tags `release-002` and `publication-002`. `evidence-005` was pushed after the visit and is not in it. Read by the session from the Software Heritage API | 179 |

## 8. Charter comparison after deployment

| Field | Value | Step |
|---|---|---|
| Command | the runbook appendix command, unchanged, against `https://record.arkayarisk.com/charter/` | 152 |
| Result | exit 0; fixture run credited; live run **12/12 PASS**, current `v3`, 4 versions, no silent revision, entry digests match, membership retained | 153-154 |
| Baseline | advanced; `verification/live/pvr_snapshot_live.json` now `561499057bf17b8b01c2a7c74484bcdfae02a7fdcb6ddf6473f24103e656b79c` | 153 |
| Full output | `verification/live/charter_comparison_publish-002_step152.txt` | 153 |

## 9. Deviations and findings

1. **VERIFY location.** The runbook names VERIFY as a fresh clone the operator makes. Steps 70-79, the preview (85, 89) and the authoritative check (96) ran in
   `/Users/davidmckibbin/Documents/Codex/2026-09-28/referenced-chatgpt-conversation-this-is-an-2/work/VERIFY-release-002`, a fresh clone made by an agent on the operator's machine. `~/arkaya-verify-002` was created but never verified. Content-neutral: the session checked the served preview and live bytes independently against its own fresh clone.
2. **Step 128 first attempt** ran in VERIFY, not REPO: `fatal: bad object type`, no tag created. Cause fixed and the step repeated (S4).
3. **Steps 2-4 of the stop point 8 instructions** added a `git pull` and a HEAD check before `git am`. They are not in the runbook; they changed nothing.
4. **Local test by-products excluded.** `package.py`'s test stages write `verification/live/live_verification_*.json` files against a local test server (127.0.0.1). They were left out of the publication-evidence commit and this one, because they are not evidence of this publication. `publication-001` included such files; this is a departure from that precedent.
5. **HSTS at the canonical address** is `max-age=31536000`, without the `includeSubDomains; preload` seen at the preview address. The check requires presence only and passed. This comes from the custom-domain configuration; no action taken in this run.
6. **This log is not in the package.** `package.py` packages `PUBLICATION_LOG.md` by name, not this file. The log's integrity rests on this commit and on the `.sha256` sidecar filed at step 198.

## 10. Next-day checks (steps 173-180)

| Field | Value | Step |
|---|---|---|
| Scheduled | a reminder into the session, fired 2026-09-29T08:00Z | 173 |
| Authoritative live verification | VERIFY on the operator's machine against `https://record.arkayarisk.com/`, 2026-09-29T09:11:32Z: **100/100 checks passed, PRODUCTION APPROVAL: GRANTED**, exit 0; root pointer served unchanged | 174-176 |
| Evidence | `verification/live/live_verification_20260929T091132.json`, 21,316 bytes, SHA-256 `4010206bc966203a4a1acdc583f2864fae93e9e15beaefc543139679978e4c63`; equal on the filed copy and WORKING | 175 |
| Charter comparison, re-run unchanged | 2026-09-29 about 09:13Z, after step 174: exit 0, live **12/12 PASS**; baseline advanced, `pvr_snapshot_live.json` now `8e8176b7d7b67d8c39006a67b6e57d4094e87b16f49405419188521683286ca6`. Full output `verification/live/charter_comparison_publish-002_step177.txt` | 177-178 |
| Earlier session run of the comparison | 2026-09-29 about 08:02Z, before step 174, also exit 0 and 12/12; superseded by the in-order run above, which is the one recorded | 177 |
| SWHID | see Section 7 | 179 |

**Result.** The published state held for a day unchanged: both namespaces served their frozen
bytes, the Charter passed its acceptance suite, and no finding arose.
