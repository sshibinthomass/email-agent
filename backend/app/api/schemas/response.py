from pydantic import BaseModel
from typing import Optional

class ClassificationResponse(BaseModel):
    subject: str
    body: str
    category: Optional[str]
    confidence: Optional[float]
    reason: Optional[str]
