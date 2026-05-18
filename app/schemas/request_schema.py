from pydantic import BaseModel
from typing import List, Optional

class TextRequest(BaseModel):
    text: str
    webhook_url: Optional[str] = None

class BatchTextRequest(BaseModel):
    texts: List[str]
    webhook_url: Optional[str] = None
