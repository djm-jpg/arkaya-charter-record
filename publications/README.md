# Published index snapshots

One directory per publication sequence, written by `record_publication.py`:

    <sequence>/index.json              the index exactly as it was made current
    <sequence>/manifest.json           the manifest it was published with
    <sequence>/manifest.json.sha256
    <sequence>/release.json            the freeze marker for that release
    <sequence>/live_verification.json  the evidence publication was recorded from
    <sequence>/publication.json        deploy ID, permalink, commit, tag, digests

**A ledger of hashes is not a retained record.** `published_indexes.json` records
what each index hashed to; without the index files themselves, a later holder of
the hash has nothing to compare against. These directories are the retained
record. They are immutable: `record_publication.py` refuses to write over one.

Empty until a publication is recorded.
