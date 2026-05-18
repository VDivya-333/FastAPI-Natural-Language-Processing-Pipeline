from pydantic import BaseModel
from typing import Any, Optional

class NLPResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None

class BatchNLPResponse(BaseModel):
    task_id: str
    status: str
    total_processed: int
