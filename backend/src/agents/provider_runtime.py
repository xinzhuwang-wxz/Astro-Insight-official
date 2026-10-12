from src.agents.llm_adapter import build_agent_llm

class AgentRuntime:
    """
    Shared runtime used by planner/retriever/coder/explainer agents.
    """

    def __init__(self, user_llm_config=None):
        self.llm = build_agent_llm(user_llm_config)

    def invoke(self, messages):
        return self.llm.invoke(messages)