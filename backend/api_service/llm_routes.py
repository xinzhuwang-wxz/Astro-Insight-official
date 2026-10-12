from __future__ import annotations

import importlib.util
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.llm.factory import create_llm, resolve_llm_config
from src.settings.llm_settings import load_settings, public_settings, save_settings
from src.usage.tracker import summary

router = APIRouter()


class LLMSettings(BaseModel):
    provider: str = "openai"
    api_format: str = Field(default="auto", description="auto | openai | anthropic")
    model: str
    base_url: str = ""
    api_key: str = ""
    temperature: Optional[float] = None
    timeout: Optional[float] = None
    max_retries: Optional[int] = None
    max_tokens: Optional[int] = None


@router.get("/api/settings/llm")
def get_llm_settings():
    return public_settings()


@router.post("/api/settings/llm")
def set_llm_settings(data: LLMSettings):
    current = load_settings()
    payload = data.model_dump(exclude_none=True)

    # Blank key means "keep the existing stored key" rather than deleting it.
    if not payload.get("api_key") and current.get("api_key"):
        payload["api_key"] = current["api_key"]

    try:
        resolved = resolve_llm_config(payload)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Persist the normalized protocol, while preserving user-facing provider/model.
    payload["api_format"] = resolved["api_format"]
    save_settings(payload)
    return {
        "success": True,
        "settings": public_settings(payload),
        "resolved": {
            "provider": resolved["provider"],
            "api_format": resolved["api_format"],
            "model": resolved["model"],
            "base_url": resolved["base_url"],
        },
    }


@router.post("/api/settings/llm/validate")
def validate_llm_settings(data: LLMSettings):
    """Validate protocol selection without sending any request to an LLM API."""
    try:
        resolved = resolve_llm_config(data.model_dump(exclude_none=True))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    package = (
        "langchain_anthropic"
        if resolved["api_format"] == "anthropic"
        else "langchain_openai"
    )
    return {
        "valid": True,
        "provider": resolved["provider"],
        "api_format": resolved["api_format"],
        "model": resolved["model"],
        "base_url": resolved["base_url"],
        "has_api_key": bool(resolved["api_key"]),
        "runtime_dependency": package,
        "runtime_dependency_installed": importlib.util.find_spec(package) is not None,
    }


@router.post("/api/settings/llm/test")
def test_saved_llm_connection():
    """Make one minimal real model request using the saved settings.

    This endpoint is intentionally separate from validation so no API request is
    made until the user explicitly asks for a connectivity test.
    """
    resolved = resolve_llm_config()
    if not resolved.get("api_key") and resolved.get("provider") != "ollama":
        raise HTTPException(status_code=422, detail="No API key is configured.")
    try:
        llm = create_llm()
        response = llm.invoke("Reply with exactly: OK")
        content = getattr(response, "content", response)
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, str):
                    text_parts.append(block)
                elif isinstance(block, dict) and isinstance(block.get("text"), str):
                    text_parts.append(block["text"])
            content = "".join(text_parts)
        return {
            "success": True,
            "provider": resolved["provider"],
            "api_format": resolved["api_format"],
            "model": resolved["model"],
            "response": str(content)[:500],
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/api/usage")
def get_usage():
    return summary()
