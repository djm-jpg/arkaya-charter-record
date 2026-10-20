# Test fixtures

Everything under this directory is a **TEST INPUT** or test-only code. Nothing
here is a real record, and nothing here is registered in `records.py`.

`disclosures/TEST-INPUT-disclosure-v1.md` and `-v2.md` are synthetic disclosure
carriers. `test_namespaces.py` copies them into a private sandbox, registers
their digests in the sandbox's own copy of `records.py` (the same single block
an operator completes at freeze), and builds, packages, verifies and records a
multi-namespace release there. Each carries the `ARKAYA-TEST-INPUT` marker, so
the builder refuses it unless `PVR_ALLOW_TEST_INPUT=1` is set, and a release
built from it is never granted production approval by `verify_live.py`.

`get/TEST-INPUT-get-schema-issue1.json` and `-issue2.json` are synthetic GET
schema files, registered the same way in the sandbox's GET REGISTRATION block.
Issue 1 deliberately carries a UTF-8 byte-order mark, CRLF line endings, a
non-ASCII character and no final newline, so that any change to its bytes on
the way to being served is detected. Both carry the `ARKAYA-TEST-INPUT` marker.

The real disclosure carrier and the real GET schema are not inputs to this
repository until each is registered at freeze.

`baseline-b4e36d3/build_release.py` and `records.py` are byte-for-byte copies of
those two files at commit `b4e36d3`, the builder and registry that built the
published `publish-003` release (their SHA-256, `d973186c…` and `78133311…`,
are the `release_builder` and `registry_sha256` recorded in
`releases/publish-003.json`; the test checks both). They are not inputs and are
never run outside a test sandbox. `TestGetAbsentRegression` in
`test_namespaces.py` builds the same disclosure-only release with them and with
the current builder (GET_REGISTRATION = ABSENT) under one frozen clock, and
requires the two release trees to be byte-identical apart from the builder and
registry digests the disclosure manifest records.
