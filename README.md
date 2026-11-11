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

## Enterprise integration branch (Phase 2)

Switch to `feature/enterprise-integrations` to use **actual MCP and A2A SDKs**, external OIDC token validation, OPA, pgvector, leased durable jobs, OpenTelemetry and Docker Compose.

```bash
git switch feature/enterprise-integrations
cp .env.example .env
# Edit .env with a strong Postgres password, actual OIDC issuer/JWKS/audience and optional LLM API key.
docker compose up --build -d
docker compose ps
```

- Streamlit: http://localhost:8501 (new **Enterprise integrations** tab)
- FastAPI gateway: http://localhost:8000/docs
- Internal-only MCP: `http://mcp:8002/mcp` (not exposed on host)
- Internal-only A2A specialist: `http://a2a:8003/`
- OPA: `http://opa:8181` (internal)
- PostgreSQL: internal network only

**Identity setup is required:** Provide a token from an actual OIDC provider with RS256 signature, audience `aiplatform-api`, a signed `tenant` claim (`alpha` or `beta` for demo data), and space-separated `scope` claims such as `campaign:read risk:read`. Configure the exact issuer and container-reachable JWKS URL in `.env`. This project does not fabricate credentials or ship a default administrator.

Try a read-only request:

```bash
curl -X POST http://localhost:8000/v1/rag \
  -H "Authorization: Bearer $OIDC_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"campaign approval"}'
```

Submit an idempotent background job:

```bash
curl -X POST http://localhost:8000/v1/jobs \
  -H "Authorization: Bearer $OIDC_ACCESS_TOKEN" \
  -H "Idempotency-Key: management-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"question":"Summarize campaign conversion"}'
```

Then call `GET /v1/jobs/{id}` with the same token. Submitting the same request with the same key returns the same job ID. Changing the payload with the same key is rejected.

Run the offline unit and golden evaluation gates:

```bash
pip install -r requirements-enterprise.txt
python -m pytest -q tests evals
```

The CI workflow additionally compiles Python modules and builds a container image. **The source has been committed, but the full Docker stack, external identity provider, MCP/A2A protocol compatibility, and live model calls have not yet been validated.** See [enterprise architecture and limitations](docs/enterprise-architecture.md).
