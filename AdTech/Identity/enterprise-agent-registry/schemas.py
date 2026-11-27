from pydantic import BaseModel, Field
from typing import Literal


class AgentRegistration(BaseModel):

    agent_id: str = Field(min_length=1, max_length=100)

    name: str

    tenant_id: str

    role: str

    model: Literal["openai/gpt-4o-mini"]

    allowed_actions: list[
        Literal[
            "read_campaign",
            "analyze_campaign",
            "approve_campaign",
            "reject_campaign"
        ]
    ]

    capabilities: list[str]


class AgentRequest(BaseModel):

    request: str = Field(min_length=1, max_length=4000)


class AgentAction(BaseModel):

    action: Literal[
        "read_campaign",
        "analyze_campaign",
        "approve_campaign",
        "reject_campaign",
        "unknown"
    ]

    reason: str