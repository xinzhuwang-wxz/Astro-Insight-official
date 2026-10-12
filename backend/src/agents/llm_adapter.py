from src.llm.factory import create_llm

def build_agent_llm(user_config=None):
    return create_llm(user_config)