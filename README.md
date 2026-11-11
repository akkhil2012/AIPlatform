# AIPlatform — Streamlit Agentic AI PoC

Management-ready interactive proof of concept for the 58-topic [AgenticSamplesPrincipalEngineer curriculum](https://github.com/akkhil2012/AgenticSamplesPrincipalEngineer). One shared real-LLM runtime powers the 58 topic exercises; these are not 58 independently implemented production services.

## Start

```bash
git clone https://github.com/akkhil2012/AIPlatform.git
cd AIPlatform
git switch feature/agentic-platform-streamlit-poc
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
streamlit run app.py
```

Open http://localhost:8501. Or enter your API key in the sidebar. The default model is `gpt-4.1-mini`; choose a compatible model and HTTPS API endpoint. Never commit secrets.

## Management demonstration (10 minutes)

1. Architecture: UI → supervisor/planner → LLM gateway → PDP/PEP → specialists → evidence.
2. Supervisor: ask "Summarize campaign engagement." Inspect model routing and trace.
3. Planner: ask "Compare engagement and application funnel." Show validated JSON plan and sequential specialists.
4. Security: switch tenant, remove agent scopes, and try a write operation; inspect denial.
5. Reliability: persist/reload SQLite checkpoint and inspect chained audit evidence.
6. Roadmap: distinguish demonstration-only components from enterprise integrations.

## Project files

- `app.py`: Streamlit UI with executive demo, 58 labs, policy, retrieval, audit, architecture tabs
- `catalog.py`: 58 topics in five domains
- `llm.py`: real OpenAI-compatible HTTPS Chat Completions client
- `runtime.py`: supervisor, planner, reflection, specialist policies, synthetic retrieval, tracing, checkpoints, audit
- `tests/test_runtime.py`: offline unit tests; run with `python3 -m pytest -q`

## Scope

**Implemented:** live LLM calls, routing, bounded JSON planning, sequential specialists, reflection, deterministic authorization, synthetic tenant-filtered retrieval, trace capture, SQLite checkpoint illustration, and HMAC audit-chain illustration.

**Not implemented:** networked MCP/A2A, production authentication, distributed durable orchestration, vector DB, real business systems, secure key vault, model eval release gates or cloud deployment. Planner is sequential, not parallel. Audit key is hardcoded for demonstration and must not be used for compliance. Tenant and scopes selected in UI are not authenticated identity. No production security or performance assurances are implied.

## Recommended next milestones

Real MCP SDK server/client; remote A2A specialist; OIDC and external PDP; Postgres/pgvector; durable queue with idempotency; OpenTelemetry and golden evaluation CI gates; containerized deployment.
