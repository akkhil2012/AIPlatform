import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import Base, engine
from schemas import AgentRegistration, AgentRequest
from registry import AgentRegistry
from identity import verify_identity
from policy_engine import authorize
from llm_service import identify_action

app = FastAPI(title="Enterprise Agent Registry")

registry = AgentRegistry()

security = HTTPBearer()

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("agent-audit")

# Local demonstration only.
# Use Alembic migrations in production.
Base.metadata.create_all(bind=engine)


def authenticate(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    return verify_identity(credentials.credentials)


def require_admin(identity=Depends(authenticate)):

    if identity["principal_type"] != "admin":
        raise HTTPException(403, "Admin required")

    return identity


@app.post("/agents", status_code=201)
def register_agent(
    registration: AgentRegistration,
    identity=Depends(require_admin)
):

    if registration.tenant_id != identity["tenant_id"]:
        raise HTTPException(403, "Tenant mismatch")

    return registry.register(registration)


@app.get("/agents/discover")
def discover_agents(
    capability: str,
    identity=Depends(authenticate)
):

    return registry.discover(
        identity["tenant_id"],
        capability
    )


@app.get("/agents/me")
def get_agent_identity(identity=Depends(authenticate)):

    if identity["principal_type"] != "agent":
        raise HTTPException(403, "Agent identity required")

    return registry.resolve(
        identity["sub"],
        identity["tenant_id"]
    )


@app.post("/agents/{agent_id}/deactivate")
def deactivate_agent(
    agent_id: str,
    identity=Depends(require_admin)
):

    return registry.deactivate(
        agent_id,
        identity["tenant_id"]
    )


@app.post("/execute")
def execute_agent(
    request: AgentRequest,
    identity=Depends(authenticate)
):

    if identity["principal_type"] != "agent":
        raise HTTPException(403, "Agent identity required")

    agent_id = identity["sub"]

    # 1. Resolve authenticated agent
    agent = registry.resolve(
        agent_id,
        identity["tenant_id"]
    )

    # 2. LLM proposes an action
    try:
        result = identify_action(
            agent,
            request.request
        )
    except Exception:
        raise HTTPException(502, "Action classification failed")

    # 3. Revalidate identity and registry state
    agent = registry.resolve(
        agent_id,
        identity["tenant_id"]
    )

    # 4. OPA evaluates authorization
    permitted = authorize(
        identity,
        agent,
        result.action
    )

    # 5. Generate audit event
    logger.info(
        "agent=%s tenant=%s version=%s action=%s allowed=%s",
        agent_id,
        identity["tenant_id"],
        agent["version"],
        result.action,
        permitted
    )

    # 6. Enforce authorization
    if not permitted:

        raise HTTPException(
            status_code=403,
            detail="Action not authorized"
        )

    # 7. Return authorized action
    # Actual business tool execution is not implemented.
    return {
        "agent_id": agent_id,
        "version": agent["version"],
        "action": result.action,
        "decision": "ALLOWED"
    }