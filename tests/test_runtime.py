import os, tempfile
import pytest
from catalog import TOPICS,group,topic
from runtime import RuntimeContext,retrieve,policy_decision,guarded_action,plan,orchestrate,audit_hash_chain,checkpoint,checkpoint_status,route

def test_catalog():
    assert len(TOPICS)==58
    assert topic(58)=="Compliance evidence"
    assert group(52)=="Security and governance"
def test_tenant_isolation():
    assert all(x["tenant"]=="alpha" for x in retrieve("campaign","alpha"))
    assert all(x["tenant"]=="beta" for x in retrieve("campaign","beta"))
def test_pdp_denies_cross_tenant_and_write():
    ctx=RuntimeContext(tenant="alpha",scopes=["campaign:read"])
    assert policy_decision({"operation":"read","tenant":"alpha","scope":"campaign:read"},ctx)
    assert not policy_decision({"operation":"read","tenant":"beta","scope":"campaign:read"},ctx)
    with pytest.raises(PermissionError): guarded_action({"operation":"write","tenant":"alpha","scope":"campaign:read"},ctx)
def test_checkpoint_survives_connection():
    with tempfile.TemporaryDirectory() as tmp:
        path=tmp+"/workflow.sqlite"
        checkpoint(path,"wf1",1,"completed")
        assert checkpoint_status(path,"wf1")==[(1,"completed")]
        assert checkpoint_status(path,"wf2")==[]
def test_audit_chain():
    chain=audit_hash_chain([{"x":1},{"x":2}])
    assert chain[1]["previous"]==chain[0]["digest"]
def test_route_uses_llm(monkeypatch):
    ctx=RuntimeContext()
    monkeypatch.setattr(ctx,"llm",lambda *a,**k:"engagement")
    assert route("email clicks",ctx)=="engagement"
def test_plan_rejects_invalid_tools(monkeypatch):
    ctx=RuntimeContext()
    monkeypatch.setattr(ctx,"llm",lambda *a,**k:'{"steps":[{"agent":"shell","task":"rm -rf /"}]}')
    with pytest.raises(ValueError):plan("danger",ctx)
def test_plan_accepts_bounded_tasks(monkeypatch):
    ctx=RuntimeContext()
    monkeypatch.setattr(ctx,"llm",lambda *a,**k:'{"steps":[{"agent":"campaign","task":"metrics"}]}')
    assert len(plan("metrics",ctx))==1
