"""Real MCP SDK server: read-only campaign tools backed by Postgres.

Security boundary: the caller MUST supply a verified, signed, short-lived
delegation JWT minted by the API's identity provider. The MCP process validates
that JWT independently and never trusts arbitrary tenant arguments.
"""
import os
from mcp.server.fastmcp import FastMCP
from enterprise.security import verify_token
from enterprise.db import retrieve

mcp=FastMCP("aiplatform-knowledge",host="0.0.0.0",port=8002,stateless_http=True)

@mcp.tool()
def search_campaign_knowledge(delegation_token:str,query:str,limit:int=3)->list[dict]:
    """Search tenant-isolated campaign evidence using a verified OIDC delegation token."""
    principal=verify_token(delegation_token)
    if "campaign:read" not in principal.scopes: raise PermissionError("Missing campaign:read")
    # Deterministic toy embedding. Replace with a real embedding model in production.
    terms=query.lower()
    vector=[float("campaign" in terms)+0.1,float("beta" in terms)+0.1,float("approval" in terms)+0.1]
    rows=retrieve(principal.tenant,vector,limit)
    return [{"id":str(x["id"]),"title":x["title"],"content":x["content"]} for x in rows]

if __name__=="__main__":
    mcp.run(transport="streamable-http")
