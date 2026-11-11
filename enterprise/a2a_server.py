"""Remote A2A specialist built with the official a2a-sdk.

Runs on a private service network. The API gateway is the authenticated entry
point; do not publish this internal agent directly to the Internet.
"""
import os
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication
from a2a.types import AgentCard,AgentCapabilities,AgentSkill
from a2a.utils import new_agent_text_message
import uvicorn

class RiskSpecialist(AgentExecutor):
    async def execute(self,context:RequestContext,event_queue:EventQueue)->None:
        # Only synthetic, aggregate-only information is returned.
        await event_queue.enqueue_event(new_agent_text_message(
            "Risk specialist (remote A2A): aggregate application decisions: "
            "120 applications, 80 approved, 25 declined, 15 pending. "
            "No individual customer information is accessible."
        ))
    async def cancel(self,context:RequestContext,event_queue:EventQueue)->None:
        raise NotImplementedError("Cancellation is not supported by this read-only demo")

def build_app():
    url=os.getenv("A2A_PUBLIC_URL","http://a2a:8003/")
    card=AgentCard(
        name="Aggregate Risk Specialist",description="Remote read-only synthetic decision funnel specialist",
        url=url,version="0.1.0",default_input_modes=["text"],default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[AgentSkill(id="risk-summary",name="Risk summary",description="Return aggregate application funnel data",tags=["risk","aggregate"])]
    )
    handler=DefaultRequestHandler(agent_executor=RiskSpecialist(),task_store=InMemoryTaskStore())
    return A2AStarletteApplication(agent_card=card,http_handler=handler).build()

app=build_app()
if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=8003)
