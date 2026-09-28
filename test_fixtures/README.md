# Test fixtures

Everything under this directory is a **TEST INPUT**. Nothing here is a real
record, and nothing here is registered in `records.py`.

`disclosures/TEST-INPUT-disclosure-v1.md` and `-v2.md` are synthetic disclosure
carriers. `test_namespaces.py` copies them into a private sandbox, registers
their digests in the sandbox's own copy of `records.py` (the same single block
an operator completes at freeze), and builds, packages, verifies and records a
multi-namespace release there. Each carries the `ARKAYA-TEST-INPUT` marker, so
the builder refuses it unless `PVR_ALLOW_TEST_INPUT=1` is set, and a release
built from it is never granted production approval by `verify_live.py`.

The real disclosure carrier is not an input to this repository until it is
registered at freeze.
