# Arkaya Schema Independence Charter: provenance and verification source

Maintained by **Arkaya Risk**.

## This is not the canonical publication venue

The canonical publication venue for the Schema Independence Charter is:

> **https://record.arkayarisk.com/charter/**

This repository is the **provenance and independent verification layer** that sits behind it.
It is deliberately secondary. The hierarchy is:

| Layer | Where |
|---|---|
| **Canonical publication** | `record.arkayarisk.com/charter/` |
| **Provenance and verification** | this repository |
| **Independent preservation** | third-party archival capture |

Arkaya maintains this repository openly and under its own name, so that a counterparty can see
the verification source is intentionally kept rather than incidental. That is the reason for the
branding. It is not an invitation to treat the repository as the publication.

**The canonical object is the version served at `record.arkayarisk.com`.**

## Where the repository and the canonical venue differ

> Where the repository and canonical venue differ, the discrepancy is an integrity finding
> requiring investigation. The canonical venue identifies Arkaya's asserted publication state;
> the discrepancy must not be resolved by silently overwriting either record.

A difference is a finding, not a tie to be broken. Neither copy is corrected into agreement with
the other until the discrepancy has been investigated and the investigation recorded.

## Historical states

Superseded repository states remain useful evidence after supersession and are not removed. A
version ceasing to be current does not make the record of it less evidential.

**No repository state establishes the retrospective validity of any amendment.** What a repository
state evidences is what was published, and when it was published here.

## What is published

| File | What it is |
|---|---|
| `index.json` | Machine-readable publication index |
| `index.html` | Human-readable page, generated from `index.json` |
| `manifest.json` | Integrity manifest: path, canonical URI, media type, byte length, SHA-256 |
| `manifest.json.sha256` | Digest of the manifest |
| `vN/charter-vN.pdf` | The instrument as filed, byte-for-byte unchanged |

The lineage is **v1, v1.1, v2 and v3**.

The PDFs are copied from the filed documents and are never regenerated. Regenerating a PDF would
produce different bytes and a different digest for the same document, breaking the link to what
was actually filed.

## How the set was built, and what that shows

The manifest records the builder, its digest, its source path in this repository, the exact
inputs with their digests, and the build parameters including the runtime version. The builder
itself is at `tools/build_publication_set.py`, with its tests beside it, and the verification
evidence is under `verification/`.

**Matching digests identify the supplied builder and show that the shipped objects stand in the
expected relationship to the recorded inputs. They do not independently prove that this builder
historically executed.** That is what the retained build and verification evidence is for, and it
is a weaker claim than a digest match can look like on its own.

## What `superseded_from` is, and is not

`superseded_from` is **documentary chronology**: the instrument date of the succeeding issue. It
records how the documents are dated and ordered. It is not an assertion that supersession took
legal effect on that date, and nothing in this record establishes that it did. Every field in
the index is defined in the index itself, under `definitions`.

## Verifying a version

1. Retrieve the PDF from the canonical venue.
2. Compute its SHA-256.
3. Compare against the digest for that version in `index.json` and `manifest.json`.
4. Compare the canonical venue's copy against this repository's copy.

```
shasum -a 256 v3/charter-v3.pdf
```

Step 4 producing a difference is an integrity finding. Report it rather than choosing a copy.

## Two dates, and they are not the same

**Instrument date** is the date on the document's own cover.
**Published to this record** is the date it was first published to the canonical venue.

Four versions dated May and July 2026 were first published to this record in September 2026. The
record says so on every entry. No earlier publication date is asserted for any version.

## What `as_of` means

`as_of` states the position asserted by that publication at that moment. It does not warrant the
absence of subsequent events that have not yet been published to this record.

## What this publication does not assert

Publication records the documentary state and the publication metadata. **It does not validate,
cure or establish the historical effectiveness of any amendment to this instrument.**

## Retention

Each published Charter issue, publication index and associated integrity record is retained
permanently as part of Arkaya's governance record. Publication expressly permits recipients to
retain independent copies for evidential and verification purposes.

**Clone this repository if you need an independent copy.** A retained copy lets you detect later
alteration against what you hold. It does not establish that what you captured was complete at the
moment of capture.

## Integrity properties, stated accurately

Version control makes ordinary changes highly visible and gives independently cloned or archived
copies a means of detecting later history alteration. **It does not make rewriting impossible.**
The publication branch is protected against force-push and deletion, and publication commits or
tags are signed where practicable.

No later publication replaces an earlier object's bytes.
