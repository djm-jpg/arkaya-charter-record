"""Sequence regression tests: whole observation histories, not single states.

DM, 14 September 2026: "Add this complete sequence as a regression test;
validating store shapes alone cannot catch it."

He was right, and the reason is worth keeping. The v6 defect was a STATE
TRANSITION, not a state: every individual store the adapter wrote was
well-formed and passed all fourteen shape tests. What was wrong was what
happened between two of them. Only a sequence sees that.

No network. live._get is replaced with a controlled responder.
"""
import hashlib, json, os, sys, tempfile
import live, checks, run_acceptance
from fixtures import SPEC

BODIES = {"v1": b"CHARTER V1", "v1.1": b"CHARTER V1.1", "v2": b"CHARTER V2", "v3": b"CHARTER V3"}
DATES = {"v1": "2026-05-19", "v1.1": "2026-05-28", "v2": "2026-07-29", "v3": "2026-07-29"}
ORDER = ["v1", "v1.1", "v2", "v3"]
PUB = "2026-09-20"

def _dig(b): return "sha256:" + hashlib.sha256(b).hexdigest()

def make_index(bodies, versions=ORDER):
    out = []
    for i, v in enumerate(versions):
        nxt = versions[i + 1] if i + 1 < len(versions) else None
        e = {"version": v, "instrument_date": DATES[v], "published_to_record": PUB,
             "reason": None if i == 0 else f"reason {v}",
             "revision_class": "minor_decimal" if "." in v.lstrip("v") else "whole_integer",
             "is_current": nxt is None, "entry_url": v, "content_digest": _dig(bodies[v])}
        if nxt:
            e.update({"superseded_by": nxt, "superseded_from": "2026-07-29"})
        out.append(e)
    return {"change_log_dated": True, "external_anchor": "rfc3161:example", "versions": out}

def responder(bodies, versions=ORDER):
    idx = json.dumps(make_index(bodies, versions)).encode()
    def _get(url, headers=None):
        if url.endswith("/index.json"):
            return 200, idx, {}
        leaf = url.rstrip("/").rsplit("/", 1)[-1]
        if leaf in versions:
            return 200, bodies[leaf], {}
        if leaf in ("record", "") or url.endswith("/record/"):
            return 200, b"<h1>record</h1>", {}
        return 404, b"nope", {}
    return _get

BASE = "http://stub/record/"

def observe(get):
    live._get = get
    st = live.fetch(BASE)
    results = {c(st, SPEC).check: c(st, SPEC).passed for c in checks.ALL_CHECKS}
    clean = all(v for k, v in results.items() if k.split()[0] in {"8", "10", "11", "12"})
    try:
        note = live.record_observation(st, clean)
    except live.BaselineError as e:
        note = f"REFUSED: {e}"
    return results, note

def accepted_versions():
    try:
        d = live._load_raw()
    except live.BaselineError as e:
        return f"STORE ERROR: {e}"
    return sorted((d.get("accepted") or {}).get("versions") or {})

def t_empty_index_must_not_lose_the_baseline():
    """DM's sequence, 14 September 2026."""
    live.SNAPSHOT = os.path.join(tempfile.mkdtemp(), "b.json")
    steps = []

    r, n = observe(responder(BASE_BODIES := dict(BODIES)))
    steps.append(("1 establish", n, accepted_versions()))

    r, n = observe(responder(BASE_BODIES))
    steps.append(("2 unchanged", n, accepted_versions()))
    if not all(r.values()):
        return False, "step 2 should pass everything", steps

    # 3. the record serves an empty index. No corruption, no operator action.
    r, n = observe(responder(BASE_BODIES, versions=[]))
    kept = accepted_versions()
    steps.append(("3 empty index", n, kept))
    if kept != ORDER:
        return False, f"BASELINE LOST at step 3: accepted={kept}", steps

    # 4. the record returns, with v2's bytes changed and its digest updated to
    #    match, which is the substitution the baseline exists to catch.
    altered = dict(BASE_BODIES); altered["v2"] = b"CHARTER V2 SUBSTITUTED"
    r, n = observe(responder(altered))
    steps.append(("4 altered returns", n, accepted_versions()))
    if r["8 no silent revision"]:
        return False, "step 4: substitution accepted as the new baseline", steps

    # 5. repeated. Must still fail.
    r, n = observe(responder(altered))
    steps.append(("5 repeated", n, accepted_versions()))
    if r["8 no silent revision"]:
        return False, "step 5: substitution passed on repeat", steps
    return True, "baseline survived the empty index and still caught the substitution", steps

def t_invariant_refuses_a_narrowing_write():
    live.SNAPSHOT = os.path.join(tempfile.mkdtemp(), "b.json")
    live._save_raw({"schema": live.SCHEMA, "state": live.STATE_ESTABLISHED,
                    "accepted": {"versions": {"v1": "a", "v2": "b"}, "at": "t0"}})
    try:
        live._save_raw({"schema": live.SCHEMA, "state": live.STATE_ESTABLISHED,
                        "accepted": {"versions": {"v1": "a"}, "at": "t1"}},
                       before={"v1": "a", "v2": "b"})
        return False, "a narrowing write was allowed", []
    except live.BaselineError:
        pass
    try:
        live._save_raw({"schema": live.SCHEMA, "state": live.STATE_INITIALISING},
                       before={"v1": "a", "v2": "b"})
        return False, "a revert to initialising was allowed", []
    except live.BaselineError:
        pass
    # DM, 14 September 2026: the guard protected membership and state but not
    # the accepted digest of a retained version. A direct write could rewrite
    # what the record is compared against.
    try:
        live._save_raw({"schema": live.SCHEMA, "state": live.STATE_ESTABLISHED,
                        "accepted": {"versions": {"v1": "a", "v2": "SUBSTITUTED"}, "at": "t2"}},
                       before={"v1": "a", "v2": "b"})
        return False, "a changed accepted digest was allowed", []
    except live.BaselineError:
        pass
    # And the permitted case must still work: growth with existing digests intact.
    try:
        live._save_raw({"schema": live.SCHEMA, "state": live.STATE_ESTABLISHED,
                        "accepted": {"versions": {"v1": "a", "v2": "b", "v3": "c"}, "at": "t3"}},
                       before={"v1": "a", "v2": "b"})
    except live.BaselineError as e:
        return False, f"growth was wrongly refused: {e}", []
    return True, "narrowing, reverting and digest rewriting refused; growth allowed", []

if __name__ == "__main__":
    print("SEQUENCE REGRESSION")
    ok_all = True
    for name, fn in [("empty index must not lose an established baseline",
                      t_empty_index_must_not_lose_the_baseline),
                     ("invariant refuses narrowing, reverting and digest rewriting",
                      t_invariant_refuses_a_narrowing_write)]:
        ok, detail, steps = fn()
        ok_all &= ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
        for s in steps:
            print(f"           {s[0]:<20} {s[1][:58]:<58} accepted={s[2]}")
    sys.exit(0 if ok_all else 1)
