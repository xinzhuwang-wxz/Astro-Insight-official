from api_service.copilot_stream_adapter import create_copilot_stream

class AstroCopilotRuntime:
    def __init__(self, workflow):
        self.workflow = workflow

    def stream(self, payload):
        return create_copilot_stream(self.workflow, payload)