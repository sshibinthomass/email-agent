from pydantic import BaseModel
from typing import Optional

class ClassificationResponse(BaseModel):
    subject: str
    body: str
    category: Optional[str]
    reason: Optional[str]
    JudgeVerted: Optional[str] = None
    JudgeReasoning: Optional[str] = None

