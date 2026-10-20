# Publication record under Schema Independence Charter §6: founding-period schema decisions taken in concurrent capacities

**Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-10-19_v5 · 19 October 2026 · Layer 1 · AKR AIPS**

**Status: APPROVED FOR PUBLICATION. Publication is complete only when the frozen bytes have been deployed and verified through the public record pipeline.** Prepared under `APPROVE AR-20261019-001-zhzg8v GETV6-3 (a)` (19 October 2026, 10:10 BST); publication approved under `APPROVE AR-20261020-003-zhzg8v` (20 October 2026, 15:03 BST). The inclusions were decided on 19 October 2026 under `AR-20261019-005-zhzg8v` (V5INC-1 to V5INC-3).

**Successor to v4** (`Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-10-15_v4`, published 15 October 2026 at `https://record.arkayarisk.com/disclosures/`, SHA-256 `27e0f46a33025cd16e4375d965d79f1ddd5e12c63d9b0ffe3d4e321f875c39ec`). v3 and v4 stay published and unchanged. v5 does not repeat their entries. It covers three things: the decisions taken since v4 that v4 could not carry, two corrections to v4, and the misses since. **Its purpose is narrow: to keep the §7.6 disclosure mechanism current. It creates no new governance layer.**

**Publication cures nothing recorded below.**

---

## 1. Why this record exists

Schema Independence Charter v3 §7.6 makes a decision in which the founder's capacities conflict *"a schema-governance act published per Section 6"*. §6 requires that *"Every schema decision, version change, disciplinary-rule application and occupancy-pending null is published to the public version record."* Since 29 September 2026, every founding-period schema decision is disclosed within five business days of its effective date. Where it changes something already relied on externally, it is disclosed earlier (D-DISCLOSURE-INTERVAL, disclosed in v4). This is the second publication run under that rule.

## 2. How to read the entries

The conventions are as v4 §2 states them, unchanged:

- **Capacity.** The capacity column names the capacity in which a decision was taken. It does not determine whether the capacities conflicted on that decision.
- **Inclusion.** An entry is included for completeness. Inclusion does not determine that the entry is a schema decision within §6, or a conflicted decision within §7.6.
- **Dates.** *Effective* is when the decision took effect. *Disclosed* is when public disclosure was completed. A later disclosure date does not mean the decision was made on that date.
- **External reliance.** Recorded on every entry. Counterparties are not named.
- **Review routes.** R-§9, R-§5.1, R-V, R-7.4 and R-P are as v3 §2 defines them. R-C is as v4 §2 corrected it: **no solicitor is instructed on these questions, and none is planned.**

## 3. Entries

| Effective | ID | Decision | Capacity | Operative effect now | Does not confer | Review | External reliance | Disclosed |
|---|---|---|---|---|---|---|---|---|
| 15 Oct | AR-20261015-019 | Disposition of the second independent check of record v4 build 2. That check returned FAIL on two findings: change lists that left changes out, though every listed change was checked and found accurate. Both findings were classed as not blocking under the operating rules' R3. Build 2 went forward unchanged. The override covers change-log completeness only and sets no precedent. The FAIL report is kept unaltered | Founding Assessor, for the Custodian, deciding on a check of a record of his own decisions | Applied: record v4 was published from build 2's content. The omitted changes are listed at Section 4 item 1 | Any precedent for overriding a check finding | R-P; R-7.4 | None | By this publication, 20 Oct 2026 |
| 15 Oct | AR-20261015-020 | Publish record v4 under disclosure runbook v4 (build 3), adopted for that run only. This covers the inclusions as record v4 states them, the public registration reason, and publication on 15 October. Includes the acceptance of the publication-state diff at 17:34 BST | Founding Assessor, for the Custodian, deciding to publish a record of his own concurrent-capacity decisions | Applied: record v4 public since 15 Oct (release `publish-003`) | Any finding on the record's completeness beyond what it states | R-P | None | By this publication, 20 Oct 2026 |
| 18 Oct | AR-20261018-001 | Preparation of a private pilot: one deterministic adapter, in a private repository, for one authorised governance export, serving a named reader's decision. Existing assets are reconciled against Suite Version Register v21, and the selected pack and dependencies are pinned, "preserving issued bytes, existing grants and candidate status". No reading is signed or issued, nothing is released publicly, no licence is chosen, and no approved status is claimed | The founder, authorising preparation of a commercial pilot that uses Layer 1 material. The cited register entry does not state the capacity | Preparation only. No schema, register entry, pinned version or status changes | Signing or issuing a reading; public release; any licence; any claim of approved status | R-P | Not established by the cited register entry, which records no named reader and no authorised export | By this publication, 20 Oct 2026 |
| 19 Oct | AR-20261019-001 (GETV6-1, GETV6-3, GETV6-5) | Preparation of GET schema v6 for publication as a public draft for comment. Route: the public record pipeline, extended for the schema. v6 build 3 is unchanged and served at an address naming its version. The schema identifier `/get/1.0` is not served while v5 remains the candidate. The disclosure release is kept independent of the schema work. The notice states present control, authority and rights, and the custody pathway, with its open questions stated as open. After the second and final independent check found two blocking defects in the pipeline change for the schema, its scope was cut (GETV6-5): that change is kept out of every release, and the work goes to a next version with its own check. Publication of v6 waits on that version and on the founder's outstanding publication decisions | Founding Assessor, for the Custodian | Preparation only. Nothing is published by this decision; publication of v6 needs its own approval | Publication of v6; any statement of title, licence authority or custody beyond the records; any change to the identifier | R-§9; R-P | Yes: it governs how v6, which corrects v5, will reach the implementer that has relied on v5 since 4 Sep | By this publication, 20 Oct 2026 |

**If the decision to publish GET v6 is taken before this record is frozen, it is added here as an entry. If it is taken after, the next record carries it.**

## 4. Corrections and control failures (clause 5)

**This section is not housekeeping.** It records two corrections to record v4 and one place where the disclosure mechanism did not work as stated.

1. **Record v4's build-2 revision row is incomplete** (AR-20261015-019). It does not list four changes made in build 2. Each of the four was independently checked and found accurate:
   - the 3 September sentence in the G7-A reliance cell;
   - the 4 September 2026 date in section 4 item 4;
   - reference 11, changed from queue v5 to v6;
   - the new reference 12.
2. **Record v4 §4 item 5 is corrected** (AR-20261015-005). Record v4 states that no request or decision under that identifier is on file, and that it was not established whether a request was put. In fact a request was put on 15 October 2026. It was a routine filing request, and it was withdrawn unanswered before any decision was taken. No decision was taken under it. Record v4's statement was accurate as to the filed records searched; the request was later found in the conversation record. Nothing in record v4 relied on it.
3. **The disclosure queue was not maintained** from 15 October, after AR-20261015-019 at 16:54 BST, until 16 October. Decisions AR-20261015-020 to -029 were not added on 15 October, the day they were taken. They were added on 16 October. **This is the third such lapse.** v4 §4 item 2 records the first two.

## 5. Considered and not included, with the reason

| Date | Item | Reason not included |
|---|---|---|
| 15 Oct | AR-20261015-018: record v4 build 2 replaces build 1 under the same version; the second check is run | Preparation and checking of the record. Record v4's own revision row states build 2 |
| 15 Oct | AR-20261015-021: production approval of the record v4 deploy | It is the publication of record v4, public since 15 Oct |
| 15 Oct | AR-20261015-022 to -029: filing of a root-sweep fix pack, a commercial delivery kit (three builds) and two sets of Action Register entries; a pricing wording proposed to the price owner; a correction proposed and withdrawn (-024) | House filing, commercial positions, or withdrawn without decision. Not schema decisions |
| 16 Oct | Two disclosure-queue updates (versions 8 and 9) | Queue maintenance. The correction one of them carries is at Section 4 item 2 |
| 19 Oct | AR-20261019-001 GETV6-2: a publication-route choice | Withdrawn unanswered and replaced by GETV6-3 after review; no decision taken |
| 19 Oct | AR-20261019-003: filing of disclosure queue v10, which added the decisions of 19 October on the day they were taken | Queue maintenance |
| 19 Oct | AR-20261019-004: filing of disclosure queue v11, which added GETV6-5 on the day it was taken | Queue maintenance |
| 19 Oct | AR-20261019-006, AR-20261019-010 and AR-20261019-011: filing of disclosure queue v12, v13 and v14, each adding the decisions of 19 October on the day they were taken | Queue maintenance |
| 19 Oct | AR-20261019-009: filing of an updated internal context file in a partnership folder; nothing sent to the counterparty | House filing; not a schema decision |
| 19 and 20 Oct | The date of this run: set for 21 October on 19 October, moved to 20 October on 20 October, with 21 and 22 October kept as fallback days | Scheduling; it changes no artefact, status or claim |
| 20 Oct | AR-20261020-004: filing of disclosure queue v15, which added the decisions of 20 October on the day they were taken | Queue maintenance |

## 6. The unresolved matters, stated as unresolved

1. **Charter §8.** Whether Custodian Charter v3 §8 applies to any decision above is unresolved. No solicitor is instructed on it.
2. **The Custodian board is not constituted.** No schema version has been approved.
3. **Title to the schema estate is unvested.** The licence grantor remains open, as does whether "Arkaya remains Custodian" authorises Arkaya Risk Limited specifically. Vesting and handover to the Foundation are separate steps, and neither has occurred.
4. **The GET endpoint.** GET v1.0 has not been published. Its identifier returned HTTP 404 (not found) when checked on 19 October 2026. GET v6 has not been published.
5. **The 1.1 list** stands as v4 §6 item 5 states it.
6. **An internal target date** for GET v6 exists and is not disclosed (D11).

## 7. The publication control

- **This record is the second run under the interval rule.** The rule's review falls after the third run.
- **The earliest due date in this record is 22 October 2026** (AR-20261015-019 and -020). The record is to be published on or before that date, independent of any GET publication.
- **What closes this run** (owner DM; executed under `OPS_Disclosures_LiveSequence_Runbook_v4` as release `publish-004`, not by this record): freeze this record as a build identified by digest; deploy it through the public record pipeline with the Charter and v3 and v4 carried unchanged; live-verify; record publication from the live evidence; preserve the evidence.

## 8. What has not happened

- No schema version has been approved.
- No vector set has been adopted, and no conformance recognition has been recorded.
- GET v1.0 has not been published. GET v6 has not been published.
- Nothing in this record authorises any of those.

## 9. References

1. **Schema Independence Charter v3**, 29 July 2026. §6 publication; §7.6 the founding-period mechanism.
2. **Arkaya Layer1 Custodian Charter v3**, 30 June 2026.
3. **Arkaya_Layer1_PublicationRecord_ConflictedDecisions_2026-10-15_v4**, published 15 October 2026.
4. **OPS_DecisionRecord_PubRecordV4_Publication_2026-10-15_v1**. AR-20261015-020; basis items 2 and 3 for AR-20261015-019.
5. **OPS_PublicationLog_publish-003_2026-10-16**. The publication of record v4; deviation 10.
6. **OPS_DisclosureQueue_2026-10-20_v15**, filed 20 October 2026. Current rows, clocks and decided inclusions. **OPS_DisclosureQueue_2026-10-19_v12** for the AR-20261018-001 row at Section 1; **v11** and **v10** for the positions before the inclusion decisions and before GETV6-5. **OPS_DisclosureQueue_2026-10-16_v9** for Section 1A and the position at 16 October.
7. **AR_Register_2026-10-15_Entries001-021_v1** and **AR_Register_2026-10-15_Entries022-027_v1**. Entry AR-20261015-005.
8. **Arkaya_Governance_Founding_Period_Decision_Authority_and_Stewardship_Pathway_v3**. §2 (custody in the interval); §4.5 (vesting and handover).
9. **OPS_GET_v6_IndependentCheck_Disposition_2026-10-15_v1**. The status of v6 build 3.

## 10. Revisions

| Version | Date | Change |
|---|---|---|
| 5 (build 9) | 20 Oct 2026 | Publication-state changes only, made at the freeze step under `APPROVE AR-20261020-003-zhzg8v` (DM, 15:03 BST), for publication on 20 Oct 2026 (release `publish-004`, `OPS_Disclosures_LiveSequence_Runbook_v4`). The status line carries the time of approval and no longer refers to cells awaiting completion. Every `Disclosed` cell now carries the publication date, 20 Oct 2026; no interval was missed. Section 7's closing sequence names the runbook and the release. Entries, capacities, operative effects, what each entry does not confer, review routes, external reliance, corrections, control failures, unresolved matters and references are unchanged. Build 8 (SHA-256 `661693b4581d240bb237874dd1634a33c51d7e69e6eca0c16b3fc4350a47be13`) is superseded by this build, not withdrawn. |
| 5 (build 8) | 20 Oct 2026 | Pre-freeze publication carrier: status line and footer in the approved form, naming `AR-20261020-003-zhzg8v`; Section 5 completed for the queue filings of 19 and 20 October, one house filing and the scheduling of this run; reference 6 cites queue v15. No entry, correction or inclusion changed. |
| 5 (build 7) | 19 Oct 2026 | After the narrow verification of builds 4 to 6 (`AR-20261019-007-zhzg8v`; findings N1, N3, V1): reference 6 cites queue v12; the pilot entry's capacity and reliance cells limited to what its register entry establishes; the build 6 row completed. |
| 5 (build 6) | 19 Oct 2026 | Under `APPROVE AR-20261019-005-zhzg8v V5INC-3`: Section 5 settled as drafted; the proposed markers and the status-line note on them removed. The status line now records the inclusion decisions under AR-20261019-005-zhzg8v, V5INC-1 to V5INC-3. Unchecked when made. |
| 5 (build 5) | 19 Oct 2026 | Under `APPROVE AR-20261019-005-zhzg8v` V5INC-1 (a) and V5INC-2 (a): AR-20261019-001 is an entry (proposed marker removed); AR-20261018-001 moves from Section 5 to Section 3 as an entry. Unchecked. |
| 5 (build 4) | 19 Oct 2026 | GETV6-5 (19 October, 13:07 BST) added to the proposed AR-20261019-001 entry; the queue v11 filing added at Section 5. Reference 6 cites queue v11. Made after the second independent check, which covered build 3; this build's changes are unchecked. |
| 5 (build 3) | 19 Oct 2026 | After independent check round 1 (findings 2 and 18): Section 4 item 3 no longer counts AR-20261016-001 as added late, since it was added on the day it was taken; reference 6 cites queue v10; reference 8 gives the exact filename. |
| 5 (build 2) | 19 Oct 2026 | Section 4 item 4 removed: queue v10, carrying the decisions of 19 October, was filed that day (AR-20261019-003), so no fourth lapse arose. The filing is added at Section 5. |
| 5 (build 1) | 19 Oct 2026 | Prepared under `APPROVE AR-20261019-001-zhzg8v GETV6-3 (a)`. Three entries (one proposed); two corrections to v4 and one queue lapse, with a fourth for confirmation; seven items considered and not included. Not approved for publication. |

*AKR AIPS · v5 · APPROVED FOR PUBLICATION · Layer 1, no house identity.*
