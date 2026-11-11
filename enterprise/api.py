"""FastAPI gateway: verified OIDC, external OPA, MCP/A2A and durable jobs."""
import os,uuid
from fastapi import FastAPI,Depends,HTTPException,Header
from pydantic import BaseModel,Field
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from enterprise.security import Principal,authenticated,authorize
from enterprise.db import submit_job,get_job,retrieve
from enterprise.mcp_client import search_knowledge
from enterprise.a2a_client import ask_risk_agent
from enterprise.telemetry import setup_telemetry

app=FastAPI(title="AIPlatform Enterprise Gateway",version="0.2.0")
setup_telemetry(app)
bearer=HTTPBearer()

class Query(BaseModel):
    text:str=Field(min_length=1,max_length=2000)

class JobRequest(BaseModel):
    question:str=Field(min_length=1,max_length=2000)

@app.get("/health/live")
def live(): return {"status":"alive"}

@app.get("/health/ready")
def ready():
    # Liveness is separate from dependency readiness; check DB.
    from enterprise.db import connection
    try:
        with connection() as db: db.execute("SELECT 1")
        return {"status":"ready"}
    except Exception: raise HTTPException(503,"Database unavailable")

@app.post("/v1/mcp/search")
async def mcp_search(q:Query,p:Principal=Depends(authenticated),creds:HTTPAuthorizationCredentials=Depends(bearer)):
    await authorize(p,"read",{"tenant":p.tenant,"type":"campaign","scope":"campaign:read"})
    return {"results":await search_knowledge(creds.credentials,q.text)}

@app.post("/v1/a2a/risk")
async def risk(q:Query,p:Principal=Depends(authenticated)):
    await authorize(p,"read",{"tenant":p.tenant,"type":"risk","scope":"risk:read"})
    return {"remote":await ask_risk_agent(q.text)}

@app.post("/v1/jobs",status_code=202)
async def enqueue(q:JobRequest,p:Principal=Depends(authenticated),idempotency_key:str=Header(...,alias="Idempotency-Key")):
    await authorize(p,"submit",{"tenant":p.tenant,"type":"analysis","scope":"campaign:read"})
    try: return submit_job(p.tenant,p.sub,idempotency_key,{"question":q.question})
    except ValueError as exc: raise HTTPException(409,str(exc)) from exc

@app.get("/v1/jobs/{job_id}")
async def job_status(job_id:uuid.UUID,p:Principal=Depends(authenticated)):
    await authorize(p,"read",{"tenant":p.tenant,"type":"analysis","scope":"campaign:read"})
    result=get_job(p.tenant,p.sub,str(job_id))
    if result is None: raise HTTPException(404,"Job not found")
    return result

@app.post("/v1/rag")
async def rag(q:Query,p:Principal=Depends(authenticated)):
    await authorize(p,"read",{"tenant":p.tenant,"type":"campaign","scope":"campaign:read"})
    # 3-dimensional deterministic toy embedding. Use a real embedding model for production.
    terms=q.text.lower()
    vector=[float("campaign" in terms)+0.1,float("beta" in terms)+0.1,float("approval" in terms)+0.1]
    return {"documents":retrieve(p.tenant,vector)}
