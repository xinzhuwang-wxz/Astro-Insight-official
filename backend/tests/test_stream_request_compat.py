from api_service.stream_routes import extract_query


def test_native_query_body():
    assert extract_query({"query": "hello"}) == "hello"


def test_openai_style_messages_body():
    payload = {
        "messages": [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "latest user question"},
        ]
    }
    assert extract_query(payload) == "latest user question"


def test_anthropic_style_content_blocks():
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "first"},
                    {"type": "text", "text": "second"},
                ],
            }
        ]
    }
    assert extract_query(payload) == "first\nsecond"


def test_copilot_nested_input_body():
    assert extract_query({"input": {"query": "nested"}}) == "nested"

from fastapi import FastAPI
from fastapi.testclient import TestClient
from api_service import stream_routes


class _FakeWorkflowService:
    def __init__(self):
        self.last_payload = None

    async def stream(self, payload):
        self.last_payload = payload
        yield 'data: {"event":"done","data":{"ok":true}}\n\n'


def test_stream_route_accepts_openai_messages(monkeypatch):
    fake = _FakeWorkflowService()
    monkeypatch.setattr(stream_routes, "_service", fake)
    app = FastAPI()
    app.include_router(stream_routes.router)
    with TestClient(app) as client:
        response = client.post(
            "/query/stream",
            json={
                "messages": [
                    {"role": "user", "content": "stream this"}
                ],
                "threadId": "thread-1",
            },
        )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert '"event":"done"' in response.text
    assert fake.last_payload["query"] == "stream this"
    assert fake.last_payload["session_id"] == "thread-1"
