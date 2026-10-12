# Agent LLM migration

Replace:

ChatOpenAI(...)

with:

from src.agents.llm_adapter import build_agent_llm

llm = build_agent_llm(user_config)

This enables frontend-selected LLM providers.