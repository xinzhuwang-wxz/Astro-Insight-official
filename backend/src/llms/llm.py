def get_llm_by_type(llm_type="basic", user_config=None):
    """Compatibility wrapper.

    Existing agents can keep calling get_llm_by_type while
    internally using the new user-configurable LLM runtime.
    """
    # Imported lazily: src.agents pulls in src.llms.llm (via agents.py), so a
    # module-level import here makes the two packages circular. Keeping this
    # module free of top-level imports lets any import order succeed.
    from src.agents.provider_runtime import AgentRuntime

    return AgentRuntime(user_config).llm


def get_configured_llm_models():
    """Compatibility wrapper around the legacy YAML-based model listing."""
    from src.llms.llm_legacy_backup import (
        get_configured_llm_models as _legacy_get_configured_llm_models,
    )

    return _legacy_get_configured_llm_models()
