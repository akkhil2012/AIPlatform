import jwt
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

PRIVATE_KEY = Path("keys/private.pem").read_text()

agent_id = sys.argv[1]

principal_type = (
    sys.argv[2] if len(sys.argv) > 2 else "agent"
)

now = datetime.now(timezone.utc)

token = jwt.encode(
    {
        "sub": agent_id,
        "principal_type": principal_type,
        "tenant_id": "marketing-tenant",
        "iss": "enterprise-identity-provider",
        "aud": "agent-platform",
        "iat": now,
        "exp": now + timedelta(minutes=5)
    },
    PRIVATE_KEY,
    algorithm="RS256"
)

print(token)