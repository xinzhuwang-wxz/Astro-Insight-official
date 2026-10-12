"""LLM provider factory with OpenAI-compatible and Anthropic-native support.

The rest of the application calls :func:`create_llm` and does not need to know
which wire protocol is used. Runtime settings saved from the UI are merged with
environment variables; explicit function arguments always win.
"""
from __future__ import annotations

import os
from typing import Any, Dict

_OPENAI_FORMAT_ALIASES = {
    "openai",
    "openai-compatible",
    "openai_compatible",
    "chat-completions",
    "chat_completions",
}
_ANTHROPIC_FORMAT_ALIASES = {
    "anthropic",
    "anthropic-native",
    "anthropic_native",
    "messages",
    "anthropic-messages",
    "anthropic_messages",
}
_ANTHROPIC_PROVIDER_ALIASES = {"anthropic", "claude"}


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _load_saved_settings() -> Dict[str, Any]:
    try:
        from src.settings.llm_settings import load_settings

        data = load_settings()
        return data if isinstance(data, dict) else {}
    except Exception:
        # Settings are optional: environment-only deployments must still work.
        return {}


def _normalize_api_format(value: Any) -> str:
    normalized = _text(value).lower()
    if normalized in {"", "auto"}:
        return "auto"
    if normalized in _OPENAI_FORMAT_ALIASES:
        return "openai"
    if normalized in _ANTHROPIC_FORMAT_ALIASES:
        return "anthropic"
    raise ValueError(
        "Unsupported LLM api_format. Use 'auto', 'openai', or 'anthropic'."
    )


def _infer_api_format(provider: str, base_url: str, explicit: str) -> str:
    if explicit != "auto":
        return explicit

    p = provider.lower()
    url = base_url.lower()
    if p in _ANTHROPIC_PROVIDER_ALIASES:
        return "anthropic"
    if "anthropic" in url and "openai" not in url:
        return "anthropic"
    return "openai"


def _normalize_anthropic_base_url(base_url: str) -> str:
    """Return the SDK base URL, not the final ``/v1/messages`` endpoint.

    Anthropic SDKs append ``/v1/messages`` themselves. Users frequently paste
    ``https://api.anthropic.com/v1``; stripping that terminal ``/v1`` avoids a
    ``/v1/v1/messages`` request while preserving gateway prefixes such as
    ``https://gateway.example/anthropic``.
    """
    url = base_url.rstrip("/")
    lowered = url.lower()
    if lowered.endswith("/v1/messages"):
        return url[: -len("/v1/messages")]
    if lowered.endswith("/v1"):
        return url[:-3]
    return url


def resolve_llm_config(config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Resolve effective LLM configuration without creating a network client."""
    explicit = config or {}
    saved = _load_saved_settings()

    provider = _text(
        explicit.get("provider")
        or saved.get("provider")
        or os.getenv("LLM_PROVIDER")
        or "openai"
    ).lower()

    # General base/key env vars take precedence over protocol-specific legacy vars.
    base_url = _text(
        explicit.get("base_url")
        or saved.get("base_url")
        or os.getenv("LLM_BASE_URL")
    )
    api_key = _text(
        explicit.get("api_key")
        or saved.get("api_key")
        or os.getenv("LLM_API_KEY")
    )

    api_format = _normalize_api_format(
        explicit.get("api_format")
        or explicit.get("protocol")
        or saved.get("api_format")
        or saved.get("protocol")
        or os.getenv("LLM_API_FORMAT")
        or "auto"
    )

    if not base_url:
        if provider in _ANTHROPIC_PROVIDER_ALIASES or api_format == "anthropic":
            base_url = _text(
                os.getenv("ANTHROPIC_BASE_URL") or os.getenv("ANTHROPIC_API_URL")
            )
        else:
            base_url = _text(os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE"))

    effective_format = _infer_api_format(provider, base_url, api_format)

    if not api_key:
        if effective_format == "anthropic":
            api_key = _text(os.getenv("ANTHROPIC_API_KEY"))
        else:
            provider_key_map = {
                "deepseek": "DEEPSEEK_API_KEY",
                "openrouter": "OPENROUTER_API_KEY",
                "doubao": "DOUBAO_API_KEY",
                "qwen": "DASHSCOPE_API_KEY",
                "dashscope": "DASHSCOPE_API_KEY",
            }
            api_key = _text(
                os.getenv(provider_key_map.get(provider, "OPENAI_API_KEY"))
            )
            if not api_key and provider == "ollama":
                api_key = "ollama"

    default_model = (
        "claude-sonnet-4-5" if effective_format == "anthropic" else "gpt-4o-mini"
    )
    protocol_model_env = (
        os.getenv("ANTHROPIC_MODEL")
        if effective_format == "anthropic"
        else os.getenv("OPENAI_MODEL")
    )
    model = _text(
        explicit.get("model")
        or saved.get("model")
        or os.getenv("LLM_MODEL")
        or protocol_model_env
        or default_model
    )

    temperature_raw = (
        explicit.get("temperature")
        if explicit.get("temperature") is not None
        else saved.get("temperature")
    )
    if temperature_raw is None:
        temperature_raw = os.getenv("LLM_TEMPERATURE", "0.2")

    timeout_raw = explicit.get("timeout") or saved.get("timeout") or os.getenv("LLM_TIMEOUT", "120")
    retries_raw = explicit.get("max_retries") or saved.get("max_retries") or os.getenv("LLM_MAX_RETRIES", "2")
    max_tokens_raw = explicit.get("max_tokens") or saved.get("max_tokens") or os.getenv("LLM_MAX_TOKENS", "4096")

    return {
        "provider": provider,
        "api_format": effective_format,
        "model": model,
        "base_url": base_url,
        "api_key": api_key,
        "temperature": float(temperature_raw),
        "timeout": float(timeout_raw),
        "max_retries": int(retries_raw),
        "max_tokens": int(max_tokens_raw),
    }


def create_llm(config: Dict[str, Any] | None = None):
    """Create a LangChain chat model for the configured wire protocol.

    ``api_format='openai'`` means OpenAI Chat-Completions-compatible HTTP APIs
    (OpenAI, DeepSeek, Doubao/Ark, Ollama-compatible gateways, etc.).
    ``api_format='anthropic'`` means native Anthropic Messages-compatible APIs.
    """
    resolved = resolve_llm_config(config)

    try:
        if resolved["api_format"] == "anthropic":
            from langchain_anthropic import ChatAnthropic

            kwargs: Dict[str, Any] = {
                "model": resolved["model"],
                "api_key": resolved["api_key"],
                "temperature": resolved["temperature"],
                "timeout": resolved["timeout"],
                "max_retries": resolved["max_retries"],
                "max_tokens": resolved["max_tokens"],
            }
            if resolved["base_url"]:
                kwargs["base_url"] = _normalize_anthropic_base_url(
                    resolved["base_url"]
                )
            return ChatAnthropic(**kwargs)

        from langchain_openai import ChatOpenAI

        kwargs = {
            "model": resolved["model"],
            "api_key": resolved["api_key"],
            "temperature": resolved["temperature"],
            "timeout": resolved["timeout"],
            "max_retries": resolved["max_retries"],
        }
        if resolved["base_url"]:
            kwargs["base_url"] = resolved["base_url"].rstrip("/")
        return ChatOpenAI(**kwargs)
    except ImportError as exc:
        package = (
            "langchain-anthropic"
            if resolved["api_format"] == "anthropic"
            else "langchain-openai"
        )
        raise RuntimeError(
            f"LLM api_format={resolved['api_format']} requires package {package}."
        ) from exc
    except Exception as exc:
        raise RuntimeError(
            "Unable to initialize LLM "
            f"provider={resolved['provider']} api_format={resolved['api_format']}: {exc}"
        ) from exc
