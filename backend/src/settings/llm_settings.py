from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

_DEFAULT_FILE = Path(__file__).resolve().parents[2] / "runtime" / "llm_settings.json"
CONFIG_FILE = Path(os.getenv("LLM_SETTINGS_FILE", str(_DEFAULT_FILE)))


def save_settings(data: Dict[str, Any]) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = CONFIG_FILE.with_suffix(CONFIG_FILE.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(CONFIG_FILE)
    try:
        CONFIG_FILE.chmod(0o600)
    except OSError:
        # Windows and some mounted filesystems may ignore POSIX permissions.
        pass


def load_settings() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def public_settings(data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    result = dict(data if data is not None else load_settings())
    api_key = str(result.get("api_key") or "")
    result["has_api_key"] = bool(api_key)
    # Never return a persisted secret back to the browser.
    result["api_key"] = ""
    return result
