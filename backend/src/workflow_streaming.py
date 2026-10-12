import json


def _json_default(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        try:
            return value.dict()
        except Exception:
            pass
    if hasattr(value, "content"):
        return {
            "type": value.__class__.__name__,
            "content": getattr(value, "content", ""),
        }
    return str(value)


async def stream_workflow_events(workflow, inputs):
    graph = workflow.graph if hasattr(workflow, "graph") else workflow

    async for event in graph.astream_events(inputs, version="v2"):
        yield (
            "data: "
            + json.dumps(
                {
                    "event": event.get("event"),
                    "name": event.get("name"),
                    "data": event.get("data", {}),
                },
                ensure_ascii=False,
                default=_json_default,
            )
            + "\n\n"
        )
