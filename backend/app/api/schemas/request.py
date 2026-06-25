from pydantic import BaseModel, Field
from typing import Optional

class ClassificationRequest(BaseModel):
    subject: str = Field(..., description="The subject line of the email")
    body: str = Field(..., description="The body content of the email")
    provider: str = Field(
        default="openai",
        description="The LLM provider to use (openai, groq, ollama, gemini, anthropic)",
    )
    selected_llm: Optional[str] = Field(
        default=None,
        description="The specific LLM model name to use. If not specified, a provider default will be selected.",
    )
    thread_id: str = Field(
        default="default-api-thread",
        description="The conversation thread ID for LangGraph memory saver state tracking",
    )

