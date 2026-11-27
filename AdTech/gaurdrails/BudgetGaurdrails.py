import os
from decimal import Decimal
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    max_retries=0,
    timeout=30
)


class BudgetPolicy(BaseModel):
    max_cost: Decimal = Decimal("0.05")
    max_tokens: int = 10000
    max_calls: int = 5
    max_output_tokens: int = 500


class BudgetGuardrail:

    def __init__(self):
        self.policy = BudgetPolicy()
        self.total_cost = Decimal("0")
        self.total_tokens = 0
        self.total_calls = 0

    def validate_budget(self):

        if self.total_cost >= self.policy.max_cost:
            raise RuntimeError("Cost budget exceeded")

        if self.total_tokens >= self.policy.max_tokens:
            raise RuntimeError("Token budget exceeded")

        if self.total_calls >= self.policy.max_calls:
            raise RuntimeError("LLM call limit exceeded")

    def call_llm(self, query: str):

        # Pre-execution budget check
        self.validate_budget()

        self.total_calls += 1

        response = client.chat.completions.create(
            model="openai/gpt-4.1-mini",
            messages=[
                {"role": "user", "content": query}
            ],
            max_completion_tokens=min(
                self.policy.max_output_tokens,
                self.policy.max_tokens - self.total_tokens
            ),
            extra_body={
                "usage": {"include": True}
            }
        )

        # Retrieve actual usage
        usage = response.usage

        if usage is None:
            raise RuntimeError("Usage information unavailable")

        cost = usage.model_dump().get("cost")

        if cost is None:
            raise RuntimeError("Cost information unavailable")

        # Update workflow budget
        self.total_tokens += usage.total_tokens
        self.total_cost += Decimal(str(cost))

        # Post-execution budget check
        if self.total_cost > self.policy.max_cost:
            raise RuntimeError("Cost budget exceeded")

        if self.total_tokens > self.policy.max_tokens:
            raise RuntimeError("Token budget exceeded")

        return response.choices[0].message.content



guardrail = BudgetGuardrail()

result = guardrail.call_llm(
    "Explain campaign conversion metrics"
)

print(result)

print("Total calls:", guardrail.total_calls)
print("Total tokens:", guardrail.total_tokens)
print("Total cost:", guardrail.total_cost)