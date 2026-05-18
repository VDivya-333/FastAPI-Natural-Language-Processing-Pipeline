from pydantic import BaseModel
from typing import Any, List, Optional


class NLPResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None

class BatchNLPResponse(BaseModel):
    task_id: str
    status: str
    results: Optional[List[Any]] = None
    total_processed: int

class RagRetrieveRequest(BaseModel):
    query: str
    top_k: int = 3

class RagDocument(BaseModel):
    doc_id: str
    text: str
    score: float

class RagRetrieveResponse(BaseModel):
    query: str
    results: List[RagDocument]