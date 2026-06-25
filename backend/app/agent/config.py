"""Agent configuration for email classifier LLM providers."""

# Fallback order after the user-selected provider.
FALLBACK_PROVIDER_ORDER = ["anthropic", "gemini", "groq", "openai", "ollama"]

DEFAULT_MODELS = {
    "anthropic": "claude-haiku-4-5-20251001",
    "gemini": "gemini-2.5-flash",
    "groq": "llama-3.3-70b-versatile",
    "openai": "gpt-4.1-mini",
    "ollama": "gemma3:1b",
    "azure": "gpt-4o-mini",
}
