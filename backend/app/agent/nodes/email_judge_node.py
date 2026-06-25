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
from backend.app.agent.prompts import EMAIL_JUDGE_PROMPT
from backend.app.agent.llms.azure_llm import AzureLLM
from pydantic import BaseModel, Field
import json

load_dotenv()

# Azure judge LLM — same deployment and credentials as gepa_training_judge/optimize_prompt.py
AZURE_JUDGE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4")
AZURE_JUDGE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")


def _create_judge_llm():
    """Build the Azure OpenAI gpt-5.4 LLM used exclusively by the email judge."""
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not azure_api_key or not azure_endpoint:
        raise ValueError(
            "AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set for the email judge."
        )
    azure_controls = {
        "AZURE_OPENAI_API_KEY": azure_api_key,
        "AZURE_OPENAI_ENDPOINT": azure_endpoint,
        "AZURE_OPENAI_API_VERSION": AZURE_JUDGE_API_VERSION,
        "selected_llm": AZURE_JUDGE_DEPLOYMENT,
    }
    return AzureLLM(azure_controls).get_base_llm()


class EmailJudgeDecision(BaseModel):
    """Schema for the email judge output."""
    accepted: bool = Field(
        description="Whether the proposed category is a reasonable fit for the email (true or false)."
    )
    reason: str = Field(
        description="A brief explanation of why the category fits or why there is a mismatch."
    )


class EmailJudgeNode:
    """
    Email Judge node implementation.
    Evaluates whether the classified category fits the email content.
    """

    def __init__(self):
        judge_llm = _create_judge_llm()
        self.llm = judge_llm.with_structured_output(EmailJudgeDecision)


    def process(self, state: AgentState) -> dict:
        """
        Processes the input state, evaluates the classification using LLM,
        and returns the judge results (JudgeVerted and JudgeReasoning) to update AgentState.
        """
        subject = state.get("subject", "")
        body = state.get("body", "")
        proposed_category = state.get("category", "")

        prompt = EMAIL_JUDGE_PROMPT.format(
            subject=subject,
            body=body,
            proposed_category=proposed_category
        )

        try:
            result = self.llm.invoke(prompt)
            verted = "accept" if result.accepted else "reject"
            return {
                "JudgeVerted": verted,
                "JudgeReasoning": result.reason
            }
        except Exception as e:
            return {
                "JudgeVerted": "reject",
                "JudgeReasoning": f"Error during judge validation: {str(e)}"
            }


if __name__ == "__main__":
    node = EmailJudgeNode()

    # State with sample email and category
    state: AgentState = {
        "subject": """Your post was moved to "Programming Help""",
        "body": """Trending: "cooking" (258 comments). View: support.site/ticket/456.""",
        "category": "updates",
        "reason": "Exclusive discount offer for loyal customers.",
        "JudgeVerted": None,
        "JudgeReasoning": None,
    }

    # Call the process method and print the result
    result = node.process(state)
    print("Email Judge Node Result:")
    print(json.dumps(result, indent=2))
