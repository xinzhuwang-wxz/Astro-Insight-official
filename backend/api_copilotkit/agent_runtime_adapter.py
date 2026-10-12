from src.agents.provider_runtime import AgentRuntime


def get_user_configured_llm(config=None):
    """
    Single entry point for CopilotKit agent model creation.
    """
    return AgentRuntime(config).llm