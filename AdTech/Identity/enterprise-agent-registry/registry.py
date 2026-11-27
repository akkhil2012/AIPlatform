from database import SessionLocal
from models import Agent
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class AgentRegistry:

    def register(self, registration):

        with SessionLocal() as db:

            agent = Agent(**registration.model_dump())

            db.add(agent)

            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                raise HTTPException(
                    409, "Agent already exists"
                )

            return {"agent_id": agent.agent_id,
                    "status": "REGISTERED"}


    def resolve(self, agent_id, tenant_id):

        with SessionLocal() as db:

            agent = db.query(Agent).filter_by(
                agent_id=agent_id,
                tenant_id=tenant_id
            ).first()

            if not agent:
                raise HTTPException(404, "Agent not found")

            if agent.status != "ACTIVE":
                raise HTTPException(403, "Agent inactive")

            return {
                column.name: getattr(agent, column.name)
                for column in Agent.__table__.columns
            }


    def discover(self, tenant_id, capability):

        with SessionLocal() as db:

            agents = db.query(Agent).filter_by(
                tenant_id=tenant_id,
                status="ACTIVE"
            ).all()

            return [
                {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "version": agent.version
                }
                for agent in agents
                if capability in agent.capabilities
            ]


    def deactivate(self, agent_id, tenant_id):

        with SessionLocal() as db:

            agent = db.query(Agent).filter_by(
                agent_id=agent_id,
                tenant_id=tenant_id
            ).first()

            if not agent:
                raise HTTPException(404, "Agent not found")

            agent.status = "INACTIVE"
            agent.version += 1

            db.commit()

            return {"status": "INACTIVE"}