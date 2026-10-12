from src.agents.provider_runtime import AgentRuntime

def get_explanation_llm(config=None):
    return AgentRuntime(config).llm