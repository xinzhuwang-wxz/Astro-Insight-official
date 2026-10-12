def normalize_agent_event(event):
    """
    Convert internal LangGraph events into frontend-friendly messages.
    """
    return {
        "type": event.get("event", "message"),
        "node": event.get("name", "agent"),
        "message": event.get("data", {})
    }