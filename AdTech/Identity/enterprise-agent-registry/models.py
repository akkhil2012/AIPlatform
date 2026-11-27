from sqlalchemy import Column, String, JSON, Integer
from database import Base


class Agent(Base):

    __tablename__ = "agents"

    agent_id = Column(String(100), primary_key=True)

    name = Column(String(200), nullable=False)

    version = Column(Integer, default=1, nullable=False)

    tenant_id = Column(String(100), nullable=False)

    role = Column(String(100), nullable=False)

    model = Column(String(100), nullable=False)

    status = Column(String(20), default="ACTIVE")

    allowed_actions = Column(JSON, nullable=False)

    capabilities = Column(JSON, nullable=False)