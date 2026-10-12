# LLM Migration Report v10

Files still containing direct model constructors:

- api_copilotkit/agent.py
- src/llms/llm_legacy_backup.py
- src/mcp_retrieval/client.py
- src/llm/factory.py

These should be migrated after verifying constructor parameters.
