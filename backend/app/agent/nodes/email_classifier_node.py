import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
current_file = Path(__file__).resolve()
project_root = current_file.parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.agent.state import AgentState
from backend.app.agent.prompts import EMAIL_CLASSIFIER_PROMPT
from pydantic import BaseModel, Field
from typing import Literal
import json

load_dotenv()


class EmailCategory(BaseModel):
    """Schema for the email classifier output."""
    category: Literal["forum", "verify_code", "promotions", "social_media", "spam", "updates"] = Field(
        description="The category of the email."
    )
    reason: str = Field(
        description="A brief one-sentence reason for this classification."
    )


class EmailClassifierNode:
    """
    Email Classifier node implementation.
    Classifies incoming emails into specific folders/categories based on subject and body.
    """

    def __init__(self, model):
        self.llm = model.with_structured_output(EmailCategory)

    def process(self, state: AgentState) -> dict:
        """
        Processes the input state, classifies the email using LLM,
        and returns the classification results to update AgentState.
        """
        subject = state.get("subject", "")
        body = state.get("body", "")

        prompt = EMAIL_CLASSIFIER_PROMPT.format(subject=subject, body=body)

        try:
            result = self.llm.invoke(prompt)
            return {
                "category": result.category,
                "reason": result.reason
            }
        except Exception as e:
            return {
                "category": "Unknown",
                "reason": f"Error during structured classification: {str(e)}"
            }


if __name__ == "__main__":
    # Create LLM instance
    from backend.app.agent.llms.groq_llm import GroqLLM

    user_controls_input = {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "selected_llm": "llama-3.3-70b-versatile",
    }
    llm = GroqLLM(user_controls_input)
    llm = llm.get_base_llm()

    # Create Email classifier instance with the LLM
    node = EmailClassifierNode(llm)

    # State with the specified input email
    state: AgentState = {
        "subject": "Anniversary Special: Buy one get one free",
        "body": "As our loyal customer, get exclusive $60 off $75+: example.com/6058 Offer code: WELCOME20.",
        "category": None,
        "reason": None,
    }

    # Call the process method and print the result
    result = node.process(state)
    print("Email Classifier Node Result:")
    print(json.dumps(result, indent=2))
