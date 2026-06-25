import os
import sys

import dotenv
from langchain_openai import AzureChatOpenAI

dotenv.load_dotenv()


class AzureLLM:
    def __init__(self, user_controls_input):
        self.user_controls_input = user_controls_input

    def get_base_llm(self):
        """Return the base AzureChatOpenAI LLM instance"""
        azure_api_key = (
            self.user_controls_input.get("AZURE_OPENAI_API_KEY")
            or self.user_controls_input.get("OPENAI_API_KEY")
            or os.getenv("AZURE_OPENAI_API_KEY")
            or os.getenv("OPENAI_API_KEY", "")
        )
        azure_endpoint = (
            self.user_controls_input.get("AZURE_OPENAI_ENDPOINT")
            or self.user_controls_input.get("OPENAI_BASE_URL")
            or os.getenv("AZURE_OPENAI_ENDPOINT")
            or os.getenv("OPENAI_BASE_URL", "")
        )
        api_version = (
            self.user_controls_input.get("AZURE_OPENAI_API_VERSION")
            or self.user_controls_input.get("OPENAI_API_VERSION")
            or os.getenv("AZURE_OPENAI_API_VERSION")
            or os.getenv("OPENAI_API_VERSION", "2024-02-15-preview")
        )
        selected_deployment = self.user_controls_input.get("selected_llm") or "gpt-4o-mini"

        return AzureChatOpenAI(
            azure_deployment=selected_deployment,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
        )


if __name__ == "__main__":
    # Example user_controls_input
    user_controls_input = {
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", ""),
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("OPENAI_BASE_URL", ""),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION") or os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        "selected_llm": "gpt-4o-mini",
    }

    azure_llm = AzureLLM(user_controls_input)
    llm = azure_llm.get_base_llm()
    if llm:
        prompt = "What is the capital of Germany?"
        try:
            response = llm.invoke(prompt)
            print("Response:", response)
        except Exception as e:
            print("Error during invocation:", e)
            sys.exit(1)
    else:
        print("LLM could not be initialized.")
        sys.exit(1)
