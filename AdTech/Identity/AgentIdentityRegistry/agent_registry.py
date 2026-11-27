import yaml


class AgentRegistry:
    def __init__(self, filepath):
        with open(filepath, encoding="utf-8") as file:
            self.config = yaml.safe_load(file) or {}

    def get_agent(self, agent_id):
        agents = self.config.get("agents", {})
        if agent_id not in agents:
            raise KeyError(f"Unknown agent: {agent_id}")

        agent = agents[agent_id]
        if agent["status"].upper() != "ACTIVE":
            raise PermissionError("Agent is not active")
        return agent

    def authorize_agent(self, agent_id, action):
        agent = self.get_agent(agent_id)
        if action not in agent.get("allowed_actions", []):
            raise PermissionError("Agent does not have permission for this action")
        return True

    def authorize(self, agent_id, action):
        return self.authorize_agent(agent_id, action)

    def list_agents(self):
        return list(self.config.get("agents", {}).keys())