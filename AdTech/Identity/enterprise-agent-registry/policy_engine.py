import os
import httpx

OPA_URL = os.getenv(
    "OPA_URL",
    "http://localhost:8181"
)


def authorize(identity, agent, action):

    payload = {
        "input": {
            "identity": identity,
            "agent": agent,
            "action": action
        }
    }

    try:

        response = httpx.post(
            f"{OPA_URL}/v1/data/agent_authz/allow",
            json=payload,
            timeout=3
        )

        response.raise_for_status()

        return response.json().get("result") is True

    except (httpx.HTTPError, ValueError):

        # Fail closed when authorization is unavailable
        return False