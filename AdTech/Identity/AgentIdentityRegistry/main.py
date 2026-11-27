import os
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal
from agent_registry import AgentRegistry

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY is not set")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

registry = AgentRegistry("agent_registry.yml")


class AgentAction(BaseModel):
    action: Literal[
        "read_campaign",
        "analyze_campaign",
        "approve_campaign",
        "reject_campaign",
        "unknown",
    ]
    reason: str


def execute_agent(agent_id, user_request):
    agent = registry.get_agent(agent_id)

    response = client.chat.completions.create(
        model=agent["model"],
        messages=[
            {
                "role": "system",
                "content": f"""
                You are {agent['name']}.

                Your role is {agent['role']}.

                Identify the requested action.

                Supported actions:
                read_campaign
                analyze_campaign
                approve_campaign
                reject_campaign
                unknown

                Use unknown for unsupported requests.

                Return JSON with action and reason.
                """,
            },
            {"role": "user", "content": user_request},
        ],
        response_format={"type": "json_object"},
    )

    result = AgentAction.model_validate_json(response.choices[0].message.content)

    authorized = registry.authorize(agent_id, result.action)

    print("Agent ID:", agent_id)
    print("Agent Role:", agent["role"])
    print("Agent Version:", agent["version"])
    print("Requested Action:", result.action)

    if authorized:
        print("Decision: ALLOWED")
    else:
        print("Decision: DENIED")

    print("-" * 40)


#execute_agent("marketing-agent-001", "Approve campaign 123")
execute_agent("compliance-agent-001", "Approve campaign 123")





