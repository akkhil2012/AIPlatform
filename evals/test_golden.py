"""Offline golden evaluation release gate (no external model required)."""
import json
from pathlib import Path
from runtime import RuntimeContext,policy_decision,retrieve,CAPABILITIES

def evaluate():
    cases=json.loads((Path(__file__).parent/"golden.json").read_text())["cases"]
    failures=[]
    for case in cases:
        if case["kind"]=="policy":
            ctx=RuntimeContext(tenant=case["tenant"],scopes=case["scopes"])
            action=case["action"]
            mapped={"operation":action["operation"],"tenant":action["tenant"],"scope":action["scope"]}
            ok=policy_decision(mapped,ctx)==case["expected_allowed"]
        elif case["kind"]=="retrieval":
            ok=all(doc["tenant"]==case["expected_tenant"] for doc in retrieve(case["query"],case["tenant"]))
        elif case["kind"]=="planner":
            steps=case["steps"]
            valid=bool(steps) and len(steps)<=3 and all(s.get("agent") in CAPABILITIES for s in steps)
            ok=valid==case["expected_valid"]
        else: ok=False
        if not ok: failures.append(case["id"])
    return len(cases),failures

def test_golden_release_gate():
    count,failures=evaluate()
    assert count>=6
    assert not failures, "Golden evaluation failures: "+", ".join(failures)

if __name__=="__main__":
    total,failures=evaluate()
    print(f"Golden cases: {total}, failures: {failures}")
    raise SystemExit(bool(failures))
