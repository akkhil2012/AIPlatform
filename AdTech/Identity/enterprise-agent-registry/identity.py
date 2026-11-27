import jwt
from pathlib import Path
from fastapi import HTTPException

PUBLIC_KEY = Path("keys/public.pem").read_text()


def verify_identity(token):

    try:

        return jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience="agent-platform",
            issuer="enterprise-identity-provider",
            options={
                "require": [
                    "sub", "exp", "iat",
                    "tenant_id", "principal_type"
                ]
            }
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid identity token"
        )