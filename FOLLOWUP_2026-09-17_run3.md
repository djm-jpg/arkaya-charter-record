# Follow-up record — run 3, next-day comparison

17 September 2026. A separate follow-up to the controlled publication sequence for the Schema
Independence Charter's public version record, sequence 1.

**The sequence is closed.** It closed on 16 September 2026 at `evidence-003`, commit
`74a4693b20d8f0ac4ce07d6159842eb83e1c5b69`. This record does not reopen it. It does not alter
the filed publication log, the closing note, or any existing tag. It carries its own tag,
`evidence-004`.

## 1. The observation

| Field | Value |
|---|---|
| Command | the baseline command in the runbook appendix, unchanged |
| Exit status | **0** |
| Checks | **12 of 12 passed** |
| Baseline established | `2026-09-16T17:57:40.894345+00:00` |
| Run 2 (mechanism test) | `2026-09-16T18:16:32.021629+00:00` |
| Run 3 (this observation) | `2026-09-17T08:31:32.275336+00:00` |
| Interval, baseline to this observation | **approximately 14 hours 34 minutes, spanning a UTC date boundary** |
| Versions observed | v1, v1.1, v2, v3 |
| Digest mismatches | none |
| Versions missing since baseline | none |

All twelve checks passed: resolves; current version v3; four prior versions; amendment reasons;
version semantics; supersession; unauthenticated access; no silent revision; date consistency;
entries retrievable; entry digests match; membership retained.

## 2. What this establishes, and what it does not

**Establishes.** The record served at `https://record.arkayarisk.com/charter/` was unchanged
over the observed interval of approximately 14 and a half hours spanning a UTC date boundary.
Every entry resolved, every entry digest matched the accepted baseline, and no version was
removed.

**Does not establish.** This is **not** a full day and it is **not** proof of indefinite
persistence. It is one observation at one later point. The record's continued integrity beyond
that point is unobserved until the next comparison, and nothing in this record should be read as
a claim about it. The earlier limits stated in the closing note are unaffected: this record says
nothing about the retrospective validity of the amendments, nothing about publication before
2026-09-16, and nothing about constituting authority, which remained not established as at
14 September 2026.

## 3. What is preserved unchanged

| Artefact | State |
|---|---|
| `PUBLICATION_LOG.md` as filed | unchanged, SHA-256 `d94b17848fca64ffc8cc63edbbb6b11d760d32a42f459d1261847c9d3732ce24` |
| Closing note as filed | unchanged, SHA-256 `8569a9e34ebf0470d3c4585b4a581a47fc69a9fdf96f95e9fa795914dd7d7df4` |
| `release-001` | unchanged, `89f6e53c65ae8405ed050ab92a9625206a6a819b` |
| `publication-001` | unchanged, `144530d0f8a4d902097fbc61995f65a6223ce905` |
| `evidence-002` | unchanged, `0f724449803822dd99c03d0b4dd94a11614a6910` |
| `evidence-003` | unchanged, `74a4693b20d8f0ac4ce07d6159842eb83e1c5b69` |
| Baseline snapshot as committed at `evidence-002` | unchanged, `9c8c6a9d853ef330f6f5d3be8f1724d49f418c6191b8edd5c79ac5f242abbd83` |
| Baseline snapshot as committed at `evidence-003` | unchanged, `f654462baf34596394299bf5343e4e3f0eca5eb2cf7fb1a61f2c73e2ba1dc16c` |

**The snapshot file advances by design; the comparison basis does not.** A clean run appends its
observation and updates the accepted-at time, so the file's digest necessarily changes. It is now
`aa34c3924c3b2c9fc8fb55ef3f5de076b16e76e4c51fa57e721a3c61747d348d`. What matters is what did not
change, and it was tested rather than assumed: the accepted digests for v1, v1.1, v2 and v3 are
byte-identical to the state committed at `evidence-003`, and the suite's own invariant refuses
any write that would drop a version or alter a retained digest. The two fields that differ are
`accepted.at` and one appended entry in `observations`.

A reader comparing the snapshot at `evidence-003` with the snapshot here will therefore see a
different file digest. That is the mechanism working, not the record changing.

## 4. Correction to the closing note, stated not overwritten

The closing note filed on 16 September 2026 records the baseline as established at
**18:00:24 UTC** and the run 2 interval as **sixteen minutes**. Both are wrong.

The snapshot's own observation log, which is the primary record, gives the baseline at
`2026-09-16T17:57:40.894345+00:00`. Run 2 at `18:16:32.021629+00:00` therefore followed it by
approximately **19 minutes**, not sixteen.

Cause: the closing-note figures were written from an approximation rather than read from the
file. The error is the assistant's.

Effect on the conclusions: none. The closing note's point was that run 2's interval was too short
to evidence persistence, and 19 minutes is no better than 16. The error does not make any filed
claim stronger than the evidence supports; it makes the recorded interval slightly shorter than
it was.

Handling: the closing note is **not** amended. It is filed, its digest sits in the ledger and in
an external sidecar, and the repository's own README states that where two records differ the
difference is a finding to be investigated and recorded, not a tie broken by silently
overwriting either copy. This section is that record.

## 5. Preservation, stated separately

Three Software Heritage visits exist for `https://github.com/djm-jpg/arkaya-charter-record`.

| Visit | Date (UTC) | Status | Snapshot |
|---|---|---|---|
| 1 | 2026-09-16T17:56:42.798Z | full | `3197c3d7d2c8bb9bcc36296a1d84eda72039f074` |
| 2 | 2026-09-16T18:15:12.766Z | **failed** | null |
| 3 | 2026-09-16T19:15:13.915Z | full | `d12c73737199f6081bf6fd9f96f43f60b77c5c5a` |

Visit 1 captured the repository as at `publication-001` (one branch, two releases). Visit 2 was
the explicit "save again" requested at 18:15 to capture the later commits; **it failed and
produced no snapshot**. Visit 3 succeeded an hour later and carries four releases with tip
revision `74a4693`, the `evidence-003` commit, at directory `0a04e28`.

So `evidence-002` and `evidence-003` are preserved, at
`swh:1:snp:d12c73737199f6081bf6fd9f96f43f60b77c5c5a`, but not by the action taken to secure it.
The requested capture failed and a later visit on Software Heritage's own schedule succeeded.
That distinction is recorded because an operator who assumes a requested capture succeeded, and
does not check, will eventually be wrong about what is preserved.

`evidence-004` itself is not preserved by any of these visits, all of which precede it. Any
snapshot naming this commit necessarily comes later.

## 6. Control observed, not merely asserted

The publication log records the `publication-tags` ruleset as operator-confirmed rather than
screenshot-captured, and notes that "Applies to 0 targets" was correct at the time because no
matching tags existed. Four now do.

Independently confirmed on 17 September 2026: the ruleset is **active and targets four tags**.
The control is operating against the tags it was written to protect. This upgrades the log's
entry from asserted to observed, and is recorded here rather than in the closed log.

## 7. Scope of this record

This record covers one observation and the three findings above. It is not a revision of the
publication set, it changes no published bytes, and the manifest remains
`b926170e96be40ce35b3e2528bb6fba2a584f79676d8251884b660af3e942ac6`.

**Resilience Capital is built. Not asserted.**
