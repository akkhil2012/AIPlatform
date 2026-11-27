import os
from openai import OpenAI
from schemas import AgentAction

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    timeout=15,
    max_retries=1
)


def identify_action(agent, user_request):

    response = client.chat.completions.create(

        model=agent["model"],

        messages=[
            {
                "role": "system",
                "content": f"""
                You are {agent['name']}.

                Your role is {agent['role']}.

                Classify the user request into one action:

                read_campaign
                analyze_campaign
                approve_campaign
                reject_campaign
                unknown

                Return JSON containing action and reason.
                Use unknown for ambiguous requests.
                Do not execute any action.
                """
            },
            {
                "role": "user",
                "content": user_request
            }
        ],

        max_tokens=200,

        temperature=0,

        response_format={"type": "json_object"}
    )

    return AgentAction.model_validate_json(
        response.choices[0].message.content
    )