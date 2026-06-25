"""
Configuration module for DeepEval evaluation suite.

Provides Azure OpenAI gpt-5.4 configuration and a custom DeepEvalBaseLLM
wrapper so that all deepeval metrics use the same Azure deployment.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from deepeval.models import DeepEvalBaseLLM
from openai import AzureOpenAI

# ---------------------------------------------------------------------------
# Environment & paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DATASET_DIR = PROJECT_ROOT / "dataset"
TEST_GEPA_CSV = DATASET_DIR / "test_gepa.csv"

VALID_CATEGORIES = [
    "forum",
    "verify_code",
    "promotions",
    "social_media",
    "spam",
    "updates",
]

# ---------------------------------------------------------------------------
# Azure OpenAI settings (from .env)
# ---------------------------------------------------------------------------
AZURE_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4")


# ---------------------------------------------------------------------------
# Custom DeepEval model wrapper for Azure OpenAI gpt-5.4
# ---------------------------------------------------------------------------
class AzureGPT54Model(DeepEvalBaseLLM):
    """Wraps Azure OpenAI gpt-5.4 for use as the deepeval evaluation model."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment: Optional[str] = None,
    ):
        self._api_key = api_key or AZURE_API_KEY
        self._endpoint = endpoint or AZURE_ENDPOINT
        self._api_version = api_version or AZURE_API_VERSION
        self._deployment = deployment or AZURE_DEPLOYMENT

        self._client = AzureOpenAI(
            api_key=self._api_key,
            azure_endpoint=self._endpoint,
            api_version=self._api_version,
        )

    def load_model(self):
        """Return the underlying client (required by DeepEvalBaseLLM)."""
        return self._client

    def generate(self, prompt: str, schema=None) -> str:
        """Synchronous generation used by deepeval metrics."""
        client = self.load_model()

        response = client.chat.completions.create(
            model=self._deployment,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response.choices[0].message.content or ""

        # If a schema is provided, deepeval expects JSON parseable output.
        # We rely on the LLM to produce valid JSON when the prompt asks for it.
        if schema:
            import json
            try:
                json_obj = json.loads(content)
                return schema(**json_obj)
            except (json.JSONDecodeError, Exception):
                return content

        return content

    async def a_generate(self, prompt: str, schema=None) -> str:
        """Async generation — delegates to sync for simplicity."""
        return self.generate(prompt, schema)

    def get_model_name(self) -> str:
        return f"azure/{self._deployment}"
