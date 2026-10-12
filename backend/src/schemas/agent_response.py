from pydantic import BaseModel
from typing import Any, Optional

class AgentEvent(BaseModel):
    type: str
    node: str
    message: Optional[str] = None
    data: Optional[Any] = None