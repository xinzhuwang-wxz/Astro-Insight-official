from src.workflow_streaming import stream_workflow_events
from src.services.workflow_factory import create_workflow
from src.services.state_adapter import build_workflow_input


class WorkflowService:
    def __init__(self, workflow=None):
        self.workflow = workflow or create_workflow()

    async def stream(self, payload):
        graph_input = build_workflow_input(payload)

        async for event in stream_workflow_events(
            self.workflow,
            graph_input
        ):
            yield event