"""Official MCP SDK streamable-HTTP client, invoked from authenticated API."""
import os
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL=os.getenv("MCP_URL","http://mcp:8002/mcp")

async def search_knowledge(access_token:str,query:str):
    async with streamablehttp_client(MCP_URL) as (read,write,_):
        async with ClientSession(read,write) as session:
            await session.initialize()
            response=await session.call_tool("search_campaign_knowledge",arguments={"delegation_token":access_token,"query":query,"limit":3})
            if response.isError: raise RuntimeError("MCP tool returned error")
            return [getattr(part,"text",str(part)) for part in response.content]
