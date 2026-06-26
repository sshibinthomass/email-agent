from unittest.mock import patch, MagicMock
import pytest
from backend.app.agent.llms import openai_llm, groq_llm, gemini_llm, anthropic_llm, ollama_llm, azure_llm
from backend.app.agent.llms.factory import try_build_provider_llm, build_llm_with_fallbacks


def test_try_build_provider_llm_openai():
    with patch("backend.app.agent.llms.openai_llm.ChatOpenAI") as mock_chat:
        llm = try_build_provider_llm("openai")
        assert llm is not None
        mock_chat.assert_called_once()


def test_try_build_provider_llm_groq():
    with patch("backend.app.agent.llms.groq_llm.ChatGroq") as mock_chat:
        llm = try_build_provider_llm("groq")
        assert llm is not None
        mock_chat.assert_called_once()


def test_try_build_provider_llm_gemini():
    with patch("backend.app.agent.llms.gemini_llm.ChatGoogleGenerativeAI") as mock_chat:
        llm = try_build_provider_llm("gemini")
        assert llm is not None
        mock_chat.assert_called_once()


def test_try_build_provider_llm_anthropic():
    with patch("backend.app.agent.llms.anthropic_llm.ChatAnthropic") as mock_chat:
        llm = try_build_provider_llm("anthropic")
        assert llm is not None
        mock_chat.assert_called_once()


def test_try_build_provider_llm_ollama():
    with patch("backend.app.agent.llms.ollama_llm.ChatOllama") as mock_chat:
        llm = try_build_provider_llm("ollama")
        assert llm is not None
        mock_chat.assert_called_once()


def test_try_build_provider_llm_azure():
    with patch("backend.app.agent.llms.azure_llm.AzureChatOpenAI") as mock_chat:
        llm = try_build_provider_llm("azure")
        assert llm is not None
        mock_chat.assert_called_once()


def test_try_build_provider_llm_unsupported():
    llm = try_build_provider_llm("invalid-provider")
    assert llm is None


def test_build_llm_with_fallbacks():
    with patch("backend.app.agent.llms.factory.try_build_provider_llm") as mock_try:
        mock_primary = MagicMock()
        mock_fallback_1 = MagicMock()
        mock_fallback_2 = MagicMock()

        mock_try.side_effect = lambda provider, selected_llm=None: {
            "openai": mock_primary,
            "anthropic": mock_fallback_1,
            "gemini": mock_fallback_2,
        }.get(provider, None)

        res = build_llm_with_fallbacks("openai")

        assert res is not None
        mock_primary.with_fallbacks.assert_called_once_with([mock_fallback_1, mock_fallback_2])


def test_build_llm_with_fallbacks_no_providers():
    with patch("backend.app.agent.llms.factory.try_build_provider_llm", return_value=None):
        with pytest.raises(ValueError, match="No LLM providers available"):
            build_llm_with_fallbacks("openai")
