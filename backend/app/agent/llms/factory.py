import logging
import os

from backend.app.agent.config import DEFAULT_MODELS, FALLBACK_PROVIDER_ORDER

logger = logging.getLogger(__name__)


def try_build_provider_llm(provider: str, selected_llm: str | None = None):
    """Return a base LLM for the provider, or None if it cannot be initialized."""
    provider_lower = provider.lower()
    model_name = selected_llm or DEFAULT_MODELS.get(provider_lower)
    if not model_name:
        return None

    try:
        if provider_lower == "openai":
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                return None
            from backend.app.agent.llms.openai_llm import OpenAILLM

            return OpenAILLM(
                {"OPENAI_API_KEY": api_key, "selected_llm": model_name}
            ).get_base_llm()

        if provider_lower == "groq":
            api_key = os.getenv("GROQ_API_KEY", "")
            if not api_key:
                return None
            from backend.app.agent.llms.groq_llm import GroqLLM

            return GroqLLM(
                {"GROQ_API_KEY": api_key, "selected_llm": model_name}
            ).get_base_llm()

        if provider_lower == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            from backend.app.agent.llms.ollama_llm import OllamaLLM

            return OllamaLLM(
                {"selected_llm": model_name, "OLLAMA_BASE_URL": base_url}
            ).get_base_llm()

        if provider_lower == "gemini":
            api_key = os.getenv("GEMINI_API_KEY", "")
            if not api_key:
                return None
            from backend.app.agent.llms.gemini_llm import GeminiLLM

            return GeminiLLM(
                {"GEMINI_API_KEY": api_key, "selected_llm": model_name}
            ).get_base_llm()

        if provider_lower == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            if not api_key:
                return None
            from backend.app.agent.llms.anthropic_llm import AnthropicLLM

            return AnthropicLLM(
                {"ANTHROPIC_API_KEY": api_key, "selected_llm": model_name}
            ).get_base_llm()

        if provider_lower == "azure":
            api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("OPENAI_BASE_URL", "")
            api_version = (
                os.getenv("AZURE_OPENAI_API_VERSION")
                or os.getenv("OPENAI_API_VERSION", "2024-02-15-preview")
            )
            if not api_key or not endpoint:
                return None
            from backend.app.agent.llms.azure_llm import AzureLLM

            return AzureLLM(
                {
                    "AZURE_OPENAI_API_KEY": api_key,
                    "AZURE_OPENAI_ENDPOINT": endpoint,
                    "AZURE_OPENAI_API_VERSION": api_version,
                    "selected_llm": model_name,
                }
            ).get_base_llm()

        logger.warning("Unsupported provider for fallback chain: %s", provider_lower)
        return None
    except Exception as exc:
        logger.warning("Failed to initialize %s LLM: %s", provider_lower, exc)
        return None


def build_llm_with_fallbacks(selected_provider: str, selected_llm: str | None = None):
    """
    Build an LLM runnable that tries providers in order:
    selected -> anthropic -> gemini -> groq -> openai -> ollama
    """
    selected_lower = selected_provider.lower()

    providers = [selected_lower]
    for provider in FALLBACK_PROVIDER_ORDER:
        if provider not in providers:
            providers.append(provider)

    llms = []
    built_providers = []
    for index, provider in enumerate(providers):
        model = selected_llm if index == 0 else None
        llm = try_build_provider_llm(provider, model)
        if llm is not None:
            llms.append(llm)
            built_providers.append(provider)

    if not llms:
        raise ValueError(
            "No LLM providers available. Configure at least one provider API key "
            "or ensure Ollama is running."
        )

    primary = llms[0]
    fallbacks = llms[1:]
    if fallbacks:
        logger.info(
            "Email classifier fallback chain: %s",
            " -> ".join(built_providers),
        )
        return primary.with_fallbacks(fallbacks)

    return primary
