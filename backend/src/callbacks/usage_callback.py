from langchain_core.callbacks import BaseCallbackHandler
from src.usage.tracker import record

class UsageCallback(BaseCallbackHandler):
    def __init__(self, model="unknown"):
        self.model = model

    def on_llm_end(self, response, **kwargs):
        output = getattr(response, "llm_output", {}) or {}
        usage = output.get("token_usage", {})
        record(
            model=self.model,
            tokens=usage.get("total_tokens", 0)
        )