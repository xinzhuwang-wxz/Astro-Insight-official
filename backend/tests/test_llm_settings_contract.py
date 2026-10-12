from pathlib import Path

from api_service import llm_routes
from src.settings import llm_settings


def test_save_masks_secret_and_keeps_protocol(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(llm_settings, "CONFIG_FILE", tmp_path / "llm_settings.json")

    payload = llm_routes.LLMSettings(
        provider="claude",
        api_format="anthropic",
        model="claude-test",
        base_url="https://api.anthropic.com",
        api_key="super-secret",
    )
    result = llm_routes.set_llm_settings(payload)
    assert result["success"] is True
    assert result["resolved"]["api_format"] == "anthropic"
    assert result["settings"]["api_key"] == ""
    assert result["settings"]["has_api_key"] is True
    assert llm_settings.load_settings()["api_key"] == "super-secret"


def test_blank_key_preserves_existing_key(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(llm_settings, "CONFIG_FILE", tmp_path / "llm_settings.json")
    llm_settings.save_settings(
        {
            "provider": "openai",
            "api_format": "openai",
            "model": "gpt-test",
            "api_key": "existing-key",
        }
    )
    llm_routes.set_llm_settings(
        llm_routes.LLMSettings(
            provider="openai",
            api_format="openai",
            model="gpt-test-2",
            api_key="",
        )
    )
    assert llm_settings.load_settings()["api_key"] == "existing-key"
