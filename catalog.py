"""Curriculum metadata for all 58 executable demo scenarios."""
TOPICS = [
"Enterprise agentic platform vs chatbot","Enterprise AI platform reference architecture","Control plane vs execution plane","Essential agent runtime components","Single-agent vs multi-agent","Deterministic workflow vs planning","Typed A2A contracts","Deterministic enforcement of AI output","Least privilege and least agency","Durable workflow checkpoints","Planning/execution context isolation","Latency and cost budgets","Observability and tracing","Evaluation release gates","Graceful degradation","Versioned contracts and rollout","Human accountability",
"Supervisor architecture","Sequential and parallel orchestration","Agent loop prevention","Partial failure recovery","Planner-executor","Reflection and refinement","Human-in-the-loop approval","Capability registry","Minimal context sharing","Orchestration metrics",
"MCP tool discovery and invocation","MCP versus A2A","MCP tool gateway","Secure agent communication","Confused deputy defense","Two-level authorization","Idempotent tool retries","Governed dynamic discovery","Malicious tool response handling","Protocol version compatibility",
"Session management","Durable agent recovery","Short-term and long-term memory","Context budget guard","Tenant-isolated RAG","Knowledge freshness","Knowledge graph vs vector retrieval","Shared agent memory","Safe memory summarization","Vector migration","Secure RAG caching",
"Zero trust agents","Least agency budgets","Identity delegation chain","PDP and PEP enforcement","Prompt injection defense","Tamper-evident audit","Secret management","Tenant isolation","Production change approvals","Compliance evidence"]
assert len(TOPICS) == 58
GROUPS = [(1,17,"Platform architecture"),(18,27,"Orchestration"),(28,37,"MCP and A2A"),(38,48,"Memory and RAG"),(49,58,"Security and governance")]
def topic(number:int)->str:
    if not 1 <= number <= 58: raise ValueError("Select 1-58")
    return TOPICS[number-1]
def group(number:int)->str:
    return next(name for start,end,name in GROUPS if start<=number<=end)
