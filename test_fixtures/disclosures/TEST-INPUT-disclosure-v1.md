<!-- ARKAYA-TEST-INPUT -->
# TEST INPUT: synthetic governance disclosure, version 1

**This is a synthetic test fixture. It is not a disclosure, it describes no real
control, and it must never be registered in the shipped `records.py` or
published.** It exists so that the multi-namespace tests can build, package,
verify and record a disclosure namespace without any real input.

The builder refuses any input carrying the marker on the first line unless the
run sets `PVR_ALLOW_TEST_INPUT=1`, and a release built from it is marked as a
test-input release and is never granted production approval.

## Fixture body

1. Statement one of the synthetic disclosure.
2. Statement two of the synthetic disclosure.
