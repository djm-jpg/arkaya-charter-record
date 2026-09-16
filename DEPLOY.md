# Deployment steps

> **The executable sequence is `OPS_Charter_LiveSequence_Runbook`, not this document.** That
> runbook supersedes the step lettering below and is what is followed at deployment. This
> document remains the design rationale: why the order is what it is, and what each control is
> for. Where the two differ, the runbook governs.
>
> Material differences introduced by the runbook, all of them corrections to this document:
> the deployment is taken from a fresh clone checked out at `release-001` and verified against
> the bound commit and manifest, not from the working copy; `releases/publish.json` is included
> in the evidence commit; a fresh-clone check is run at `publication-001` as well as at
> `release-001`; the baseline and the next-day comparison are committed and tagged as
> `evidence-002` and `evidence-003`, because neither is captured by the publication evidence
> that precedes them; a replacement release takes new identifiers rather than reusing
> `release-001`; every command failure or identity mismatch is a stop by standing rule, with
> named exceptions for the steps whose non-zero result is expected or handled; the
> publication-evidence tag is recorded after it exists, so the production record names it; and
> the closing boundary is stated, since the last artefact in a chain cannot certify itself.

Rewritten at v6. The v5 sequence could not be executed as written: D1 required the commit
created at E4, and E3 asked for a fresh-clone check before E4 created the commit to clone.
A sequence with a cycle in it is not a procedure.

**The order now, and why it is this order.** The repository commit comes FIRST, because a
commit is the cheapest way to give the frozen release a durable identifier before anything
depends on it. Deploy that exact output. Verify it live. Record publication against that
commit and that deployment. Then commit the resulting evidence separately. Each tag names
which commit it identifies, because they identify different things.

    A  build and freeze the release            Claude
    B  commit the frozen release, tag, bind    DM + Claude   <- release-001 identifies this commit
    C  deploy that output to Netlify           DM
    D  verify the live venue                   Claude
    E  record publication                      Claude
    F  commit the evidence, tag it             DM        <- publication-001 identifies this commit
    G  archival                                DM
    H  close out, and schedule the follow-up   Claude

**Nothing here has been done.** No project, repository, DNS record or archive request
exists. This is the sequence, not a report.

---

## A. Build and freeze the release — Claude, on the day of deployment

**A1.** On the day the set will actually be deployed, from a clean extraction:

```
python3 build_publication_set.py
```

> **The package ships a frozen release already.** If its release date is not the day you are
> deploying, this step refuses, and that is the control working: the set carries its date on
> its face. Discard the shipped release deliberately and build today's:
> `PVR_REPLACE_RELEASE=1 python3 build_publication_set.py`. A release RECORDED AS PUBLISHED
> cannot be replaced at all, by this or any flag. If the shipped release is already dated
> today, skip to A2 — the release is packaged as built, not rebuilt for the sake of it.

The release date defaults to today and any other date is refused unless
`PVR_ALLOW_DATE_MISMATCH=1` **and** `PVR_DATE_MISMATCH_REASON` are both set; the reason is
recorded in the release metadata, the manifest and the production record.

**A2.** Verify the frozen release. This rebuilds nothing:

```
python3 verification/run_verification.py
```

Ten acceptance runs against a served copy, each with a declared expected outcome, plus a
reproducibility comparison built into a separate directory. Evidence lands in
`verification/runs/<timestamp>/`. Nothing existing is deleted.

**A3.** Package it. This rebuilds nothing either:

```
python3 package.py
```

It checks the release against its freeze marker; hashes the builder, the inputs, the README
source and every vendored suite file against their recorded identities; requires a
verification run against **this** manifest and re-derives every outcome from the retained
transcripts; recomputes the rebuild verdict from the retained trees; regenerates the
production record and compares it byte for byte; then runs the three test suites.

**A4.** Record the manifest digest from `publish/charter/manifest.json.sha256` and the
package digest. Everything downstream is checked against them.

---

## B. Commit the frozen release — DM

The repository is a **subordinate provenance and verification layer**. It is not the
canonical venue and does not decide what the record says. It is committed first so the
release has an identifier before anything cites one.

**B1.** Create a public repository named `arkaya-charter-record`.

**B2.** Copy in **the extracted package, unchanged**, keeping its layout:

```
build_publication_set.py    record_publication.py    package.py
expectations.py             verify_live.py           test_build.py
test_verify_live.py         test_package.py          README_source.md
DEPLOY.md                   PUBLICATION_LOG.md
first_publication.json      published_indexes.json
inputs/charter-v1.pdf  inputs/charter-v1.1.pdf  inputs/charter-v2.pdf  inputs/charter-v3.pdf
vendor/acceptance_suite/    verification/            publications/
releases/publish.json       publish/
```

> The v4 instruction moved the scripts into `tools/` and the sources into `sources/` without
> adapting their path assumptions, and omitted the input PDFs entirely. The manifest names
> `inputs/charter-vN.pdf` and the builder resolves them relative to itself, so a relocated
> clone does not run. The repository mirrors the package exactly, and the manifest's
> `builder.source_path` is `build_publication_set.py` accordingly.

**B3.** Commit on `main` with the message `Charter publication set, release <date>`.
**Record this commit SHA.** This is the **frozen-release commit**: it identifies the bytes
that are about to be deployed.

**B4.** Protect `main` in Settings → Rules (or Branches, depending on the mechanism offered):

- **"Allow force pushes" left disabled.**
- **"Allow deletions" left disabled.**
- **Administrator coverage enforced** — the control must apply to administrators. In branch
  protection this is "Do not allow bypassing the above settings"; in a ruleset it is leaving
  the bypass list empty. A protection an administrator can step around protects against
  accident, not against a disputed change.

**B5.** Protect the publication tags **separately from the branch**. A branch rule does not
govern tags, so `main` being protected says nothing about whether a tag can be moved or
deleted. Create a ruleset targeting tags matching `release-*` and `publication-*`, with
deletion and force-push blocked and administrator coverage enforced.

> *Moderate confidence on the interface, high on the requirement.* GitHub has been moving tag
> protection from the standalone "Tag protection rules" page into rulesets, and the labels
> differ between the two. Record which mechanism was used and what it was set to, rather than
> assuming the wording above matches what you see.

**B6.** Tag the frozen-release commit `release-001`. Sign it if a signing key is configured;
if not, record that it is unsigned rather than leaving it ambiguous.

**B7.** Bind the frozen release to that commit and tag — Claude:

```
python3 record_publication.py --bind --commit <commit from B3> --tag release-001
```

> **Why this step exists.** Until it was added, the commit passed at recording time was free
> text: written into the snapshot, checked against nothing. Approval evidence for one frozen
> release could in principle have been recorded against another. Recording now refuses unless
> the commit and tag it is given are exactly the ones bound here, to this manifest digest.
>
> **What it does not establish.** It binds an identifier supplied by the operator. It cannot
> verify that the commit exists in any repository, or that the repository holds these bytes.
> Step B8 is what tests the other half. A release is bound once: if the commit was wrong,
> rebuild the release and bind the new one.

**B8.** Clone the repository fresh, at `release-001`, and confirm it runs:

```
python3 package.py --check
```

Exit 0 is required before deploying. This is the check the v5 sequence asked for before the
commit existed, and it is the half of the binding that `--bind` cannot supply: it shows the
repository at that tag really does hold a package that reconciles.

**B9.** Confirm the rulesets show as active on `main`, `release-*` and `publication-*`, and
record the ruleset JSON or a screenshot. Attempt nothing destructive to test it.

---

## C. Deploy — DM

**C1.** Open the Netlify team's projects page and choose "Add new project".

**C2.** Choose "Deploy manually".

**C3.** Name the project `arkaya-record`. This is a **separate project** from the main Arkaya
site: the record's availability must not depend on unrelated site deployments.

**C4.** Drag the **`publish`** folder onto the deploy area — not `charter`, and not the
working directory.

> `publish/` contains `charter/` and a pointer page, and nothing else. The builder, the
> inputs, the vendored suite, the ledgers, the freeze markers and the verification evidence
> all sit outside it. The freeze marker in particular lives in `releases/`, not in the deploy
> root, because anything inside the deploy root is served.

**C5.** Record the **deploy ID** and the **deploy permalink**
(`https://<deploy-id>--arkaya-record.netlify.app`). The permalink is the immutable reference
to this exact deployment and is what makes a later "the record changed" claim checkable.

**C6.** Open "Domain management" and add the custom domain `record.arkayarisk.com`.

**C7.** Copy the DNS target Netlify shows.

**C8.** At your DNS provider, create a CNAME for `record` pointing to that target.

**C9.** Wait for Netlify to report the certificate as issued. Do not proceed while the domain
shows as awaiting DNS or awaiting certificate.

---

## D. Verify the live venue — Claude, before anything is recorded or archived

**D1.** Run the live verifier against the canonical address:

```
python3 verify_live.py https://record.arkayarisk.com/charter/
```

It checks, against the **frozen** manifest: HTTPS; that plain HTTP redirects to the same
HTTPS address, not merely to some HTTPS address; HSTS; that the body served at `/charter/` is
the page that was built, not merely a 200; that the **served** `manifest.json` hashes to the
frozen manifest; that the served sidecar agrees with the **served** manifest and with the
frozen one; every canonical path, SHA-256, byte count and content type; a control path that
must 404; that the deploy root serves the pointer and not a listing; and that no internal
file is reachable from either level.

**D2.** Read the **PRODUCTION APPROVAL** line, not just the pass count. Approval is withheld
unless the run was over HTTPS, against the canonical address, against a frozen release that
still matches its marker, with every check passing. Only an approved run can record
publication.

**D3.** If anything failed, stop. Fix the deployment and repeat D1. Do not record and do not
archive: archival would capture a record that does not match its manifest.

**D4.** Retain the verification file written to `verification/live/`.

---

## E. Record the publication — Claude, only on an approved verification

**E1.** With the approved evidence from D1, the deploy identifiers from C5 and the
frozen-release commit from B3:

```
python3 record_publication.py \
  --evidence verification/live/live_verification_<stamp>.json \
  --deploy-id <deploy id> \
  --deploy-permalink <permalink> \
  --commit <the commit bound at B7> \
  --tag release-001
```

It refuses unless the commit and tag match the binding made at B7 against this manifest
digest, so approval evidence cannot be attached to a different frozen release. It validates
**every object in the release** against the manifest, the sidecar, the index
digest and the pointer page immediately before recording — not merely the manifest file's own
hash — and refuses a rehearsal, a failed or unapproved verification, evidence from another
address, evidence against a different manifest, a venue that served a different manifest, and
an observation on a date other than the one the set carries.

**E2.** It writes `first_publication.json`, `published_indexes.json` and the immutable
snapshot `publications/1/`, which holds the index, the manifest, its sidecar, the freeze
marker, the live evidence and the deployment identifiers. **A ledger of hashes is not a
retained record**; the snapshot is.

> **If E1 is interrupted**, the recording is staged and moved into place atomically, so the
> state is either absent, incomplete or complete — never ambiguous. An incomplete recording
> refuses a plain retry and says so; re-run the same command with `--resume` to complete it.
> An incomplete recording is not a published sequence and nothing is lost.

**E3.** Re-run `python3 package.py` so the archive carries the ledgers and the snapshot. This
still rebuilds nothing, and the release is unchanged.

---

## F. Commit the evidence — DM

**F1.** Copy the updated `first_publication.json`, `published_indexes.json`,
`publications/1/`, `verification/live/` and `verification/PRODUCTION_RECORD.md` into the
repository.

**F2.** Commit on `main` with the message `Publication of sequence 1, <release date>`.
**Record this commit SHA.** This is the **publication-evidence commit**.

**F3.** Tag it `publication-001`.

> **Which commit each tag identifies, and what each one is.**
>
> `release-001` identifies the frozen release: the bytes that were deployed.
>
> **`publication-001` is not the published object.** It is the evidence record *that*
> publication occurred — the ledgers, the snapshot and the live verification — and it
> necessarily post-dates the deployment it records. A future reader finding this tag should
> not take it for the released set, and should not cite it as the record itself.
>
> Do not move either tag to the other commit.

**F4.** Sign the tag if a signing key is configured; otherwise record that it is unsigned.

---

## G. Archival — DM, only after section D passed

**G1.** At the Internet Archive's Save Page Now, submit
`https://record.arkayarisk.com/charter/`.

**G2.** Submit each canonical object URL as well. A snapshot of the index alone does not
preserve the PDFs it lists:

```
https://record.arkayarisk.com/charter/index.json
https://record.arkayarisk.com/charter/index.html
https://record.arkayarisk.com/charter/manifest.json
https://record.arkayarisk.com/charter/manifest.json.sha256
https://record.arkayarisk.com/charter/README.md
https://record.arkayarisk.com/charter/v1/charter-v1.pdf
https://record.arkayarisk.com/charter/v1.1/charter-v1.1.pdf
https://record.arkayarisk.com/charter/v2/charter-v2.pdf
https://record.arkayarisk.com/charter/v3/charter-v3.pdf
```

**G3.** Record each archived URL with its capture timestamp.

**G4.** At Software Heritage's save page, submit the repository URL.

**G5.** Record the **request status**.

**G6.** Return later and record the **completed snapshot or revision identifier** (the SWHID).
A submitted request is not preservation: it is a request. Until an identifier exists,
Software Heritage has archived nothing, and the publication log must say so.

**G7.** If the request has not completed, record it as outstanding with the date it was made
and set a date to check again. Do not describe the repository as archived.

---

## H. Close out, and the follow-up — Claude

**H1.** Establish the live baseline and retain its store:

```
PVR_LINEAGE=v1,v1.1,v2,v3 PVR_EXPECTED_CURRENT=v3 PVR_ESTABLISHED=<release date> \
PUBLIC_VERSION_RECORD_URL=https://record.arkayarisk.com/charter/ \
PVR_CONTROL_URL=https://record.arkayarisk.com/charter/definitely-not-here \
PVR_SNAPSHOT=verification/live/pvr_snapshot_live.json \
python3 vendor/acceptance_suite/run_acceptance.py
```

> This first live run establishes the baseline and therefore **accepts the record as it
> stands**. It is not evidence of preservation. Preservation is demonstrated by later runs
> comparing against this baseline, and only from the second run onward.

**H2.** Complete `PUBLICATION_LOG.md` with every identifier recorded above.

**H3.** File the completed log, the frozen package and the verification evidence to
`00-Group/99-Working/`.

**H4.** **Schedule the next-day comparison as a follow-up**, not as a prerequisite to
anything above. Re-run H1 the following day; that second run is the first observation capable
of detecting a silent change. Its result is recorded in the publication log when it happens,
and nothing in sections A to G waits for it.

**H5.** Report what is established and what is not. On the evidence this sequence produces,
what is established is: the set was served at the canonical address on the recorded date;
what was served matched the frozen manifest object by object, including the manifest itself
and the landing page; and a baseline exists from which later change can be detected. What is
**not** established, and must not be implied: that the v1.1, v2 and v3 amendments were validly
effective from their stated July dates, or that any version was published anywhere before the
recorded date.

---

## Held

Gate v18, the schema release, the historical-validity assertion and the authority
classification of the six exposed artefacts are unaffected by this deployment and remain held.
Publication does not cure any of them, and the record says so on its face.
