# Publication record under Schema Independence Charter §6: founding-period schema decisions taken in concurrent capacities

**Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-09-28_v3 · 28 September 2026 · Layer 1 · AKR AIPS**

**Status: APPROVED FOR PUBLICATION. Publication is complete only when the frozen bytes have been deployed and verified through the public record pipeline.** Adopted as the prepared publication record by DM on 28 September 2026 at 19:22 BST (D-PUBREC-V3).

**Successor to v2** (`Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-09-10_v2`, prepared 10 September 2026, never published), which is archived unchanged at `Governance/_Superseded/`. v3 carries forward every decision v2 prepared, so that publishing v3 alone discloses everything v2 would have. It adds one decision that predates v2's cut-off and was not in it, and the decisions taken since. **Its purpose is narrow: to make the §7.6 disclosure mechanism current. It creates no new governance layer.**

**Publication cures nothing recorded below.** It makes the decisions, their limits and their open dependencies inspectable, which is what §6 requires and all that it achieves.

---

## 1. Why this record exists

Schema Independence Charter v3 §7.6:

> "The interval before handover concentrates more than one capacity in the founder: author of this Charter, director of the custodian company, and director of the commercial group. The Charter does not pretend otherwise."

> "fiduciary duties are owed separately in each capacity, and a decision in which those capacities conflict, including any dealing between the custodian and the commercial group, is a schema-governance act published per Section 6."

§6:

> "Every schema decision, version change, disciplinary-rule application and occupancy-pending null is published to the public version record."

The operating basis is `Arkaya_Governance_Founding_Period_Decision_Authority_and_Stewardship_Pathway_v3` (28 September 2026). Founding-period decisions are made and recorded under this mechanism. Where capacities conflict, the decision is disclosed, remains open to later independent review, and acquires no status reserved elsewhere merely because the founder made it.

## 2. How to read the entries

**Who decided, and in what capacity.** Every decision below was taken by David McKibbin. On each date he held the concurrent capacities §7.6 names. From 5 September 2026, Custodian acts are taken for Arkaya Risk Limited acting as Custodian under the founding-period measures, executed by the Founding Assessor (decision A10; D-GET-01 §1). Whether "Arkaya remains Custodian" authorises Arkaya Risk Limited specifically is open (D-GET-01 §4(a)). The capacity column names the capacity the decision was taken in. It does not determine whether the capacities conflicted on that decision.

**Inclusion.** Entries are included for completeness, on the convention v2 §3a set. Inclusion does not determine that an entry is a schema decision within §6, or a conflicted decision within §7.6. A narrow reading of either, made by the person whose decisions they are, would be the drafter construing his own instrument in his own favour.

**Two dates for every entry.**
- *Effective* is the date the decision took effect for founding-period work.
- *Disclosed* is the date public disclosure was completed.

The gap between them is the publication lag, and it is shown rather than hidden. **A later disclosure date does not mean the decision was made on that date.**

**Standard review routes**, cited by letter in the tables:

| Route | Instrument | What it reviews |
|---|---|---|
| **R-§9** | Custodian Charter v3 §9 | The board's approval of the transition into `approved`. That approval is the independent review of the founding-period decision that produced the candidate |
| **R-§5.1** | Custodian Charter v3 §5.1 | The reserved matters, including a major schema version, by two-thirds supermajority |
| **R-V** | Cryptographic Profile v6 §9; Profile v5 candidate release v2 §2.2 | Vector adoption, the act that makes conformance claimable |
| **R-7.4** | GET Ltd articles v3 art. 7.4, on adoption | Reopening of determinations made while the custodian has no independent director, by the first independent directors, within twelve months of their appointment |
| **R-C** | Instructing solicitor | Questions of company law, title, licence and construction, including Charter §8 |
| **R-P** | This record, once published | Inspection by any reader, including the first independent directors. An absent decision cannot be reviewed |

## 3. Part A: decisions carried forward from v2, with one late inclusion

| Effective | ID | Decision | Capacity | Operative effect now (as recorded; not re-examined here except where stated) | Does not confer | Review | Disclosed |
|---|---|---|---|---|---|---|---|
| 4 Sep | D-3 | GET v1.0 designation: normative version 1.0 in `schema_version` and on the cover; editorial revision v5 in the filename | Founding Assessor, for the Custodian | The designation stands. **GET v1.0 has not published.** Both `/get/1.0` hosts returned 404 on 28 September (readiness gate v3, item 5) | Approval; publication | R-§9, R-§5.1 | By this publication, 28 Sep 2026 |
| 4 Sep | D-4 | Schema v5 accepted as candidate, R-1 to R-5 as drafted | Founding Assessor, executive act under §9 | Candidate: buildable, not claimable | Adoption; approval | R-§9, R-§5.1 | By this publication, 28 Sep 2026 |
| 4 Sep | D-7 | `$id` set to `/get/1.0` | Founding Assessor | Identifier fixed. The endpoint does not resolve (Section 6) | A resolvable locator | R-§9 | By this publication, 28 Sep 2026 |
| 5 Sep | A10 | Publisher and signer: Arkaya Risk Limited as Custodian | Founding Assessor; director of the named company | Governs any GET publication. **Asserts no ownership** of the schema estate | Title; licence authority | R-C (D-GET-01 §4(a), (b)); R-P | Stated to the counterparty 6 Sep; publicly by this publication, 28 Sep 2026 |
| 6 Sep | A9 | Cryptographic Profile v6 of record: the 6 September edition, 45,965 bytes, `zQmeMCM28…` | Profile owner | Profile v6 is the candidate built against. The bytes are preserved; correction notice v7 applies (Part B) | A companion selection; approval | R-§5.1 (MAJOR); R-V | By this publication, 28 Sep 2026 |
| **6 Sep** | **D1 (late inclusion)** | **Profile v6 takes no candidate-release act of its own; it is a correction carried within the v5 candidate, under the v5 executive act of 11 August** | Profile owner | Profile v6 is buildable on the same footing as v5 and no more claimable. **No further act for v6 is owed.** Recorded in the Suite Version Register and correction notice v7 §2 | A release act; approval | R-§5.1; R-V | Stated to the counterparty 6 Sep (correction notice v7 ref. 2); publicly by this publication, 28 Sep 2026. **Omitted from v2 without a stated basis; included here on the v2 §3a convention** |
| 6 Sep | D-GET-01 | Publication disposition D: publication proceeds with title to the schema estate unvested and not asserted | Founding Assessor, for the Custodian | The footing for any GET publication. Leaves §4(a) to (e) expressly open, including the licence grantor | Title; vesting; a publication act | R-C; R-P | By this publication, 28 Sep 2026 |
| 8 Sep | none | `id_resolution` resolution rule accepted: two routes, five conditions on the second | Founding Assessor | Accepted, not invoked | Invocation; clearance of the field | R-§9 | By this publication, 28 Sep 2026 |
| 8 Sep | none | Two companion-field corrections to the release manifest, accepted and applied (manifest v7) | Founding Assessor | Applied. Neither selects a companion, establishes compatibility or distribution permission, nor clears signing | Companion selection; signing | R-§9 | By this publication, 28 Sep 2026 |
| 9 Sep | Route C | Route C and the separate dependency record endorsed | Founding Assessor | Endorsement only. Authorised adoption remains open at Release Decision Register item R-4 | Adoption | R-§9 | By this publication, 28 Sep 2026 |
| 10 Sep | none | The R-2/R-3 limitation recorded as determined: the evidence examined does not establish the old citation's complete reader obligations | Founding Assessor | Records what the evidence does not establish. Determines no reading | Any reading of the citation | R-§9; R-7.4 | By this publication, 28 Sep 2026 |
| 10 Sep | E1 | Composite reading of the citation; MINOR; treatment split at the same location | Founding Assessor | As recorded at 10 Sep: the compatibility rationale is outstanding, so E1 is unavailable as build authority. Not re-examined here | Build authority; any change to version or `$id` | R-§9; R-7.4 | By this publication, 28 Sep 2026 |

## 4. Part B: decisions taken after v2's cut-off

| Effective | ID | Decision | Capacity | Operative effect now | Does not confer | Review | Disclosed |
|---|---|---|---|---|---|---|---|
| 14 Sep | none | **Publication-method rule under a counterparty covenant:** Arkaya does not change its publication method to accelerate commencement under the covenant; if ordinary release discipline already publishes a version-and-digest identification, that satisfies a condition of that covenant at publication (as recorded in readiness gate v3) | Founding Assessor and director of the commercial group together. The decision concerns publication of the schema, and a commercial covenant turns on it | Stands. Applied by readiness gate v3 | Any commercial term; any change to publication discipline | R-P; R-C | By this publication, 28 Sep 2026 |
| 16 Sep | none | **Schema Independence Charter public record published** through the Arkaya pipeline at `record.arkayarisk.com` (production approval 16:49:17Z; `OPS_Charter_PublicationLog_2026-09-16`) | Charter author, for the Custodian | Published and live. The first run of the record pipeline | Any Charter change | R-P; R-7.4 | **16 Sep 2026** (the publication is itself the disclosure) |
| 16 Sep | none | **Vector set version 2 fixed as the authoritative Profile v6 candidate** (`vectors_v6.json`, 22,641 B, SHA-256 `a19c56b1…8342`, set digest `zQmSyj49…Yifj`); the provisional 3 September set and generator moved to `_Superseded/`, bytes preserved | Profile owner, on DM instruction (basis: an internal readiness check of 16 September 2026, §5 item 5) | Candidate vectors: the oracle for building and testing | **Adoption; normative status; any conformance claim** | R-V | By this publication, 28 Sep 2026 |
| 21 Sep | none | **Correction notice for Cryptographic Profile v6 prepared on DM's authorisation of 21 September**, the v7 edition being held pending fresh authority for its exact bytes: it corrects the Profile's Status-line statement that a v6 candidate-release act was owed, and records that a ruled §9 clarification did not enter the issued text; Profile bytes preserved | Profile owner | The notice does not assert its own issue state. **Whether, when and on what authority v7 was issued is recorded in its control records and is not determined here** | Any change to Profile v6; a release act | R-P | By this publication, 28 Sep 2026 |
| 28 Sep, 11:33 BST | none | **Counterparty collaboration position adopted**, to the extent it is a founder-capacity dealing on the schema: the commercial group's position on the relationship between an external evidence producer and Arkaya's reader-side layer is stated as layered and non-exclusive, and the position records that GET v1.0 publishes on Arkaya's own release gate and not to change that commercial position. **Included on DM's direction of 19:22 BST. Commercial terms, negotiation detail and counterparty material are excluded from this record** | Director of the commercial group; the position bears on the schema through GET publication and conformance | Internal position. Nothing sent, published or put to the counterparty (the internal position record of 28 September 2026, status line; reference 18) | Any schema decision; any change to GET, its conformance criteria or its publication discipline; any exclusivity | R-P; R-C | By this publication, 28 Sep 2026 |
| 28 Sep | D-ERS-LINEAGE | The two Evidence Record Specifications hold different roles and neither supersedes the other. Layer 1 ERS v2 governs record form for new work. GET ERS v6 remains the Methodology's assessment reference and the carve-out source. No new normative content goes into GET ERS v6; new record semantics go into the Data Model | Founding Assessor, for the Custodian | Stands (decision record v2; v1 superseded the same day and not to be relied on) | Adoption of Route C (still open at R-4); approval of either specification | R-§9; R-7.4 | By this publication, 28 Sep 2026 |
| 28 Sep | D-DM-V2-ISSUE | **Data Model Specification v2 issued as a candidate**, with amendments A and C and the reference 7 condition; compatibility class MAJOR against v1 | Founding Assessor, for the Custodian | Candidate, buildable. Recorded in the Suite Version Register v20 as in force pending v3 approval; no dependant is repointed to v3. Of the version-pinned dependants, one pins v2 (Attestation Gates v4, reference 5), one pins v1 (Document Map v2) and one lists the Data Model as forthcoming (Versioning Policy v3) | Approval. **As MAJOR, approval is a §5.1 reserved matter** | R-§9; R-§5.1 | By this publication, 28 Sep 2026 |
| 28 Sep, 17:42 BST (Homing Map v2) | D-DM-V3-HOME | The ratified W3 homing is kept. The Data Model owns meaning, the Stage Payload companion owns grammar, the Evidence companion owns Evidence-stage expression, and GET ERS v6 is provenance only. No Conflict Adjudication v8 or Manifest v3 on this basis | Founding Assessor | Governs how v3 was built | Any change to the ratified W3 register | R-§9 | By this publication, 28 Sep 2026 |
| 28 Sep, 17:54 BST (v3 delta v2) | D-DM-V3-DELTA | The v3 delta dispositions: SH-1 accepted on condition; F1 accepted; S-1 declined as framed (a source system is a distinct role, not an Agent); P-1 and A-1 accepted; R-A deferred; `verification_mode` made a separate Taxonomy reconciliation item | Founding Assessor | Built into v3. R-A and the A-1 residual remain open | Any Taxonomy change: `verification_mode` is a protected schema decision (Schema Independence Charter v3 §3) and is not decided here | R-§9; R-7.4 | By this publication, 28 Sep 2026 |
| 28 Sep (time not in a filed record) | SH-1-TERM (named in Data Model v3's authority lines) | "Contact not established" adopted as the candidate term for the source-health state previously called "offline" | Founding Assessor | A Term Register candidate in state *proposed* (`Arkaya_TermRegister_ContactNotEstablished_Candidate_v1`). Its adoption conditions are that v3 is approved, the Stage Payload companion adopts a member value, and the register takes the entry | Adoption into the Term Register; a member value | R-§9; R-P | By this publication, 28 Sep 2026 |
| 28 Sep, 18:11 BST | D-DM-DATAMODEL-V3 | **Data Model v3 candidate text accepted**, with the mixed-axis source-health refinement; transition to approved **held**; no repoint of normative dependants and no archival of v2 until approval. Record corrected at 18:18 BST (decision record v2), disposition unchanged | Founding Assessor, for the Custodian | **Data Model v3 is a candidate: buildable and testable now, not approved.** It is classified MINOR against v2 | **Approval.** The hold condition is a validly constituted board approving under §9 | R-§9 | By this publication, 28 Sep 2026 |
| 28 Sep, 19:02 BST | D-FOUNDING-AUTHORITY | Founding-period decisions are made and recorded under the §7.6 mechanism, disclosed where capacities conflict, and open to later independent review. They confer no status reserved elsewhere. Five boundaries are set, each stated from its governing instrument. Recognition is held until the GET Ltd art. 7.3 independence condition is met. Charter §8 is kept expressly open. **Corrected at v2 the same day (D-PATHWAY-V2, 19:22 BST):** §4.2 now reflects D1, so Profile v6 owes no separate candidate-release act | Founding Assessor, for the Custodian, and Charter author | Governs how founding-period work proceeds, at v2 | Any finding on §8; any Charter amendment; any status | R-7.4; R-P; R-C | By this publication, 28 Sep 2026 |

## 5. Considered and not included, with the reason

Stated so that no exclusion is silent.

| Date | Item | Reason not included |
|---|---|---|
| 16 Sep | Implementer pack v3 prepared for an implementer | A distribution act, not a schema decision. Its despatch state is not established by this record |
| 28 Sep | A partner-folder move order; three-way routing rule; root `CLAUDE.md` v21; Layer 1 `CLAUDE.md` v2 | House filing and routing, not schema decisions |
| 28 Sep | Suite Version Register v20 | A register update. It records identity and status and decides nothing (its own change block says so) |
| 28 Sep | GET v1.0 readiness gate item 9 reclassified as a director decision | Identifies a decision still to be taken; takes none |

## 6. The unresolved matters, stated as unresolved

1. **Charter §8.** Custodian Charter v3 §8 bars a person from *"both steering a Layer 2 engine and deciding the standard that engine is tested against"* and provides that *"A schema decision taken in breach of recusal is void."* **Whether §8 applies to any decision above is unresolved.** It has not been determined, it has not been closed on judgement, and this record does not settle it. **Nothing here concludes that the founder is outside §8.** The note of 11 August sets out three readings and states the owner's working view at moderate confidence. The decision record of 10 September records steering as not established for either engine; that is a finding of absent evidence, not a finding on the bar. The question sits with the instructing solicitor.
2. **The Custodian board is not constituted.** No schema version has been approved. Data Model v3 in particular is a candidate, not approved.
3. **Title to the schema estate is unvested**, and the licence grantor remains open (D-GET-01 §4(b)).
4. **The GET endpoint.** `https://record.arkayarisk.com/get/1.0` and `https://arkayarisk.com/get/1.0` returned HTTP 404 on 28 September 2026 (readiness gate v3, item 5). **This is a GET release issue.** It does not prevent this record from being published through the working record pipeline (Section 7).
5. **E1's compatibility rationale** was outstanding at 10 September and has not been re-examined here.

## 7. The publication control, stated separately from the decisions

**This is a control failure, not housekeeping.** It is recorded apart from the decisions because it concerns the mechanism, not any decision's merits.

- **The control.** Schema Independence Charter §§6 and 7.6 make publication the control that carries independence in the founding period: *"The transition is carried by disclosure and structure, not by the founder's restraint"*.
- **The failure.** Before this publication, no decision in Sections 3 and 4 had been publicly disclosed, except the 16 September Charter publication itself. The lag ran from 4 September for the oldest entry, and v2 stood prepared, unpublished, from 10 September.
- **The channel exists.** The record pipeline at `record.arkayarisk.com` ran end to end on 16 September for the Schema Independence Charter, with production approval, live verification, served manifest digest and external captures (readiness gate v3, item 6). **This record can be published through that channel.** The address for it is fixed at the publication act. The unresolved GET endpoint at Section 6 item 4 is a separate matter and does not block it.
- **A correction made in the pathway record.** `Arkaya_Governance_Founding_Period_Decision_Authority_and_Stewardship_Pathway_v1` §4.2 stated that Profile v6's executive candidate-release act was owed, repeating a Profile Status-line statement that correction notice v7 records as incorrect. The pathway record was corrected at v2 the same day (D-PATHWAY-V2), and v1 is archived unchanged.
- **What closes the failure** (owner DM; the sequence is executed under `OPS_Disclosures_LiveSequence_Runbook_v3`, not by this record):
  1. Freeze this record as build 5, identified by digest.
  2. Deploy the frozen release through the established record pipeline, carrying the published Charter unchanged.
  3. Live-verify the frozen bytes at `record.arkayarisk.com`, from an environment able to observe real HTTP and TLS behaviour.
  4. Record publication from that live evidence.
  5. Preserve the publication evidence and the later baseline checks.

  From then on, each founding-period schema decision is disclosed within a stated interval of its effective date.

## 8. What has not happened

- No schema version has been approved.
- No vector set has been adopted.
- No conformance recognition has been recorded.
- GET v1.0 has not been published.
- Nothing in this record authorises any of those. This record is itself published only by the act at Section 7.

## 9. References

1. **Schema Independence Charter v3**, 29 July 2026. §3 protected schema decisions; §6 publication; §7.6 the founding-period mechanism. Published on the public record on 16 September 2026.
2. **Arkaya Layer1 Custodian Charter v3**, 30 June 2026. §5.1 reserved matters; §8 conflicts; §9 lifecycle.
3. **Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-09-10_v2**, `10-Layer1-Custodian/Governance/_Superseded/`. Prepared, never published. The predecessor, archived unchanged; §3a is the completeness convention.
4. **OPS_Release_Decision_Register_2026-09-10_v5** §1. The source of the Part A entries.
5. **Arkaya_Layer1_DecisionRecord_GETv1_Publication_Disposition_v2** (D-GET-01), 6 September 2026.
6. **Arkaya_Layer1_CorrectionNotice_CryptographicProfile_v6_v7**, 21 September 2026. §2 records ruling D1 and the Status-line correction; §7 the authorisation and issue-state basis.
7. **Suite Version Register v20**, 28 September 2026. Profile v6 row (D1); Data Model v2 and v3 rows; the Data Model reverse-dependency row.
8. **vectors_v6_candidate_MOVED_README.md**, 16 September 2026. The authoritative vector set version 2 and the move record.
9. **OPS_GET_v1-0_ReadinessGate_2026-09-28_v3**. Item 5, the 404 check; item 6, the 16 September pipeline run; the 14 September rule.
10. **OPS_DecisionRecord_ERSLineage_2026-09-28_v2**. D-ERS-LINEAGE.
11. **Arkaya Layer1 Data Model Specification v2** and **v3**, 28 September 2026. Status and authority lines; v3's authority lines name the SH-1-TERM decision.
12. **OPS_DecisionRecord_DataModelV3_2026-09-28_v2**. D-DM-DATAMODEL-V3 and the hold condition.
13. **Arkaya_TermRegister_ContactNotEstablished_Candidate_v1**. SH-1-TERM.
14. **Arkaya_Governance_Founding_Period_Decision_Authority_and_Stewardship_Pathway_v3**, 28 September 2026. D-FOUNDING-AUTHORITY, with §4.2 corrected at v2 on D-PATHWAY-V2 and citations repointed to this record at v3; v1 and v2 are archived at `Governance/_Superseded/`.
15. **GOV_Custodian_Board_Composition_S8_Related_Party_Question_v2**, 11 August 2026, and **Arkaya_Layer1_DecisionRecord_GETv1_ConflictedCustody_v10** §7. The §8 question and the steering finding.
16. **OPS_Prepared_DataModel_v3_Delta_2026-09-28_v2**, `00-Group/99-Working/`. D-DM-V3-DELTA as decided, with its time.
17. **OPS_HomingMap_GETERS6_s7.3-7.6_2026-09-28_v2**, `00-Group/17-Compliance/06-Audit-Trail/`. D-DM-V3-HOME, decided 28 September 2026 at 17:42, option (a).
18. **Internal position record, 28 September 2026**, held in the Layer 1 estate and not identified further here, so as not to identify the counterparty. §1, the adopted position (11:33 BST), and the status line recording that nothing was sent, published or put to the counterparty. Cited for the schema-bearing element only.

## 10. Revisions

| Version | Date | Change |
|---|---|---|
| 3 (build 5) | 28 Sep 2026 | Publication-state changes only, made at the freeze step under D-PUBREC-FINALISE (DM, 19:38 BST), for publication on 28 Sep 2026 (run 1, `OPS_Disclosures_LiveSequence_Runbook_v3`). The header status now reads true before and after deployment. Every `Disclosed` cell for a decision this record discloses now reads "By this publication, 28 Sep 2026"; the two rows already stated to the counterparty keep that fact; the Schema Independence Charter row keeps 16 Sep 2026. §7's statement of the failure is put in the past, and its closing sequence replaced by freeze, deploy, live-verify, record and preserve. The §8 publication sentence and the footer status are conformed. Decisions, capacities, operative effects, what each entry does not confer, review routes, unresolved matters, §8 treatment and legal caveats are unchanged. Build 4 (SHA-256 `e99cf1e5e3fa00df1ff29ef788deb063a6826139571bd64a230f2ed281ae9350`) is superseded by this build, not withdrawn. |
| 3 (build 4, superseded by build 5) | 28 Sep 2026 | Disclosure-minimisation correction before use, on D-PUBREC-V3-B4 (DM, 19:30 BST), under the same pre-use carrier rule. Counterparty identities neutralised: one counterparty is now referred to as "a counterparty" and one as "an implementer"; internal file titles and descriptions that would identify either are replaced by neutral descriptions; the revision history is conformed so that it does not repeat them. **Decision dates, capacities, operative effects, what each entry does not confer, review routes and the §8 treatment are unchanged.** Build 3 (SHA-256 `cf245ba82d65eda6abeea64646a8e81587f976bb69b0242a06e1dfa2ed9c1436`) is **withdrawn**, preserved unchanged at `Governance/_Superseded/`. Not published. |
| 3 (build 3, withdrawn) | 28 Sep 2026 | Disclosure-minimisation correction before use, on DM's approval of 19:26 BST, under the same pre-use carrier rule: the 14 September entry's clause-level reference to the unexecuted counterparty covenant replaced by a general reference to a condition of that covenant. The clause reference is not repeated here, since repeating it would defeat the correction; the withdrawn build 2 preserves the prior wording. Consequential citation currency in the same build: §1's operating basis and reference 14 repointed to pathway v3, issued the same minute. The decisions disclosed are unchanged. The decision disclosed and its evidential proposition are unchanged. Build 2 (25,088 B, SHA-256 `5f127ffc45d005bbadd2bef0a298cf22f7d536a6fac2bb959fdede5c1cf152f0`) is **withdrawn**, preserved unchanged at `Governance/_Superseded/`. Not published. |
| 3 (build 2, withdrawn) | 28 Sep 2026 | **Adopted as the current prepared record on D-PUBREC-V3 (DM, 19:22 BST), on the condition that the counterparty collaboration position is included, limited to its founder-capacity schema dealing.** Corrected under the same version before adoption, following DM's carrier-versioning rule: the counterparty collaboration entry moved from Section 5 into Part B, stripped of commercial and counterparty material; the D-FOUNDING-AUTHORITY entry and Section 7 updated for the pathway correction made the same day (D-PATHWAY-V2); v2 and pathway v1 references repointed to their archived locations. Build 1 (23,060 B, SHA-256 `1785c785f423bb9fcfae4bdc5da59c61a6d51ae74472f07d7e34ea95fc8f9d46`) is **withdrawn**, preserved unchanged at `Governance/_Superseded/` under a name recording the withdrawal. Not published. |
| 3 (build 1, withdrawn) | 28 Sep 2026 | Prepared at DM's instruction of 19:15 BST: make the §7.6 disclosure mechanism current. v2's eleven entries carried forward; D1 (6 Sep) included late, having been omitted from v2 without a stated basis; eleven post-cut-off entries added; each entry now carries capacity, operative effect now, what it does not confer, review route, and separate effective and disclosed dates; exclusions stated with reasons; the publication control failure stated apart from the decisions; the record pipeline named as the available channel; `/get/1.0` confined to the GET release issue; a correction owed in the pathway record disclosed. Gated under the ANALYSIS profile before filing: four findings under 2.3a corrected in the draft (the correction-notice state, the Data Model v2 dependants, the D-DM-V3-HOME source, and an unfiled time for SH-1-TERM). Not published. |
| 2 | 10 Sep 2026 | Two entries added to v1's nine, with the mapping to the register stated. Prepared, not published. Retained unchanged. |
| 1 | 10 Sep 2026 | Nine entries. Superseded by v2 the same day. |

*AKR AIPS · v3 · APPROVED FOR PUBLICATION · Layer 1, no house identity.*
