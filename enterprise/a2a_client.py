"""A2A SDK remote client with explicit typed message envelope."""
import os,uuid
import httpx
from a2a.client import A2AClient
from a2a.types import Message,Part,Role,TextPart,MessageSendParams,SendMessageRequest

A2A_URL=os.getenv("A2A_URL","http://a2a:8003/")

async def ask_risk_agent(prompt:str)->dict:
    async with httpx.AsyncClient(timeout=30.0) as http:
        client=A2AClient(httpx_client=http,url=A2A_URL)
        message=Message(role=Role.user,parts=[Part(root=TextPart(text=prompt))],message_id=str(uuid.uuid4()))
        request=SendMessageRequest(id=str(uuid.uuid4()),params=MessageSendParams(message=message))
        response=await client.send_message(request)
        return response.model_dump(mode="json")
