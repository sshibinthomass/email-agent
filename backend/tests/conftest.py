import os
import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock

# Mock langchain libraries that may not be installed in the env to prevent collection errors
sys.modules["langchain_google_genai"] = MagicMock()
sys.modules["langchain_anthropic"] = MagicMock()

# Add project root to sys.path to resolve backend imports
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session", autouse=True)
def mock_env_vars():
    """Mock API keys and endpoints in the environment to avoid real LLM calls."""
    os.environ["OPENAI_API_KEY"] = "mock-openai-key"
    os.environ["GROQ_API_KEY"] = "mock-groq-key"
    os.environ["GEMINI_API_KEY"] = "mock-gemini-key"
    os.environ["ANTHROPIC_API_KEY"] = "mock-anthropic-key"
    os.environ["AZURE_OPENAI_API_KEY"] = "mock-azure-key"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://mock-azure-endpoint.openai.azure.com/"
    os.environ["AZURE_OPENAI_API_VERSION"] = "2025-01-01-preview"
    os.environ["AZURE_OPENAI_DEPLOYMENT"] = "gpt-5.4"
    yield
