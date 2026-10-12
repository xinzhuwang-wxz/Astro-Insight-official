from __future__ import annotations

import json
import uuid
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.services.workflow_service import WorkflowService

router = APIRouter()

_service = None


def get_workflow_service():
    global _service
    if _service is None:
        _service = WorkflowService()
    return _service


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text") or block.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(x for x in parts if x).strip()
    if isinstance(content, dict):
        return _content_to_text(content.get("text") or content.get("content"))
    return ""


def extract_query(payload: Dict[str, Any]) -> str:
    """Accept Astro-native, OpenAI-like, and CopilotKit-like request bodies."""
    for key in ("query", "prompt", "message"):
        value = _content_to_text(payload.get(key))
        if value:
            return value

    input_value = payload.get("input")
    if isinstance(input_value, str) and input_value.strip():
        return input_value.strip()
    if isinstance(input_value, dict):
        nested = extract_query(input_value)
        if nested:
            return nested

    messages = payload.get("messages")
    if isinstance(messages, list):
        # Prefer the latest user message; fall back to the latest textual message.
        textual = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            text = _content_to_text(msg.get("content"))
            if text:
                textual.append((str(msg.get("role") or "").lower(), text))
        for role, text in reversed(textual):
            if role in {"user", "human"}:
                return text
        if textual:
            return textual[-1][1]

    return ""


@router.post("/query/stream")
async def query_stream(payload: Dict[str, Any]):
    query = extract_query(payload)
    if not query:
        raise HTTPException(
            status_code=422,
            detail="No user query found. Send 'query' or a messages[] payload.",
        )

    session_id = payload.get("session_id") or payload.get("threadId") or str(uuid.uuid4())
    service = get_workflow_service()

    async def event_generator():
        try:
            async for event in service.stream(
                {
                    "query": query,
                    "session_id": session_id,
                    "user_type": payload.get("user_type", "professional"),
                }
            ):
                yield event
        except Exception as exc:
            yield (
                "event: error\n"
                "data: "
                + json.dumps(
                    {"event": "error", "message": str(exc)}, ensure_ascii=False
                )
                + "\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
