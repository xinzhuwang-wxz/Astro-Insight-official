from fastapi.responses import StreamingResponse
from src.streaming_adapter import langgraph_event_stream

def create_copilot_stream(workflow, payload):
    return StreamingResponse(
        langgraph_event_stream(workflow, payload),
        media_type="text/event-stream"
    )