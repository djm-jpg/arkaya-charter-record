# Publication record under Schema Independence Charter §6: founding-period schema decisions taken in concurrent capacities

**Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-10-15_v4 · 15 October 2026 · Layer 1 · AKR AIPS**

**Status: APPROVED FOR PUBLICATION. Publication is complete only when the frozen bytes have been deployed and verified through the public record pipeline.** Prepared under `APPROVE AR-20261015-017-e7xrty`; publication approved under `APPROVE AR-20261015-020-e7xrty` (15 October 2026, 17:10 BST).

**Successor to v3** (`Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-09-28_v3`, published 28 September 2026 at `https://record.arkayarisk.com/disclosures/`, SHA-256 `10400912d65cf1bfd584322874d7f178949d209f0157072908be872076926c64`). v3 stays published and unchanged. v4 does not repeat v3's entries: it discloses the decisions taken since v3, the decisions v3 recorded only in its revision rows, and the misses since. **Its purpose is narrow: to keep the §7.6 disclosure mechanism current. It creates no new governance layer.**

**Publication cures nothing recorded below.** It makes the decisions, their limits, their lateness and their open dependencies inspectable, which is what §6 requires and all that it achieves.

---

## 1. Why this record exists

Schema Independence Charter v3 §7.6 makes a decision in which the founder's capacities conflict *"a schema-governance act published per Section 6"*, and §6 requires that *"Every schema decision, version change, disciplinary-rule application and occupancy-pending null is published to the public version record."* v3 §1 sets out the basis in full.

Since 29 September 2026 a stated interval applies: every founding-period schema decision is disclosed within five business days of its effective date, and earlier where it changes something already relied on externally (D-DISCLOSURE-INTERVAL, disclosed at Section 3). This is the first publication run under that rule.

## 2. How to read the entries

**Who decided, and in what capacity.** Every decision below was taken by David McKibbin, who on each date held the concurrent capacities §7.6 names. Custodian acts are taken for Arkaya Risk Limited acting as Custodian under the founding-period measures, executed by the Founding Assessor. The capacity column names the capacity the decision was taken in. It does not determine whether the capacities conflicted on that decision.

**Inclusion.** Entries are included for completeness, on the convention v2 §3a set and v3 §2 carried. Inclusion does not determine that an entry is a schema decision within §6, or a conflicted decision within §7.6.

**Dates.** *Effective* is the date the decision took effect for founding-period work. *Disclosed* is the date public disclosure was completed. **A later disclosure date does not mean the decision was made on that date.** Where the five-business-day interval was missed, the Disclosed cell says so.

**External reliance.** Each entry states whether something it changed was already relied on outside Arkaya, and from when (interval rule, clause 6). Where it was, the rule requires disclosure no later than that reliance (clause 2). Counterparties are not named.

**Review routes**, cited by letter in the tables. R-§9, R-§5.1, R-V, R-7.4 and R-P are as v3 §2 defines them. **R-C is corrected by this record** (D12, Section 3):

| Route | Instrument | What it reviews |
|---|---|---|
| **R-C** | A solicitor, if one is instructed | Questions of company law, title, licence and construction, including Charter §8. **No solicitor is instructed on these questions and none is planned.** v3 listed R-C as if an instructing solicitor were in place; that was not so |

## 3. Entries

| Effective | ID | Decision | Capacity | Operative effect now | Does not confer | Review | External reliance | Disclosed |
|---|---|---|---|---|---|---|---|---|
| 28 Sep | D-PUBREC-COUNSEL | Record v3 is not sent to a solicitor before publication. Its disclosures on title, the licence grantor and Charter §8 are made deliberately, on founder judgement, without legal review of their effect or framing. A two-minute-earlier route giving a solicitor five business days was withdrawn unused | Founding Assessor, for the Custodian | Applied to v3. Extended by D12 (13 Oct): no solicitor is instructed on any of those questions | Any legal conclusion; any answer to the open questions | R-P | None | By this publication, 15 Oct 2026. **Interval missed** (due 5 Oct) |
| 29 Sep | D-DISCLOSURE-INTERVAL | Five-business-day disclosure interval: reliance override; clock from the Effective date; batching with separate clocks; misses disclosed as control failures; reliance recorded on every entry; review after three runs with no automatic relaxation | Founding Assessor, for the Custodian | In force from 29 Sep. This is the first run under it | Any relaxation of the interval | R-P; R-7.4 | None | By this publication, 15 Oct 2026. **Interval missed** (due 6 Oct) |
| 29 Sep | D-INTERVAL-SCOPE | The interval applies to every undisclosed founding-period schema decision, whenever taken; each keeps its own effective date | Founding Assessor, for the Custodian | In force; applied in this record | Any finding that an item is a schema decision | R-P | None | By this publication, 15 Oct 2026. **Interval missed** (due 6 Oct) |
| 6 Oct | D1 | Founding-period operating rules for Layer 1 candidate work adopted (sections 1 to 3: six strict rules and eight procedural rules). Among them: no commercial name in Layer 1; founding-period decisions never described as approved, adopted or conformant; one typed approval per release on a one-page release record; one independent check of the final bytes; at most two review rounds, after which the scope is cut | Founding Assessor, for the Custodian | In force. Governs how the decisions below were made and released | Approved status for anything made under the rules; any change to a reserved matter | R-7.4; R-P | None | By this publication, 15 Oct 2026. **Interval missed** (due 13 Oct) |
| 11 Oct | POS-11OCT | Position stated to a counterparty on GET publication terms: no implementer receives a separate publication window, consultation right or approval role; conformance test results are open to every implementer on the same terms; patents, if they matter, are dealt with through a published policy applying to every implementer. Included to the extent it is a founder-capacity dealing on the schema; counterparty and commercial detail excluded | Director of the commercial group; the position bears on the schema through publication and conformance terms | Stated to the counterparty on 11 Oct | Any exclusivity; any change to GET, its conformance criteria or its publication discipline | R-P | Stated to the counterparty on 11 Oct | Stated to the counterparty 11 Oct; publicly by this publication, 15 Oct 2026 |
| 12 Oct | G2-A | GET schema v6 is a correction-only revision within normative version 1.0. Each fix is classified against the change-control policy; any fix that changes behaviour moves to 1.1; the independent check settles the version identifier | Founding Assessor, for the Custodian | Applied: v6 classified as 1.0.1 (AR-20261015-006 below) | Candidate or approved status for v6 | R-§9 | Yes: v5 has been relied on by an implementer since 4 Sep, when its digest was given to that implementer to build against. G2-A governs its correction | By this publication, 15 Oct 2026 |
| 12 Oct | G3-A | GET v6 is published as a public draft for comment under the change-control policy, with a comment period of 21 days from publication. Release no earlier than the end of that period and the resolution of comments | Founding Assessor, for the Custodian | Not yet applied: v6 is not published. An internal target date was set with this decision and is withheld (D11) | Any shorter comment period for any implementer | R-§9; R-P | Yes: it changes how v5, relied on by an implementer since 4 Sep, will be revised. Disclosed before v6 is published | By this publication, 15 Oct 2026 |
| 12 Oct | G4-A | v6 carries an informative note on empty arrays; any normative rule on how a reader treats an empty array waits for 1.1 | Founding Assessor, for the Custodian | In v6's bytes | A reader obligation | R-§9 | None | By this publication, 15 Oct 2026 |
| 12 Oct | G5-A | v6 states in its own bytes that it is a public draft; the candidate that follows the comment period is a new editorial revision | Founding Assessor, for the Custodian | In v6's bytes | Candidate status | R-§9 | None | By this publication, 15 Oct 2026 |
| 13 Oct | D11 | The internal target date set with G3-A is withheld from this record, and the withholding is stated | Founding Assessor, for the Custodian | Applied: Section 6 item 6 | Any public commitment to a date | R-P | None | By this publication, 15 Oct 2026 |
| 13 Oct | D12 | No solicitor is instructed on the questions record v3 left open and none is planned; v3's review route R-C is corrected | Founding Assessor, for the Custodian | Applied at Section 2 | Any legal conclusion on those questions | R-P | Yes: v3 has stated R-C publicly since 28 Sep | By this publication, 15 Oct 2026, after the published statement had stood since 28 Sep |
| 13 Oct | G6-A | The `schema_version` field carries MAJOR.MINOR; a PATCH is stated on the cover and in the release record. The change-control policy's section 3 is corrected by one sentence (policy v4); the field's enumeration is not changed | Founding Assessor, for the Custodian | Carried into policy v4, released 15 Oct (below) | Approved status for the policy | R-§9 | Yes: policy v3 was given to a counterparty on 19 Aug | By this publication, 15 Oct 2026 |
| 13 Oct | G7-A | v6 replaces a false statement in v5's `auditEvent.tenant_id` description: v5 said Cryptographic Profile §3.2's prohibition of null did not apply to audit events; v6 says it does. Validation is unchanged; the null branch stays until 1.1 | Founding Assessor, for the Custodian | In v6's bytes. Section 4 records the v5 statement as relied on | Removal of the null branch | R-§9 | Yes: v5, carrying the false statement, has been relied on by an implementer since 4 Sep. The same statement was made to that implementer in correspondence on 3 Sep | By this publication, 15 Oct 2026 |
| 13 Oct | G8-A | The second review round found that a proposed v6 paragraph placed a maturity grade in an Evidence Record Specification v2 record body, which that specification excludes. Under the operating rules the paragraph is cut, the mapping of the schema's arrays to the record body goes to 1.1, and no third round is held. Two consequential edits in the cut build were read by no reviewer | Founding Assessor, for the Custodian | Applied: v6 build 3 | Any statement of how the schema's arrays map to a record body | R-§9 | None | By this publication, 15 Oct 2026 |
| 15 Oct | AR-20261015-004 | For v6 build 3 only, the G2-A independent check is met by a source-first review by an AI model (Gemini), with the other model's working paper (Codex) shown only after the first assessment was saved, and founder sign-off. **Labelled "model-assisted review with founder sign-off; no independent human review"** | Founding Assessor, for the Custodian | Applied to v6 build 3 | An independent human review; publication | R-§9; R-P | None | By this publication, 15 Oct 2026 |
| 15 Oct | AR-20261015-006 | Disposition of that check: accepted with nine recorded qualifications. All seven changed strings in v6 are a PATCH; no change to which instances validate; v6 is normative version 1.0.1 | Founding Assessor, for the Custodian | Signed disposition; v5 remains the candidate | Candidate or approved status for v6; publication | R-§9 | Yes: v5, which v6 corrects, has been relied on by an implementer since 4 Sep | By this publication, 15 Oct 2026 |
| 15 Oct | AR-20261015-009 | Change-control policy v4's out-of-date references are corrected under the same version before it comes into force (Custodian Charter v2 to v3; Schema Independence Charter v1.1 to v3) | Founding Assessor, for the Custodian | Released in v4 (AR-20261015-013) | Approved status | R-§9 | Yes: policy v3 given to a counterparty on 19 Aug | By this publication, 15 Oct 2026 |
| 15 Oct | AR-20261015-011 | Reading of the policy's compatibility matrix: "current release" identifies the companion versions pinned by the particular schema release, with their lifecycle status and any incorporated correction stated. Rejected readings: last distributed; latest on disk; approved only | Founding Assessor, for the Custodian | Applied in policy v4 §5 | Approved status for any pinned version | R-§9 | Yes: policy v3 given to a counterparty on 19 Aug | By this publication, 15 Oct 2026 |
| 15 Oct | AR-20261015-012 | The matrix's Cryptographic Profile row names v6 (candidate; a correction carried within the v5 candidate) by digest `zQmeMCM28Jk1nE3kUBLxqMc2kZcYrKhQrLG5u3S2fXQCW6m` | Founding Assessor, for the Custodian | Applied in policy v4 §5 | A release act for Profile v6; approval | R-§9 | Yes: policy v3, which named Profile v5, was given to a counterparty on 19 Aug | By this publication, 15 Oct 2026 |
| 15 Oct | AR-20261015-015 | Policy v4 further corrected before release: the commercial name removed from sections 1 and 2; the statement that a schema major-version transition triggers handover to a foundation removed, the governing charters setting four milestone conditions instead; §5 states that a row asserts no approved status; the Data Model row records that no version is pinned; §9 no longer calls the Certification Policy forthcoming | Founding Assessor, for the Custodian | Released in v4 | Approved status | R-§9 | Yes: policy v3 given to a counterparty on 19 Aug | By this publication, 15 Oct 2026 |
| 15 Oct | AR-20261015-016 | Policy v4 §2 normative correction: "A schema release pins one version of each companion specification it depends on; the set it pins, and any companion it does not yet pin, is recorded in the compatibility matrix." The Data Model row reads "not yet pinned (Pillar 2)" | Founding Assessor, for the Custodian | Released in v4 | Approved status | R-§9 | Yes: policy v3 given to a counterparty on 19 Aug | By this publication, 15 Oct 2026 |
| 15 Oct | AR-20261015-013 | Release of change-control policy v4, conditional on a clean independent check. Round 1 failed an earlier build on four findings; round 2 passed build 4 (SHA-256 `498ae60e922ce612982f48aa3aa0c93f0090caedec2fb47dbe5255e611b7f465`). **Operative by founder decision; not approved.** Policy v3 retained in place while a release manifest still pins it | Founding Assessor, for the Custodian | Operative; released 15 Oct | Approved status; suite membership | R-§9; R-7.4 | Yes: replaces the policy given to a counterparty on 19 Aug | By this publication, 15 Oct 2026 |
| 15 Oct | AR-20261015-017 | This record is published before GET v6, and each publication has its own approval | Founding Assessor, for the Custodian | Governs this run: this record is to be published before v6. Neither is published at the date of this build | Publication of v6 | R-P | None | By this publication, 15 Oct 2026 |

## 4. Control failures and corrections (clause 5)

**This section is not housekeeping.** It records where the disclosure mechanism did not work as stated.

1. **Four intervals missed.** D-PUBREC-COUNSEL (due 5 Oct), D-DISCLOSURE-INTERVAL and D-INTERVAL-SCOPE (due 6 Oct), and D1 (due 13 Oct) are disclosed late by this record. The rule's own decision was disclosed late.
2. **The disclosure queue was not maintained** from 30 September to 11 October, and again from 13 to 15 October: decisions were not added on the day they were taken. Each was found and added later.
3. **v3's review route R-C** stated a review route through an instructing solicitor that did not exist. Corrected at Section 2 (D12).
4. **A false statement in a relied-on schema.** GET schema v5, a candidate relied on by an implementer since 4 September 2026, states that Cryptographic Profile §3.2's prohibition of null does not apply to audit events. It does. v6 corrects the description (G7-A). Until v6 is published, v5 still carries the statement; validation is unaffected.
5. **A record gap.** The identifier AR-20261015-005 falls in the sequence of decisions recorded on 15 October, but no request or decision under it is on file. Whether a request was put or a decision taken under it is not established. Nothing in this record relies on it.

## 5. Considered and not included, with the reason

| Date | Item | Reason not included |
|---|---|---|
| 28 Sep | D-PUBREC-V3-B4: counterparty identities neutralised in the prepared record | Stated publicly in v3's revision rows, with its time, on 28 Sep |
| 28 Sep | D-PUBREC-FINALISE: v3 publication-state build and approval to publish | The publication of v3 is itself the disclosure; v3's revision row states it |
| 28 Sep | D-PUBREC-PIPELINE: a second namespace on the public record pipeline | Publication infrastructure; decides nothing about the schema. The namespace is public |
| 28 Sep | D-RUNBOOK-0006: a pipeline patch and runbook adopted | Operating tooling |
| 28 Sep | D-PROD-PUBLISH-002: production approval of the v3 deploy | It is the publication of v3, public since 28 Sep |
| 12 Oct | Commercial and pilot positions (call time; a prospective reader held in reserve; a first-reading funding rule; disclosure priority) | Not schema decisions |
| 12 to 13 Oct; 15 Oct | Filing of working papers, check evidence and receipts; re-issue of the operating rules with a header-only change | House filing |
| 15 Oct | A proposed reading of the matrix column (AR-20261015-010) | Not accepted: withdrawn on a factual error |
| 15 Oct | An installation request for policy v4 as first built (AR-20261015-008) | Superseded before execution |
| 15 Oct | AR-20261015-003 | Withdrawn unanswered; no decision taken |

## 6. The unresolved matters, stated as unresolved

1. **Charter §8.** Whether Custodian Charter v3 §8 applies to any decision above is unresolved, as v3 §6 item 1 records. **No solicitor is instructed on it** (D12). Nothing here concludes that the founder is outside §8.
2. **The Custodian board is not constituted.** No schema version has been approved. Policy v4 is operative by founder decision and is not approved.
3. **Title to the schema estate is unvested**, and the licence grantor remains open.
4. **The GET endpoint.** GET v1.0 has not been published. Its identifier returned HTTP 404 (not found) when checked on 15 October 2026 at 15:23 UTC.
5. **The 1.1 list.** The mapping of the schema's arrays to the Evidence Record Specification v2 record body, removal of the `tenant_id` null branch, and the other items deferred from v6 are open for 1.1.
6. **An internal target date** for GET v6 exists and is not disclosed (D11). The operating rules keep internal targets internal.

## 7. The publication control

- **This record is the first run under the interval rule.** The rule's review falls after the third run (clause 7).
- **Order of publication.** This record is published before GET v6, so that the decisions changing what an implementer relies on are disclosed before v6 reaches that implementer (clause 2; AR-20261015-017).
- **What closes this run** (owner DM; executed under `OPS_Disclosures_LiveSequence_Runbook_v4` as release `publish-003`, not by this record): freeze this record as a build identified by digest; deploy it through the public record pipeline with v3 and the Charter carried unchanged; live-verify; record publication from the live evidence; preserve the evidence.

## 8. What has not happened

- No schema version has been approved.
- No vector set has been adopted, and no conformance recognition recorded.
- GET v1.0 has not been published. GET v6 has not been published.
- Nothing in this record authorises any of those.

## 9. References

1. **Schema Independence Charter v3**, 29 July 2026. §6 publication; §7.6 the founding-period mechanism.
2. **Arkaya Layer1 Custodian Charter v3**, 30 June 2026. §5.1, §8, §9, §13.
3. **Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-09-28_v3**, published 28 September 2026. §2 review routes; §6 unresolved matters.
4. **OPS_DecisionRecord_DisclosureInterval_2026-09-29_v2**. D-DISCLOSURE-INTERVAL and D-INTERVAL-SCOPE.
5. **Arkaya_Governance_Founding_Period_Operating_Rules_v2**. D1 (6 October 2026).
6. **OPS_GET_v6_BuildNote_2026-10-13_v3**. G2-A to G8-A as built; the two review rounds; the 1.1 list.
7. **OPS_GET_v6_IndependentCheck_Disposition_2026-10-15_v1** and **OPS_GET_v6_GeminiReview_Record_2026-10-15_v1**. AR-20261015-004 and -006.
8. **OPS_DecisionRecord_PolicyMatrixReading_2026-10-15_v3**. AR-20261015-011, -012, -016.
9. **OPS_Layer1_VersioningPolicy_v4_Release_v1**. AR-20261015-013, with -009 and -015.
10. **Arkaya Layer1 Versioning Compatibility and Change-Control Policy v4**, build 4, 15 October 2026.
11. **OPS_DisclosureQueue_2026-10-15_v6**. The candidates, their clocks and the inclusion assessments.
12. **OPS_Layer1_GETv1-0_Publication_RunBook_v2** §1 and **OPS_Evidence_DisclosureRecord_v4_Reliance_and_Endpoint_2026-10-15_v1**. The start of external reliance on GET v5 (4 September 2026); the endpoint check of 15 October 2026.

## 10. Revisions

| Version | Date | Change |
|---|---|---|
| 4 (build 3) | 15 Oct 2026 | Publication-state changes only, made at the freeze step under `APPROVE AR-20261015-020-e7xrty` (DM, 17:10 BST), for publication on 15 Oct 2026 (release `publish-003`, `OPS_Disclosures_LiveSequence_Runbook_v4`). The header and footer status now read true before and after deployment. Every `Disclosed` cell now carries the publication date, 15 Oct 2026; the missed intervals, the earlier statement to the counterparty and the period v3's R-C statement stood are kept. Section 7's closing sequence names the runbook and the release. Decisions, capacities, operative effects, what each entry does not confer, review routes, external reliance, control failures, unresolved matters and references are unchanged. Build 2 (SHA-256 `12c509bd945c4799f5f6c062e4b03ded5882b89f5ab1b858aba39689abef29cc`) is superseded by this build, not withdrawn. |
| 4 (build 2) | 15 Oct 2026 | Corrected before publication after the first independent check. The start of external reliance is now stated in each entry's own cell for G2-A, G3-A, G7-A, AR-20261015-006, -011, -012, -015 and -016. POS-11OCT no longer states whether a term was agreed. The AR-20261015-005 gap is stated as final. The endpoint status is re-checked and dated. AR-20261015-017's present effect is reworded so it cannot be read as a completed publication. Build 1 withdrawn and retained. Not published. |
| 4 (build 1) | 15 Oct 2026 | Prepared under `APPROVE AR-20261015-017-e7xrty`. Twenty-three entries; four missed intervals and two queue lapses disclosed; v3's R-C corrected; a false statement in a relied-on schema recorded; ten items considered and not included. Two items marked for resolution before freeze. Withdrawn. |

*AKR AIPS · v4 · APPROVED FOR PUBLICATION · Layer 1, no house identity.*
