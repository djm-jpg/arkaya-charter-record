# Public version record: acceptance suite v10

Internal record. 14 September 2026. Supersedes v9 of the same day. Built under DM's direction of 14 September: build the tests against fixtures with the address parameterised, and prove each test rejects a known-bad implementation before trusting it against a real page.

**Change at v10. Fallback to the fixture spec is now opt-in.**

v9 parameterised the live run but still fell back to `fixtures.SPEC` when a parameter was omitted, and printed what it used. Per DM: printing improves visibility, but **a consequential run should require explicit settings**. A live run now aborts with **exit 4** unless `PVR_LINEAGE`, `PVR_EXPECTED_CURRENT` and `PVR_ESTABLISHED` are set, or `PVR_ALLOW_FIXTURE_SPEC=1` authorises exploration — in which case the output says so in terms. The fixture defaults are not a description of any real record and the run now says that rather than implying it.

**Change at v9. Not a defect fix: a parameterisation flaw exposed by building the prototype.**

The live run used `fixtures.SPEC`, whose lineage, expected current version and establishment date are constants chosen for the fixtures. Pointed at the prototype, which publishes with a different establishment date, **check 9 failed on a configuration mismatch rather than on anything about the record** — a false negative, and the mirror of every false positive found this week. The fixtures keep their own spec; the live run now takes `PVR_ESTABLISHED`, `PVR_LINEAGE` and `PVR_EXPECTED_CURRENT`, defaulting to the fixture values. The live run also prints the spec it used, so a result cannot be read without seeing what it was measured against.

No check, fixture or credited result changed: 12/12, 14/14, 2/2.

**Change at v8. DM's bounded strengthening: the defensive guard protected membership and state, but not the accepted digest of each retained version.**

`_assert_no_baseline_loss` refused a write that dropped versions or reverted to `initialising`. It permitted a write that kept every version and **changed what one of them was being compared against**. DM demonstrated it by direct write. He was precise about its standing, and so is this: **a limitation of the guard, not a demonstrated bypass of the comparison sequence.** The normal path was protected anyway, because a changed digest makes check 8 fail and the run is not clean.

Renamed `_assert_baseline_not_weakened` and extended. An established baseline may **grow**; it may not shrink, revert, or have the accepted digest of a retained version rewritten, unless explicitly authorised. Covered by three refusals and one permission in `test_sequences.py`: narrowing refused, reverting refused, digest rewriting refused, growth with existing digests intact allowed.

## Scope of these results

DM, 14 September 2026, and it governs how every number below should be read:

> **These results support the tested behaviours, not a general claim that the suite proves §9 compliance.**

The suite tests a record against twelve stated acceptance requirements, and tests itself against known-bad states, stored-state shapes and observation sequences. It does not establish that a record satisfying it complies with §9. Four of the claims separated in `OPS_PublicVersionRecord_TechnicalSpecification_v4` — identity, existence by a time, completeness, availability and continuity — are only partly reachable by any test, and completeness before the first observation is not reachable at all.

**Changes at v7. The initialisation branch I added at v6 reintroduced baseline loss. DM reproduced it. The fix I wrote to close one reset opened another.**

**The defect.** `record_observation` popped `accepted` whenever an observation saw no entry digests — **even where an established baseline existed**. So a record serving an empty index reset the store to `initialising`, and the next observation, with altered archive bytes and a matching digest, became the new baseline. No corruption and no operator action required: an empty index was sufficient.

```
1 establish            accepted = v1, v1.1, v2, v3
2 unchanged            all 12 pass
3 EMPTY INDEX          v6: accepted = []   <- baseline destroyed
4 altered bytes return v6: accepted as the new baseline
5 repeated             v6: all 12 pass
```

**The rule applied:** an empty or failed observation preserves an existing accepted baseline. `initialising` is written **only where nothing has ever been accepted**. An empty index is a finding about the record, never a reason to forget what was accepted.

**And an invariant, because a fix caused this.** `_assert_no_baseline_loss` refuses any write that would drop accepted versions or revert an established store to `initialising`. Explicit operator acceptance (`PVR_ACCEPT_BASELINE=1`) is exempt, because that is a deliberate act. A silent regression is now a loud refusal.

**`test_sequences.py` added.** DM's point is the important one and is worth keeping: **the v6 defect was a state transition, not a state.** Every store the adapter wrote was well-formed and passed all fourteen shape tests. What was wrong happened between two of them, and only a sequence sees that. The new file runs whole observation histories against a controlled responder, with no network.

Verified both ways: the sequence passes against v7, and **fails against a reinstated v6 branch** with "BASELINE LOST at step 3: accepted=[]". A regression test that has not been shown to fail the defect it names is not evidence.

**Sequence tests: 2 of 2.**

**Changes at v6. DM found a reset loophole surviving v5's fix, and corrected a claim I made about one of my own tests.**

**The loophole.** v5 stopped invalid JSON, but three *valid-JSON* forms still read as "no baseline" and silently erased the comparison history: `{}`, `{"accepted": null}`, and an empty `accepted.versions` map. An altered archive then passed as a first observation.

**The rule now applied: only a genuinely absent file means first run.** An existing store must carry either a valid non-empty accepted baseline, or an explicitly declared initialisation state. The store is schema-tagged `pvr-baseline/1` with a required `state` of `initialising` or `established`, and every other shape raises.

```
store = {}                                              ABORTED  exit 3
store = {"schema":…,"state":"established","accepted":null}          ABORTED  exit 3
store = {"schema":…,"state":"established","accepted":{"versions":{}}} ABORTED  exit 3
store = {"schema":…,"state":"initialising"}             accepted: a declared, not inferred, first run
```

`initialising` is also what the adapter writes when a run observes no entry digests at all, because writing an empty accepted block would recreate the very shape that used to read as a reset.

**Testing precision, per DM.** v5's "interrupted write" test failed during *serialisation*, before any bytes were written, and I described it as though it covered interruption generally. It does not. There are now two tests: one for serialisation failure and one that fails **at the replacement step**, after the temp file is fully written. Neither demonstrates power loss, filesystem crash consistency, or `fsync` reaching the device. The test output states that limit rather than leaving it implied.

**Store tests: 14 of 14.**

**Changes at v5. DM reproduced two defects in v4's baseline persistence. Both were bare-except handlers of mine, both are fixed, and a new adapter-level test file covers them.**

| Defect | Why it passed | Fix |
|---|---|---|
| **A corrupted baseline file was silently treated as no baseline**, so an altered archive was accepted as a first observation and the next run passed all twelve checks | `_load_raw()` caught every exception and returned `{}`. Absent and unreadable were the same thing | **Absent and unreadable are now different.** Absent is a legitimate first run. Unreadable, empty, unparseable or wrongly shaped raises `BaselineError`, and the live run **aborts before any check is evaluated** with exit code 3. Deleting the store to re-establish a baseline is a deliberate act, and the message says what re-establishing accepts |
| **A failed baseline write was swallowed**: the adapter reported "baseline established" when no file was created | `_save_raw()` caught every exception and passed | The write raises on failure, and **reads back what it wrote** before reporting success. A write that succeeds silently and produces nothing readable is the case this guards |
| *(consequential)* An interrupted write could destroy the previous baseline | The store was written in place | The store is replaced **atomically**: temp file in the same directory, `flush` + `fsync`, then `os.replace`, which is a rename within one filesystem |

**Reproduced through the adapter, 14 September 2026:**

```
CASE 1  corrupt baseline file, with a CHANGED archive
        run A  ABORTED. baseline file is not valid JSON ...            <- was "first observation" in v4
        run B  ABORTED. baseline file is not valid JSON ...            <- was 12/12 PASS in v4
        exit code 3
CASE 2  baseline path whose parent directory does not exist
        baseline  NOT WRITTEN: cannot write baseline: directory does not exist
        file exists? no    exit code 3                                 <- was "baseline established" in v4
```

`test_baseline.py` covers the persistence layer directly, because no check-level fixture can reach it (**now 14 of 14**). Absent store is a legitimate first run; corrupt, empty and malformed stores raise; a failed write raises rather than reporting success; an interrupted write leaves the previous baseline intact and no temp files behind.

**Changes at v4. DM reproduced three false passes in v3 against controlled responses. All three were defects in this suite, all three are fixed, and all three are reproduced below through the live adapter.**

| Defect | Why it passed | Fix |
|---|---|---|
| **Alter an archive entry and its index digest together: fails once, then passes on every later run** | `fetch()` overwrote the stored digests on *every* call, including the call that had just detected the alteration. The detection became the new baseline | The accepted baseline is now separate from the observation log, and `fetch()` never writes it. The runner calls `record_observation(st, clean)` afterwards, and **only a clean preservation run advances the baseline**. Accepting a changed archive is a deliberate act: `PVR_ACCEPT_BASELINE=1` |
| **Remove a version from index and archive together, where it sits outside the configured lineage: all checks pass** | Check 3 tests membership against `spec.lineage`; check 8 compared digests only for versions still present. Neither could see a removal | **Check 12 added.** It compares the accepted inventory against current membership explicitly and depends on no configured expectation |
| **Set a publication date to `not-a-date`: all checks pass** | Dates were compared as strings, and `"not-a-date"` sorts lexically after any 2026 date | Dates are parsed with `date.fromisoformat`. Malformed values fail, and comparison is on dates. Check 9 is renamed **date consistency** and its docstring states that it does not establish historical truth |

**Reproduced through the live adapter, 14 September 2026**, against a served record:

```
CASE 1  alter archive entry and index digest together
        run 3  FAIL 8 no silent revision   baseline HELD: observation was not clean
        run 4  FAIL 8 no silent revision   baseline HELD: observation was not clean   <- was a pass in v3
CASE 2  remove v0 from index and archive, outside spec.lineage
        FAIL 12 membership retained  present at baseline, absent now: v0              <- was a pass in v3
        (check 12 is the only failure: nothing else sees it)
CASE 3  publication date = "not-a-date"
        FAIL 9 date consistency  not an ISO date: v2.published_to_record='not-a-date' <- was a pass in v3
```

**Why the baseline is gated on checks 8, 10, 11 and 12 only.** Those are the preservation checks. A content defect such as a malformed date does not alter archive bytes and should not freeze the archive baseline; an altered or missing entry should. Case 3 above shows the baseline correctly advancing while check 9 fails.

**Status: 12 of 12 acceptance controls, 14 of 14 store-shape tests, 2 of 2 sequence regressions. See *Scope of these results* above for what that does and does not support.**

**Changes at v3.** Two checks added and one defect fixed, both arising from DM's separation of preservation claims on 14 September.

- **Checks 10 and 11 added.** Nothing previously fetched the archive entries. The index listing a version said the record *claimed* to hold it; only fetching says it is still there and still serves the recorded bytes. Demonstrated live: with the v2 archive entry deleted and the index untouched, **checks 1 to 9 all passed** and only check 10 caught it.
- **Vacuous-pass defect fixed.** Checks 4, 5, 6 and 9 passed on a record listing no versions at all, because `all()` over an empty list is True. Found by running the live adapter against a dead server. Every content check now carries the empty-record fixture.

Live run skipped by default: no address exists and no instrument designates one.

## What a credited check means

A check is credited only where it **passes the golden record and fails every matched known-bad state**. Passing a live endpoint is recorded and is never evidence on its own. This is the rule the QA regression suite established on 13 September, applied to a different control.

## Results

| # | Requirement | Golden | Known-bad states, all correctly rejected | Credited |
|---|---|---|---|---|
| 1 | Resolves at the required address | PASS | dead URL (404, generic host body) | ✔ |
| 2 | Identifies the current version | PASS | no version marked current; wrong version marked current | ✔ |
| 3 | Exposes prior versions and dates | PASS | current version only | ✔ |
| 4 | States the reason for each amendment | PASS | missing amendment reason | ✔ |
| 5 | Preserves whole-integer / minor-decimal semantics | PASS | flat list, revision class not declared | ✔ |
| 6 | Makes supersession explicit | PASS | version present but silently unmarked | ✔ |
| 7 | Independently retrievable, no authentication | PASS | authentication required | ✔ |
| 8 | Retains earlier states, no silent revision | PASS | overwritten with no prior version retained; history present but bytes replaceable; history present but changes undated | ✔ |
| 9 | **Date consistency** (addition) | PASS | missing publication date; backfilled to July; publication date not an ISO date; instrument date not ISO; published before the instrument is dated | ✔ |
| 10 | Every archive entry resolves (**availability**) | PASS | archive entry gone with index unchanged; entries never fetched | ✔ |
| 11 | Retrieved bytes match recorded digest (**identity**) | PASS | entry resolves but serves other bytes; entries never fetched | ✔ |
| 12 | Baseline membership retained (**completeness, between observations**) | PASS | no accepted baseline; version removed while outside the configured lineage | ✔ |

Checks 3 to 6 and 9 to 11 additionally reject an **empty record**.

**Checks 10 and 11 are separated deliberately.** An entry that has gone and an entry that serves different bytes are different failures; one result that could mean either cannot say which. Check 11 is therefore *not* given the gone-entry fixture.

**What check 12 covers, and what it does not.** It detects a version removed **between two observations you made yourself**, which needs only a retained inventory: chaining and external witnessing add assurance but are not prerequisites for this check. It cannot detect an entry removed **before the first observation**, and no test can. That gap is a record-design question — see `OPS_PublicVersionRecord_TechnicalSpecification_v3`.

**Check 9 establishes date consistency, not historical truth.** Well-formed dates and an earliest permitted date do not make a stated date true. A record can pass every limb of check 9 and state dates that never happened.

**Check 9 is an addition to DM's eight**, derived from his instruction not to backfill publication dates. It is marked as an addition and is not treated as ratified.

## Adapter proved end to end, not only the checks

A check can be correct while the adapter that feeds it is not. The live adapter was therefore run against a local endpoint serving a deliberately defective record:

- **Backfilled July dates caught on a live target.** The served record claimed v2 and v3 were published to the record on 29 July 2026. Check 9 failed it: "before the record existed". That is the exact trap DM named, caught through the HTTP path rather than through a fixture.
- **Silent replacement caught by observation.** Run 1 wrote a digest snapshot and reported requirement 8's mutability limb as asserted, not observed. Run 2 against the unchanged record observed immutability and passed. Run 3, after a prior entry's bytes were silently replaced, failed: "prior entries can be replaced in place".

So requirement 8 is tested behaviourally over time, not by reading what the record says about itself.

## Machine-readable representation: RATIFIED

DM ratified this on 14 September 2026, and restated it functionally rather than as a format:

> **The public version record must expose a deterministic machine-readable representation sufficient to test version identity, publication date, amendment reason, supersession and integrity of prior entries.**

Structured HTML satisfies that as readily as JSON. The point is that **a human-readable page alone is not a control.** The checks operate on a parsed model, so a change of representation touches `live.py` and nothing else.

## One design decision, surfaced rather than smuggled in

**DM's requirement 8 listed "prior versions accessible but no amendment reason" as a failure of requirement 8. It is tested here under check 4.** The reason is a content requirement; mutability is a storage requirement, and mixing them means a single failure cannot say which property is broken. The state still fails the suite; it fails at 4 rather than at 8.

## The honest limit on requirement 8

Whether prior entries can be silently replaced is a property of the record **over time** and cannot be established by one fetch. The adapter distinguishes two limbs:

- **Assertion:** entries are version-addressed, carry digests, and the digests are externally anchored. Read from the record.
- **Observation:** the digests seen now match a stored snapshot from an earlier run.

With no prior snapshot the mutability limb is reported as **not yet observed** and check 8 does not pass. A record cannot prove it has never been silently revised on the day it is created. It earns that over time. That is the correct result and not a defect in the test.

## The address is a parameter

```
PUBLIC_VERSION_RECORD_URL=<candidate>   # required for the live run
PVR_CONTROL_URL=<any other path on the same host>   # for the generic-response test
PVR_INDEX_SUFFIX=/index.json            # default
PVR_SNAPSHOT=pvr_snapshot.json          # accepted baseline + observation log
PVR_ACCEPT_BASELINE=1                   # deliberately accept a changed archive
```

No path is hard-coded anywhere in the suite. Per DM, the address must not acquire constitutional significance unless an instrument already specifies one.

**Set `PVR_CONTROL_URL` whenever a live run matters.** Requirement 1's known-bad is not a bare 404; it is a response byte-identical to a control fetched from the same host at the same time, which is how a wildcard response masquerades as a page. The control is fetched alongside the record rather than compared against a stored constant, because an error body and its ETag can change with a platform or site change without notice. Without a control that limb does not run, and the live output says so.

## Running it

```
python3 run_acceptance.py                                  # fixtures only
PUBLIC_VERSION_RECORD_URL=https://…  python3 run_acceptance.py   # fixtures then live
```

Exit 0 all credited and live clean or skipped; 1 live failures; 2 a check lost its credit; **3 the baseline store is unusable or could not be written**.

```
python3 test_baseline.py     # the persistence layer: store shapes, no network
python3 test_sequences.py    # whole observation histories, no network
```

## Files

| file | what it is |
|---|---|
| `model.py` | `RecordState` and `VersionEntry`: what a probe returns, fixture or live |
| `checks.py` | the twelve checks and the `Spec` that parameterises lineage and dates |
| `fixtures.py` | the golden record and the known-bad states, one mutation each |
| `live.py` | HTTP adapter, index parser, per-entry fetch and digest, accepted-baseline comparison and observation log |
| `run_acceptance.py` | runner; credits a check only on golden-pass plus known-bad-fail |
| `test_baseline.py` | the baseline store: absent vs unreadable vs initialising, reset loopholes, write failure, atomic replace |
| `test_sequences.py` | whole observation histories, which is the only thing that catches a bad state transition |

## STANDING RULES

**1. These fixtures are mandatory regression tests for any later change to the record's acceptance criteria.** A revised requirement set is not credited until it passes the golden record and rejects every state above. A check that loses its known-bad fixture loses its credit, and the runner exits 2 to say so.

The reason is on the record already: the superseded lock check in the QA suite failed intact and altered formulations alike for want of a fixture pair, and nobody knew until the pair was built.

**2. Declared control is not observed control performance.** DM's ruling of 14 September 2026, to be preserved permanently and not only for requirement 8.

A record that declares itself immutable has made an assertion. A record whose prior entries are observed unchanged across time has demonstrated a property. The two are different evidence classes and a control must never credit the first as the second. Requirement 8 implements this by refusing to pass on a first observation, however complete the record's own declaration.

This is the same failure the estate has now met three times in different clothing: the Charter's compliance with §9 evidenced only by the Charter saying it complied; a cover page asserting canonical status; a page asserting immutability. **Where an artefact is the only witness to its own conformance, there is no evidence.** When gate v18 is revisited, this belongs in it alongside requirement 5.
