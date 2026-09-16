# Publication log — Arkaya Schema Independence Charter, public version record

**Blank template. Nothing below has been done.** Each field is completed at the step named,
and an unavailable field is recorded as outstanding rather than left blank or inferred.

Step letters follow `DEPLOY.md` v6, in which the frozen-release commit is created **before**
deployment and the publication-evidence commit **after** it. The two tags identify different
commits and the log records both.

## 1. The release

| Field | Value | Step |
|---|---|---|
| Release date (the date the set carries) | | A1 |
| Publication sequence | | A1 |
| Manifest SHA-256 | | A4 |
| Package SHA-256 | | A4 |
| Builder version and SHA-256 | | A3 |
| Verification run directory | | A2 |
| Date-mismatch override used, and its recorded reason | none | A1 |
| Package | `OPS_Charter_PublicationSet_2026-09-16_v6` | — |

## 2. Frozen-release commit, before deployment

| Field | Value | Step |
|---|---|---|
| Repository URL | | B1 |
| Layout mirrors the package unchanged | | B2 |
| **Frozen-release commit SHA** | | B3 |
| Branch protection mechanism used | | B4 |
| "Allow force pushes" disabled | | B4 |
| "Allow deletions" disabled | | B4 |
| Administrator coverage enforced | | B4 |
| Tag protection mechanism used | | B5 |
| Tag patterns protected | `release-*`, `publication-*` | B5 |
| Tag `release-001` created on the frozen-release commit | | B6 |
| `release-001` signed | | B6 |
| **Release bound to that commit and tag** (`--bind`) | | B7 |
| Bound manifest digest (must equal §1) | | B7 |
| Fresh clone at `release-001` passes `package.py --check` | | B8 |
| Rulesets confirmed active by observation | | B9 |

**The binding's limit.** `--bind` records an identifier supplied by the operator. It does not
verify that the commit exists in any repository. B8, a fresh clone at the tag reconciling, is
what tests the other half.

## 3. Deployment

| Field | Value | Step |
|---|---|---|
| Netlify project | `arkaya-record` | C3 |
| Deploy ID | | C5 |
| Deploy permalink | | C5 |
| Canonical address | `https://record.arkayarisk.com/charter/` | C6 |
| DNS CNAME target | | C8 |
| Certificate issued | | C9 |

## 4. Live verification, before recording or archival

| Field | Value | Step |
|---|---|---|
| `verify_live.py` exit status | | D1 |
| Checks passed / total | | D1 |
| Served manifest matched the frozen manifest | | D1 |
| Served sidecar matched the served manifest | | D1 |
| Landing page body matched index.html | | D1 |
| HTTP redirected to the same HTTPS address | | D1 |
| **PRODUCTION APPROVAL granted** | | D2 |
| Evidence file | | D4 |

## 5. Publication recorded

| Field | Value | Step |
|---|---|---|
| `record_publication.py` exit status | | E1 |
| Interrupted and resumed | no | E2 |
| Immutable snapshot | `publications/<sequence>/` | E2 |
| First-publication dates written for | | E2 |
| Package re-run after recording | | E3 |

## 6. Publication-evidence commit, after deployment

| Field | Value | Step |
|---|---|---|
| **Publication-evidence commit SHA** | | F2 |
| Tag `publication-001` created on that commit | | F3 |
| `publication-001` signed | | F4 |

**`release-001` identifies the frozen release: the bytes that were deployed.**

**`publication-001` is not the published object.** It is the evidence record *that*
publication occurred, and it necessarily post-dates the deployment it records. They are
different commits and neither tag describes the other's content.

## 7. Preservation

### Internet Archive

| Object | Archived URL | Capture timestamp |
|---|---|---|
| `charter/` | | |
| `index.json` | | |
| `index.html` | | |
| `manifest.json` | | |
| `manifest.json.sha256` | | |
| `README.md` | | |
| `v1/charter-v1.pdf` | | |
| `v1.1/charter-v1.1.pdf` | | |
| `v2/charter-v2.pdf` | | |
| `v3/charter-v3.pdf` | | |

### Software Heritage

| Field | Value | Step |
|---|---|---|
| Request submitted (date) | | G4 |
| Request status | | G5 |
| Completed SWHID (snapshot or revision) | | G6 |
| If outstanding: date to check again | | G7 |

**A request status of "accepted" or "pending" is not preservation.** Until a SWHID exists, the
repository is not archived and must not be described as archived.

## 8. Baseline and follow-up

| Field | Value | Step |
|---|---|---|
| Live baseline established (date, run 1) | | H1 |
| Next-day comparison scheduled for | | H4 |
| Next-day comparison run (date, run 2) | | H4 |
| Run 2 result | | H4 |

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
