import json

async def langgraph_event_stream(workflow, inputs):
    """
    Adapter between LangGraph astream_events and FastAPI SSE.

    Replace invoke() with workflow.astream_events(inputs, version="v2").
    """
    async for event in workflow.astream_events(inputs, version="v2"):
        yield (
            "data: "
            + json.dumps({
                "event": event.get("event"),
                "node": event.get("name", "workflow")
            })
            + "\n\n"
        )