# Publication log — Arkaya Schema Independence Charter, public version record

Completed 16 September 2026 at step 152 of the live sequence. Fields carry the values observed
and reported during execution. An unavailable field is recorded as outstanding rather than left
blank or inferred.

Step letters follow `DEPLOY.md` v6, in which the frozen-release commit is created **before**
deployment and the publication-evidence commit **after** it. The two tags identify different
commits and the log records both.

## 1. The release

| Field | Value | Step |
|---|---|---|
| Release date (the date the set carries) | 2026-09-16 | A1 |
| Publication sequence | 1 | A1 |
| Manifest SHA-256 | `b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6` | A4 |
| Package SHA-256 | `0dcde8e8a48f0e2712630ccede98a654e2f4158a99a62b96438637abd745d22d` (published package, 1,130,317 bytes) | A4 |
| Package SHA-256, pre-publication | `7e85a5a57bc4e0f14d8368e3566b8ddbbc4d150a09f3ca748eefa50805724fb1` (the package deployed from; superseded by the above after recording) | A4 |
| Builder version and SHA-256 | `2026-09-16.4`, `311f9f110cd376d37f2d56ddde03930d7d339ae7ab7439a506f947dbeca72346` | A3 |
| Verification run directory | `verification/runs/20260916T153701` (10 runs re-derived from transcripts; rebuild recomputed, 9 objects and 4 PDFs, no unexpected change) | A2 |
| Date-mismatch override used, and its recorded reason | none | A1 |
| Package | `OPS_Charter_PublicationSet_2026-09-16_v6` | — |

## 2. Frozen-release commit, before deployment

| Field | Value | Step |
|---|---|---|
| Repository URL | https://github.com/djm-jpg/arkaya-charter-record (public) | B1 |
| Layout mirrors the package unchanged | yes — contents copied from an extraction whose archive digest matched, and reconciled at B8 | B2 |
| **Frozen-release commit SHA** | `89f6e53c65ae8405ed050ab92a9625206a6a819b` | B3 |
| Branch protection mechanism used | GitHub ruleset `main-protection`, Active, target Default resolving to `main` | B4 |
| "Allow force pushes" disabled | yes — "Block force pushes" enabled | B4 |
| "Allow deletions" disabled | yes — "Restrict deletions" enabled | B4 |
| Administrator coverage enforced | bypass list empty, so the rules bind ordinary administrator pushes. **It does not prevent an administrator editing the ruleset itself.** | B4 |
| Tag protection mechanism used | GitHub ruleset `publication-tags`, Active | B5 |
| Tag patterns protected | `release-*`, `publication-*`, `evidence-*` | B5 |
| Tag `release-001` created on the frozen-release commit | yes, on `89f6e53c…` | B6 |
| `release-001` signed | **no** — annotated, unsigned (`git cat-file tag` returned 0 signature blocks) | B6 |
| **Release bound to that commit and tag** (`--bind`) | yes, 2026-09-16T16:11:39Z, exit 0 | B7 |
| Bound manifest digest (must equal §1) | `b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6` — equal | B7 |
| Fresh clone at `release-001` passes `package.py --check` | yes, exit 0, on the operator's machine as a non-root user. **This ran the pre-correction test harness; see §10.** | B8 |
| Rulesets confirmed active by observation | `main-protection` confirmed from the settings page. `publication-tags` rules are **operator-confirmed, not screenshot-captured**. "Applies to 0 targets" was correct at the time, as no matching tags existed yet. | B9 |

**The binding's limit.** `--bind` records an identifier supplied by the operator. It does not
verify that the commit exists in any repository. B8, a fresh clone at the tag reconciling, is
what tests the other half. At B8 the clone's resolved commit equalled the recorded commit and
the clone's `publish/charter/manifest.json` equalled the frozen manifest.

## 3. Deployment

| Field | Value | Step |
|---|---|---|
| Netlify project | `arkaya-record` (Site ID `9f499435-fd4f-4b74-851f-d7659e91ca73`) | C3 |
| Deploy ID | `6aaac22b28ce9dc7b8ecf61d` | C5 |
| Deploy permalink | https://6aaac22b28ce9dc7b8ecf61d--arkaya-record.netlify.app/ | C5 |
| Canonical address | `https://record.arkayarisk.com/charter/` | C6 |
| DNS CNAME target | host `record` → `arkaya-record.netlify.app`, TTL 1800. Registrar/DNS: Squarespace Domains; zone served by `ns-cloud-e1`–`e4.googledomains.com` | C8 |
| Certificate issued | yes — Let's Encrypt via Netlify. Confirmed from an unmediated host at 2026-09-16T17:47:31Z: `HTTP/2 200`, `server: Netlify` | C9 |

Deployment source: the `publish` folder of a fresh clone (VERIFY) at `release-001`, not a
local working copy. Upload comprised the nine manifest objects under `charter/` plus the
796-byte root pointer page.

## 4. Live verification, before recording or archival

| Field | Value | Step |
|---|---|---|
| `verify_live.py` exit status | **0** | D1 |
| Checks passed / total | **49 / 49** | D1 |
| Served manifest matched the frozen manifest | yes | D1 |
| Served sidecar matched the served manifest | yes | D1 |
| Landing page body matched index.html | yes | D1 |
| HTTP redirected to the same HTTPS address | yes — `HTTP/1.1 301`, `Location: https://record.arkayarisk.com/charter/`, `server: Netlify`, `x-nf-request-id: 01M2NHVJ94CCE22P29MBBV7XSR` | D1 |
| **PRODUCTION APPROVAL granted** | **yes**, 2026-09-16T16:49:17Z | D2 |
| Evidence file | `verification/live/live_verification_20260916T164917.json`, SHA-256 `2cbb073b1e691bc53638037c7ac5b2f4e55e359b3a287f8ed3586cf1ffeca049`; snapshot copy hashes identically | D4 |

**Where the authoritative verification was run, and why it matters.** It was run on the
operator's own machine, not in the assistant's container. The container's outbound network
passes through a proxy that refuses port 80 and terminates TLS with a gateway-issued
certificate, so it cannot observe either the real redirect or the real chain. Its own run
(16:46:51Z) returned 48/49 with approval **withheld**, the single failure being the redirect
check reporting 403 on plain HTTP. That evidence is retained and superseded. A further
pre-DNS run against the `netlify.app` host (16:22:54Z) also returned 48/49 with approval
withheld, for the same reason. Neither was used: the recorder refuses evidence whose approval
was withheld. No change was made to `verify_live.py` or its expectations to accommodate the
container.

## 5. Publication recorded

| Field | Value | Step |
|---|---|---|
| `record_publication.py` exit status | **0**, recorded 2026-09-16T16:51:28Z | E1 |
| Interrupted and resumed | no | E2 |
| Immutable snapshot | `publications/1/` — six files: `index.json`, `live_verification.json`, `manifest.json`, `manifest.json.sha256`, `publication.json`, `release.json` | E2 |
| First-publication dates written for | v1, v1.1, v2, v3 — all first published 2026-09-16, sequence 1 | E2 |
| Package re-run after recording | yes, exit 0, all stages, 58 gate tests. **It first refused; see §10.** | E3 |

Release marker after recording: `published: true`, state "published; recorded from live
evidence", `release_commit` `89f6e53c…`, `release_tag` `release-001`.

## 6. Publication-evidence commit, after deployment

| Field | Value | Step |
|---|---|---|
| **Publication-evidence commit SHA** | `144530d0f8a4d902097fbc61995f65a6223ce905` | F2 |
| Tag `publication-001` created on that commit | yes | F3 |
| `publication-001` signed | **no** — annotated, unsigned (0 signature blocks) | F4 |

Verified from the object store at the tag, from a fresh public clone (VERIFY2), before the
tag was relied on: resolved commit `144530d0…`; working tree clean; `test_package.py` blob
and the file on disk both `e3ba8722b4df3643311a6e5826ef08f6ff217811a757cb7e368645ad85651ba3`;
`publish/charter/manifest.json` blob equal to the frozen manifest; `package.py --check` exit 0;
`test_package.py` 58 tests, OK.

**`release-001` identifies the frozen release: the bytes that were deployed.**

**`publication-001` is not the published object.** It is the evidence record *that*
publication occurred, and it necessarily post-dates the deployment it records. They are
different commits and neither tag describes the other's content.

## 7. Preservation

### Internet Archive

| Object | Archived URL | Capture timestamp (UTC) |
|---|---|---|
| `charter/` | https://web.archive.org/web/20260916173729/https://record.arkayarisk.com/charter/ | 2026-09-16 17:37:29 |
| `index.json` | https://web.archive.org/web/20260916173739/https://record.arkayarisk.com/charter/index.json | 17:37:39 |
| `index.html` | https://web.archive.org/web/20260916173854/https://record.arkayarisk.com/charter/index.html | 17:38:54 |
| `manifest.json` | https://web.archive.org/web/20260916173805/https://record.arkayarisk.com/charter/manifest.json | 17:38:05 |
| `manifest.json.sha256` | https://web.archive.org/web/20260916173819/https://record.arkayarisk.com/charter/manifest.json.sha256 | 17:38:19 |
| `README.md` | https://web.archive.org/web/20260916173832/https://record.arkayarisk.com/charter/README.md | 17:38:32 |
| `v1/charter-v1.pdf` | https://web.archive.org/web/20260916174401/https://record.arkayarisk.com/charter/v1/charter-v1.pdf | 17:44:01 |
| `v1.1/charter-v1.1.pdf` | https://web.archive.org/web/20260916174632/https://record.arkayarisk.com/charter/v1.1/charter-v1.1.pdf | 17:46:32 |
| `v2/charter-v2.pdf` | https://web.archive.org/web/20260916174805/https://record.arkayarisk.com/charter/v2/charter-v2.pdf | 17:48:05 |
| `v3/charter-v3.pdf` | https://web.archive.org/web/20260916173909/https://record.arkayarisk.com/charter/v3/charter-v3.pdf | 17:39:09 |

All ten captured. The v3 capture was verified by opening it: nine pages, "1 capture, 16 Sep 2026".

### Software Heritage

| Field | Value | Step |
|---|---|---|
| Request submitted (date) | 2026-09-16, origin type `git`, origin https://github.com/djm-jpg/arkaya-charter-record | G4 |
| Request status | **accepted** — "will be processed as soon as possible" | G5 |
| Completed SWHID (snapshot or revision) | **outstanding** | G6 |
| If outstanding: date to check again | 2026-09-17, with the next-day comparison | G7 |

**A request status of "accepted" or "pending" is not preservation.** Until a SWHID exists, the
repository is not archived and must not be described as archived.

## 8. Baseline and follow-up

| Field | Value | Step |
|---|---|---|
| Live baseline established (date, run 1) | 2026-09-16, exit 1 as required; failing checks exactly 8 (no silent revision) and 12 (membership retained), both being properties of a first observation; line read "baseline established" | H1 |
| Baseline snapshot | `verification/live/pvr_snapshot_live.json`, SHA-256 `9c8c6a9d853ef330f6f5d3be8f1724d49f418c6191b8edd5c79ac5f242abbd83` | H1 |
| Next-day comparison scheduled for | 2026-09-17 | H4 |
| Next-day comparison run (date, run 2) | **outstanding** | H4 |
| Run 2 result | **outstanding** | H4 |

Run 1 passed the other ten checks against the live record: resolves, current version v3, four
prior versions, amendment reasons, version semantics, supersession, unauthenticated access,
date consistency, entries retrievable, entry digests match.

**Bound.** Run 1 establishes the baseline and accepts the record as it stands; it is not
evidence of preservation. Only run 2 onward can detect a silent change. The follow-up is
scheduled, not awaited: nothing in sections A to G depends on it.

## 9. What this publication establishes

Completed at H5, and not before.

**Established.**

- The set was served at the canonical address on the recorded date.
- What was served matched the frozen manifest object by object, including the manifest itself
  and the body returned at the landing page.
- A baseline exists from which later change can be detected.

**Not established, and not to be implied.**

- That the v1.1, v2 and v3 amendments were validly effective from their stated July dates.
- That any version was published at any address before the recorded date.
- That constituting authority for the amendments has been established. As at
  14 September 2026 the position was **constituting authority not established**, and that
  position carries its date for a reason.

## 10. Stated deviations and findings

Added to the template because the execution produced findings the template did not anticipate.
Recording them here rather than in a separate document keeps the log the single account.

**1. Steps 69–70 reordered.** Netlify has replaced "Deploy manually" with an upload drop area
and names the project after the first deploy. The project was renamed to `arkaya-record`
before the permalink was captured, so the recorded permalink resolves.

**2. Unscheduled pre-canonical smoke test.** `verify_live.py` was run against the
`netlify.app` host before DNS existed, to detect a bad deploy early. Read-only; evidence
retained; approval withheld; not used.

**3. Authoritative live verification moved to the operator's machine.** See §4.

**4. Blocking defect found at step 97: the gate could not pass after a publication was
recorded.** `package.py` exited 2 with 31 of 55 gate tests failing. Cause: the `Sandbox`
fixture in `test_package.py` copied `releases`, `publications` and `verification` verbatim from
the working tree, so after recording, every sandbox inherited `published: true`, the release
binding, the `publications/1` snapshot and the regenerated published production record. The
tests failed on fixture state rather than on the behaviour under test. Reproduced on a pristine
extraction by injecting only the post-publication state: the release marker alone gave 31
failures, the snapshot alone 15, both 31, the untouched tree passed 55 of 55.

Fixed by making the fixture reset every sandbox to an explicit unpublished, unbound baseline,
with the derived production record regenerated from a reset tree and cached, and an assertion
that fails loudly if a future marker field is unclassified. A regression test was added which
records a publication in a sandbox and then runs the complete gate there with the test stage
enabled. Result: 58 tests, OK, from both a published and a never-published tree; 0 skipped;
and with the reset removed, the three fixture guards fail, so the test is not vacuous. The
complete gate then passed with `PVR_SKIP_TESTS` unset. `PVR_SKIP_TESTS` was not used to obtain
a package.

The change was confined to `test_package.py`, which is not named in the manifest and is not
covered by `check_source_identities`. The manifest-covered bytes hash identically before and
after; that is the supported claim, and it is narrower than saying the published bytes could
not have been affected.

**5. Runbook amended during execution.** Steps 112a–112e were added to verify the
publication-evidence commit's own tree from the object store *before* any tag exists, because
the `publication-tags` ruleset blocks tag deletion with an empty bypass list: a tag on the
wrong tree could not be moved or removed and would have to be superseded by `publication-002`.
Steps 127a–127m were added to verify at VERIFY2 that the harness executed is the harness in the
tagged commit, and to record that `release-001` predates the correction, so the B8 result is
not evidence about the corrected harness.

**6. A commit prepared outside the audited path was not used.** A commit
`894bdfbfc082c60747a9d403608078b47149d0e0` was prepared in a working copy neither party could
inspect, and `git cat-file -t` did not recognise it in the audited repository. It was
discarded. The apparent filesystem restriction that had prompted it was a stale
`.git/index.lock` left by the assistant's own `git status` calls through a bridge shell that
cannot delete files; once removed, staging succeeded normally.

**7. Evidence directory contents.** `verification/live/` holds 147 files. Three are
observations of a real venue (the two withheld runs and the authoritative one). The remaining
144 are rehearsals against `http://127.0.0.1:<port>/charter/` written by the verifier test
suite. They are test artefacts, not observations of the published venue. They were not pruned:
about 114 were already committed at `release-001`, so removing only the newer ones would make
the directory inconsistent across the two tags. Integrity rests on the manifest and on the
production record naming the evidence file, not on the tidiness of the directory. Confirmed
that the gate does not depend on them: with all 144 removed, the complete gate passes.

**8. Both tags are unsigned.** `release-001` and `publication-001` are annotated tags carrying
authorship metadata, not cryptographic signatures. Anyone relying on them should treat the tag
as an index into the repository, not as an attestation of authorship.

**9. An assistant reporting error, corrected.** An empty `archived_snapshots` response from the
Internet Archive availability API was treated as proof that a capture had not occurred, and
`v3/charter-v3.pdf` was reported as not archived. It had been captured at 17:39:09. The API
returned false negatives for all four PDFs. Absence of a record in that index is not evidence
of absence of a capture.
