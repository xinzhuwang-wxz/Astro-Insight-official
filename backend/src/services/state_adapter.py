from typing import Any, Dict

def build_workflow_input(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "query": payload.get("query", ""),
        "session_id": payload.get("session_id"),
        "user_type": payload.get("user_type", "professional"),
    }