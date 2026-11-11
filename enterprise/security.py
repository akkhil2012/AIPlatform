"""OIDC JWT verification and external Open Policy Agent authorization."""
import os
from dataclasses import dataclass
from functools import lru_cache
import httpx
import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

OIDC_ISSUER=os.getenv("OIDC_ISSUER","http://localhost:8080/realms/aiplatform")
OIDC_AUDIENCE=os.getenv("OIDC_AUDIENCE","aiplatform-api")
JWKS_URL=os.getenv("OIDC_JWKS_URL",OIDC_ISSUER.rstrip("/")+"/protocol/openid-connect/certs")
OPA_URL=os.getenv("OPA_URL","http://opa:8181/v1/data/aiplatform/allow")
bearer=HTTPBearer(auto_error=True)

@dataclass(frozen=True)
class Principal:
    sub:str
    tenant:str
    scopes:frozenset[str]
    issuer:str

@lru_cache(maxsize=1)
def jwks_client():
    return jwt.PyJWKClient(JWKS_URL,cache_jwk_set=True,lifespan=300)

def verify_token(token:str)->Principal:
    try:
        key=jwks_client().get_signing_key_from_jwt(token).key
        claims=jwt.decode(token,key,algorithms=["RS256"],audience=OIDC_AUDIENCE,issuer=OIDC_ISSUER,options={"require":["exp","iat","iss","sub","aud"]},leeway=30)
        tenant=claims.get("tenant")
        if not isinstance(tenant,str) or not tenant: raise ValueError("Missing trusted tenant claim")
        raw=claims.get("scope","")
        scopes=frozenset(raw.split()) if isinstance(raw,str) else frozenset()
        return Principal(sub=claims["sub"],tenant=tenant,scopes=scopes,issuer=claims["iss"])
    except Exception as exc:
        raise HTTPException(status_code=401,detail="Invalid OIDC bearer token") from exc

def authenticated(credentials:HTTPAuthorizationCredentials=Depends(bearer))->Principal:
    return verify_token(credentials.credentials)

async def authorize(principal:Principal,action:str,resource:dict)->None:
    payload={"input":{"subject":principal.sub,"tenant":principal.tenant,"scopes":sorted(principal.scopes),"action":action,"resource":resource}}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp=await client.post(OPA_URL,json=payload)
            resp.raise_for_status()
            decision=resp.json().get("result") is True
    except Exception as exc:
        raise HTTPException(status_code=503,detail="Policy decision unavailable") from exc
    if not decision: raise HTTPException(status_code=403,detail="Policy denied request")
