import os

from openai import OpenAI
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    query: str = Field(
        min_length=5,
        max_length=200,
        description="The query to be processed by the agent.",
    )


def execute_agent(request: AgentRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENROUTER_API_KEY before running the agent.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        messages=[
            {"role": "user", "content": request.query},
        ],
        timeout=30,
        extra_headers={
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", ""),
            "X-Title": os.getenv("OPENROUTER_APP_NAME", "AdTech Agent"),
        },
    )

    answer = response.choices[0].message.content
    return {"status": "success", "message": answer}


if __name__ == "__main__":
    request = AgentRequest(query="What is the weather like today?")
    print(execute_agent(request))