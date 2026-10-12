from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from src.llm import factory
from src.settings import llm_settings


class _FakeChatOpenAI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeChatAnthropic:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


@pytest.fixture(autouse=True)
def clean_llm_env(monkeypatch, tmp_path: Path):
    for key in (
        "LLM_PROVIDER",
        "LLM_API_FORMAT",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "LLM_API_KEY",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_BASE_URL",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(llm_settings, "CONFIG_FILE", tmp_path / "llm_settings.json")
    monkeypatch.setitem(
        sys.modules,
        "langchain_openai",
        types.SimpleNamespace(ChatOpenAI=_FakeChatOpenAI),
    )
    monkeypatch.setitem(
        sys.modules,
        "langchain_anthropic",
        types.SimpleNamespace(ChatAnthropic=_FakeChatAnthropic),
    )


def test_openai_compatible_protocol_uses_chat_openai():
    llm = factory.create_llm(
        {
            "provider": "deepseek",
            "api_format": "openai",
            "model": "deepseek-chat",
            "base_url": "https://api.deepseek.com/v1/",
            "api_key": "test-openai-key",
        }
    )
    assert isinstance(llm, _FakeChatOpenAI)
    assert llm.kwargs["base_url"] == "https://api.deepseek.com/v1"
    assert llm.kwargs["model"] == "deepseek-chat"


def test_anthropic_native_protocol_uses_chat_anthropic_and_normalizes_base_url():
    llm = factory.create_llm(
        {
            "provider": "claude",
            "api_format": "anthropic",
            "model": "claude-test",
            "base_url": "https://api.anthropic.com/v1",
            "api_key": "test-anthropic-key",
        }
    )
    assert isinstance(llm, _FakeChatAnthropic)
    assert llm.kwargs["base_url"] == "https://api.anthropic.com"
    assert llm.kwargs["model"] == "claude-test"
    assert llm.kwargs["max_tokens"] == 4096


def test_auto_infers_anthropic_from_provider():
    resolved = factory.resolve_llm_config(
        {
            "provider": "anthropic",
            "api_format": "auto",
            "model": "claude-test",
            "api_key": "x",
        }
    )
    assert resolved["api_format"] == "anthropic"


def test_saved_settings_are_used_by_agents_without_explicit_config():
    llm_settings.save_settings(
        {
            "provider": "custom-claude-gateway",
            "api_format": "anthropic",
            "model": "claude-gateway-model",
            "base_url": "https://gateway.example/anthropic",
            "api_key": "stored-key",
        }
    )
    resolved = factory.resolve_llm_config()
    assert resolved["api_format"] == "anthropic"
    assert resolved["model"] == "claude-gateway-model"
    assert resolved["api_key"] == "stored-key"


def test_invalid_api_format_is_rejected():
    with pytest.raises(ValueError, match="Unsupported LLM api_format"):
        factory.resolve_llm_config(
            {"api_format": "something-else", "model": "x", "api_key": "y"}
        )
