import os
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException

# Ensure project root is in sys.path
current_file = Path(__file__).resolve()
project_root = current_file.parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.api.schemas.request import ClassificationRequest
from backend.app.api.schemas.response import ClassificationResponse
from backend.app.agent.builder import GraphBuilder
from langfuse import observe
from langfuse.langchain import CallbackHandler

router = APIRouter()


def get_provider_llm(req: ClassificationRequest):
    provider_lower = req.provider.lower()

    if provider_lower == "openai":
        model_name = req.selected_llm or "gpt-4.1-mini"
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )
        user_controls = {
            "OPENAI_API_KEY": api_key,
            "selected_llm": model_name,
        }
        from backend.app.agent.llms.openai_llm import OpenAILLM
        return OpenAILLM(user_controls).get_base_llm()

    elif provider_lower == "groq":
        model_name = req.selected_llm or "llama-3.3-70b-versatile"
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="Groq API key not found. Please set the GROQ_API_KEY environment variable."
            )
        user_controls = {
            "GROQ_API_KEY": api_key,
            "selected_llm": model_name,
        }
        from backend.app.agent.llms.groq_llm import GroqLLM
        return GroqLLM(user_controls).get_base_llm()

    elif provider_lower == "ollama":
        model_name = req.selected_llm or "gemma3:1b"
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        user_controls = {
            "selected_llm": model_name,
            "OLLAMA_BASE_URL": base_url,
        }
        from backend.app.agent.llms.ollama_llm import OllamaLLM
        return OllamaLLM(user_controls).get_base_llm()

    elif provider_lower == "gemini":
        model_name = req.selected_llm or "gemini-2.5-flash"
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="Gemini API key not found. Please set the GEMINI_API_KEY environment variable."
            )
        user_controls = {
            "GEMINI_API_KEY": api_key,
            "selected_llm": model_name,
        }
        from backend.app.agent.llms.gemini_llm import GeminiLLM
        return GeminiLLM(user_controls).get_base_llm()

    elif provider_lower == "anthropic":
        model_name = req.selected_llm or "claude-haiku-4-5-20251001"
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable."
            )
        user_controls = {
            "ANTHROPIC_API_KEY": api_key,
            "selected_llm": model_name,
        }
        from backend.app.agent.llms.anthropic_llm import AnthropicLLM
        return AnthropicLLM(user_controls).get_base_llm()

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider '{req.provider}'. Allowed providers: openai, groq, ollama, gemini, anthropic."
        )



@router.post("/classify", response_model=ClassificationResponse, summary="Classify an email's content")
@observe(name="classify_email")
async def classify_email(req: ClassificationRequest):
    try:
        # Initialize selected base LLM model
        llm = get_provider_llm(req)

        # Build state graph
        builder = GraphBuilder(llm)
        graph = await builder.setup_graph("basic_chatbot")

        # Set up initial state
        initial_state = {
            "subject": req.subject,
            "body": req.body,
            "category": None,
            "confidence": None,
            "reason": None,
        }

        # Initialize Langfuse CallbackHandler if credentials are configured
        callbacks = []
        if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            try:
                langfuse_handler = CallbackHandler()
                callbacks.append(langfuse_handler)
            except Exception as e:
                print(f"Warning: Could not initialize Langfuse CallbackHandler: {e}")

        # Run classification workflow
        result = await graph.ainvoke(
            initial_state,
            config={
                "configurable": {"thread_id": req.thread_id},
                "callbacks": callbacks
            }
        )

        return ClassificationResponse(
            subject=result.get("subject", req.subject),
            body=result.get("body", req.body),
            category=result.get("category"),
            confidence=result.get("confidence"),
            reason=result.get("reason"),
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        # Standard server exception handling
        raise HTTPException(status_code=500, detail=f"Email classification failed: {str(e)}")
