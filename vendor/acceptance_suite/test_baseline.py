"""Adapter-level tests for the baseline store.

Check-level fixtures cannot reach these: the defects are in persistence, not in
any check. Both were found by DM on 14 September 2026 against the v4 adapter.
"""
import json, os, sys, tempfile
import live

def case(name, fn):
    ok, detail = fn()
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    return ok

def _with(path):
    live.SNAPSHOT = path

def t_absent_is_not_an_error():
    d = tempfile.mkdtemp(); _with(os.path.join(d, "none.json"))
    try:
        return (live._load_raw() == {} and live._load_baseline() is None), "absent reads as no baseline"
    except Exception as e:
        return False, f"raised {e!r}"

def t_corrupt_raises():
    d = tempfile.mkdtemp(); p = os.path.join(d, "b.json"); open(p, "w").write("{not json")
    _with(p)
    try:
        live._load_raw(); return False, "corrupt file read without error"
    except live.BaselineError:
        return True, "corrupt file raises rather than resetting"

def t_empty_raises():
    d = tempfile.mkdtemp(); p = os.path.join(d, "b.json"); open(p, "w").write("   ")
    _with(p)
    try:
        live._load_raw(); return False, "empty file read without error"
    except live.BaselineError:
        return True, ""

def _store(d, **kw):
    p = os.path.join(d, "b.json")
    json.dump(kw, open(p, "w")); _with(p)
    return p

def _must_raise(d, label, **kw):
    _store(d, **kw)
    try:
        live._load_raw(); return False, f"{label} read without error"
    except live.BaselineError:
        return True, ""

def t_malformed_accepted_raises():
    d = tempfile.mkdtemp()
    return _must_raise(d, "malformed accepted block", schema=live.SCHEMA,
                       state=live.STATE_ESTABLISHED,
                       accepted={"versions": "not-a-dict"})

# --- the reset loophole DM found in v5 --------------------------------------
def t_empty_object_raises():
    return _must_raise(tempfile.mkdtemp(), "{}")

def t_null_accepted_raises():
    return _must_raise(tempfile.mkdtemp(), "null accepted", schema=live.SCHEMA,
                       state=live.STATE_ESTABLISHED, accepted=None)

def t_empty_versions_raises():
    return _must_raise(tempfile.mkdtemp(), "empty versions map", schema=live.SCHEMA,
                       state=live.STATE_ESTABLISHED, accepted={"versions": {}})

def t_missing_accepted_raises():
    return _must_raise(tempfile.mkdtemp(), "established with no accepted block",
                       schema=live.SCHEMA, state=live.STATE_ESTABLISHED)

def t_unknown_schema_raises():
    return _must_raise(tempfile.mkdtemp(), "unrecognised schema",
                       schema="something/else", state=live.STATE_ESTABLISHED,
                       accepted={"versions": {"v1": "x"}})

def t_explicit_initialising_is_not_an_error():
    d = tempfile.mkdtemp()
    _store(d, schema=live.SCHEMA, state=live.STATE_INITIALISING)
    try:
        live._load_raw()
        return live._load_baseline() is None, "declared initialising reads as no baseline"
    except live.BaselineError as e:
        return False, f"raised {e!r}"

def t_initialising_with_accepted_raises():
    return _must_raise(tempfile.mkdtemp(), "initialising carrying an accepted block",
                       schema=live.SCHEMA, state=live.STATE_INITIALISING,
                       accepted={"versions": {"v1": "x"}})

def t_unwritable_raises():
    _with(os.path.join(tempfile.mkdtemp(), "no", "such", "dir", "b.json"))
    try:
        live._save_raw({"accepted": {"versions": {"v1": "x"}}})
        return False, "reported success with no file created"
    except live.BaselineError:
        return True, "failed write raises rather than being swallowed"

def _good():
    return {"schema": live.SCHEMA, "state": live.STATE_ESTABLISHED,
            "accepted": {"versions": {"v1": "sha256:aaa"}, "at": "t0"}}

def t_serialise_failure_preserves_previous():
    """Fails BEFORE any bytes are written. Weaker than it looks, and labelled."""
    d = tempfile.mkdtemp(); p = os.path.join(d, "b.json"); _with(p)
    live._save_raw(_good())
    class Boom:
        def __repr__(self): raise RuntimeError("interrupted mid-serialise")
    try:
        live._save_raw({"schema": live.SCHEMA, "state": live.STATE_ESTABLISHED,
                        "accepted": {"versions": {"v1": Boom()}}})
    except Exception:
        pass
    leftovers = [f for f in os.listdir(d) if f.startswith(".pvr_baseline.")]
    return (json.load(open(p)) == _good() and not leftovers), f"{len(leftovers)} temp files left"

def t_replace_failure_preserves_previous():
    """Fails AT the replacement step, after the temp file is fully written.
    This is the case DM exercised; the serialise-failure test above does not
    reach it."""
    d = tempfile.mkdtemp(); p = os.path.join(d, "b.json"); _with(p)
    live._save_raw(_good())
    real = os.replace
    os.replace = lambda *a, **k: (_ for _ in ()).throw(OSError("replace interrupted"))
    try:
        live._save_raw({"schema": live.SCHEMA, "state": live.STATE_ESTABLISHED,
                        "accepted": {"versions": {"v1": "sha256:NEW"}, "at": "t1"}})
        ok, detail = False, "reported success despite replace failing"
    except live.BaselineError:
        ok, detail = True, ""
    finally:
        os.replace = real
    leftovers = [f for f in os.listdir(d) if f.startswith(".pvr_baseline.")]
    if json.load(open(p)) != _good():
        return False, "previous baseline was not preserved"
    if leftovers:
        return False, f"{len(leftovers)} temp files left behind"
    return ok, detail

if __name__ == "__main__":
    print("BASELINE STORE")
    results = [
        case("absent store is a legitimate first run", t_absent_is_not_an_error),
        case("corrupt store raises, never resets", t_corrupt_raises),
        case("empty store raises", t_empty_raises),
        case("malformed accepted block raises", t_malformed_accepted_raises),
        case("{} raises, never reads as first run", t_empty_object_raises),
        case("null accepted raises", t_null_accepted_raises),
        case("empty versions map raises", t_empty_versions_raises),
        case("established with no accepted block raises", t_missing_accepted_raises),
        case("unrecognised schema raises", t_unknown_schema_raises),
        case("explicit initialising state is legitimate", t_explicit_initialising_is_not_an_error),
        case("initialising carrying a baseline raises", t_initialising_with_accepted_raises),
        case("failed write raises, never reports success", t_unwritable_raises),
        case("serialise failure leaves the previous baseline intact", t_serialise_failure_preserves_previous),
        case("REPLACE failure leaves the previous baseline intact", t_replace_failure_preserves_previous),
    ]
    print(f"\n  {sum(results)}/{len(results)} passed")
    print("\n  LIMIT. These exercise failure during serialisation and failure at the")
    print("  replacement step. They do not demonstrate power loss, filesystem crash")
    print("  consistency, or fsync actually reaching the device. Those need different")
    print("  tooling and are not claimed here.")
    sys.exit(0 if all(results) else 1)
