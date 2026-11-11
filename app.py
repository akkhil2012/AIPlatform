"""Streamlit management-ready AI platform demonstration."""
import json, os, time, uuid
import streamlit as st
from catalog import TOPICS,GROUPS,topic,group
from runtime import RuntimeContext, CAPABILITIES, DOCS, topic_demo, supervisor, orchestrate, review, guarded_action, retrieve, audit_hash_chain, checkpoint, checkpoint_status
from llm import LLMError

st.set_page_config(page_title="Enterprise Agentic AI Platform | 58 Labs",page_icon="🧠",layout="wide")
st.title("Enterprise Agentic AI Platform")
st.caption("58 architecture topics · live LLM calls · supervisor and specialists · policy enforcement · traceability")
with st.sidebar:
    st.header("Model configuration")
    key=st.text_input("OpenAI-compatible API key",type="password",help="Used for this session only; not stored by this app.",value="")
    model=st.text_input("Model",value=os.getenv("OPENAI_MODEL","gpt-4.1-mini"))
    base_url=st.text_input("HTTPS API base URL",value=os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1"))
    st.divider()
    tenant=st.selectbox("Tenant",["alpha","beta"])
    scopes=st.multiselect("Granted scopes",["campaign:read","engagement:read","risk:read"],default=["campaign:read","engagement:read","risk:read"])
    budget=st.slider("Maximum LLM calls",1,12,6)
    st.info("Synthetic demo data only. Real actions are disabled. This is not a production security boundary.")
settings={"api_key":key or None,"model":model,"base_url":base_url}
tabs=st.tabs(["Executive demo","58 topic labs","Policy and identity","Memory and RAG","Audit and recovery","Architecture"])
def context():
    return RuntimeContext(tenant=tenant,scopes=scopes,max_llm_calls=budget)
def render(result):
    st.markdown("### Result")
    st.write(result.get("answer",""))
    if "agent" in result: st.caption("Selected agent: "+result["agent"])
    if "architecture_explanation" in result:
        with st.expander("Architecture explanation",expanded=True): st.write(result["architecture_explanation"])
    if "steps" in result: st.dataframe(result["steps"],use_container_width=True)
    if "critique" in result:
        with st.expander("Reflection details"): st.write("Draft:",result["draft"],"Critique:",result["critique"])
    if "evidence" in result:
        with st.expander("Retrieved evidence"): st.json(result["evidence"])
    if "policy" in result: st.json(result["policy"])
    with st.expander("Execution trace and decision evidence",expanded=True): st.json(result.get("trace",[]))
def run(mode,query,number=None):
    if not (key or os.getenv("OPENAI_API_KEY")):
        st.error("Provide an API key in the sidebar or set OPENAI_API_KEY.");return
    ctx=context()
    start=time.perf_counter()
    try:
        with st.spinner("Calling the configured LLM and executing governed workflow..."):
            if mode=="Supervisor": result=supervisor(query,ctx,**settings)
            elif mode=="Planner / executor": result=orchestrate(query,ctx,**settings)
            elif mode=="Reflection": result=review(query,ctx,**settings)
            else: result=topic_demo(number,query,ctx,**settings)
        st.success(f"Completed in {time.perf_counter()-start:.2f}s · {ctx.calls} LLM calls")
        render(result)
    except Exception as exc:
        st.error(f"Execution stopped safely: {type(exc).__name__}: {exc}")
        with st.expander("Trace"): st.json(ctx.trace)
with tabs[0]:
    st.subheader("Management demonstration: governed marketing analytics")
    st.write("Watch the model route or plan tasks, while deterministic code enforces permissions, budgets, tenant isolation and execution contracts.")
    mode=st.radio("Demo pattern",["Supervisor","Planner / executor","Reflection"],horizontal=True)
    question=st.text_area("Business request","Compare campaign engagement with application approvals and identify any limitations in the available evidence.",key="exec_q")
    if st.button("Run live agent demo",type="primary",key="run_exec"): run(mode,question)
    st.markdown("**Narrative:** A request enters the harness → LLM selects a specialist or creates a bounded plan → policy checks precede each specialist → tenant-filtered evidence is retrieved → LLM responds → trace records every step.")
with tabs[1]:
    st.subheader("All 58 branch topics")
    category=st.selectbox("Curriculum domain",[g[2] for g in GROUPS])
    available=[i for i in range(1,59) if group(i)==category]
    number=st.selectbox("Choose a topic",available,format_func=lambda n:f"{n:02d} · {topic(n)}")
    st.info(f"Topic {number:02d}: {topic(number)}")
    st.caption("All topics execute an actual LLM call. Specialized paths are used for orchestration, RAG, reflection, and governance; remaining topics use the shared supervisor and a second LLM-based architectural explanation. These are educational scenarios, not 58 separate complete implementations.")
    q=st.text_area("Experiment prompt","Explain and demonstrate this pattern for enterprise marketing analytics, with its main tradeoffs.",key="topic_q")
    if st.button("Execute topic PoC",type="primary"): run("Topic",q,number)
with tabs[2]:
    st.subheader("Deterministic policy enforcement")
    operation=st.selectbox("Requested operation",["read","write","delete"])
    resource_tenant=st.selectbox("Resource tenant",["alpha","beta"])
    scope=st.selectbox("Required scope",["campaign:read","engagement:read","risk:read","admin:write"])
    if st.button("Evaluate PDP → PEP"):
        ctx=context()
        action={"operation":operation,"tenant":resource_tenant,"scope":scope}
        try: st.success(str(guarded_action(action,ctx)))
        except PermissionError as exc: st.error(str(exc))
        st.json(ctx.trace)
    st.caption("LLM output cannot override the Python policy enforcement point. Only tenant-matched, scoped, read-only actions are permitted.")
with tabs[3]:
    st.subheader("Tenant-scoped retrieval")
    query=st.text_input("Search synthetic knowledge","campaign applications")
    results=retrieve(query,tenant)
    st.dataframe(results,use_container_width=True)
    st.caption("This uses a small keyword-based retriever, not embeddings or a vector database. Switching tenants changes which documents are eligible for retrieval.")
with tabs[4]:
    st.subheader("Tamper-evident audit illustration")
    sample=[{"action":"request","tenant":tenant},{"action":"policy","decision":"allow"},{"action":"result","status":"complete"}]
    st.json(audit_hash_chain(sample))
    st.warning("The default HMAC key is a demo constant. Production requires protected key management, durable append-only storage and external anchoring.")
    st.subheader("SQLite checkpoint illustration")
    wf=st.text_input("Workflow ID",value="demo-workflow")
    step=st.number_input("Step",min_value=1,max_value=10,value=1)
    if st.button("Persist checkpoint"):
        checkpoint("demo_checkpoints.sqlite",wf,int(step),"completed")
        st.success("Checkpoint persisted in local SQLite")
    if st.button("Load checkpoints"): st.write(checkpoint_status("demo_checkpoints.sqlite",wf))
with tabs[5]:
    st.subheader("Reference architecture")
    st.code("""Streamlit UI
    │
    ▼
Harness / Supervisor ──► LLM Gateway (OpenAI-compatible HTTPS)
    │                          │
    ├──► Planner (bounded) ◄───┘
    │
    ├──► PDP / PEP ──► Scoped Tool/Agent Registry
    │                         │
    ├──► Campaign Specialist ─┤
    ├──► Engagement Specialist┤──► Tenant-filtered knowledge
    └──► Risk Specialist ─────┘
    │
    ├──► In-memory execution trace
    ├──► HMAC audit illustration
    └──► SQLite checkpoint illustration""",language="text")
    st.markdown("""**Implemented:** real LLM API calls, model-based routing/planning/reflection, bounded tool-like specialist invocation, deterministic authorization, synthetic tenant-filtered retrieval, trace collection, and SQLite checkpoint demonstration.

**Not implemented:** real MCP/A2A transport, production authentication, distributed queues, persistent secret vault, vector database, real business integrations, automated model evaluation, and cloud deployment. The 58 curriculum entries reuse shared building blocks; they are not 58 independently deployed services.""")
