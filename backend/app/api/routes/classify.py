import os
import sys
import logging
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
from backend.app.agent.llms.factory import build_llm_with_fallbacks
from langfuse import observe
from langfuse.langchain import CallbackHandler

logger = logging.getLogger(__name__)

router = APIRouter()




@router.post("/classify", response_model=ClassificationResponse, summary="Classify an email's content")
@observe(name="classify_email")
async def classify_email(req: ClassificationRequest):
    logger.info(
        f"API: Received classification request. "
        f"Provider: '{req.provider}', Selected LLM: '{req.selected_llm}', "
        f"Subject: '{req.subject}', Thread ID: '{req.thread_id}'"
    )
    try:
        supported_providers = {"openai", "groq", "ollama", "gemini", "anthropic", "azure"}
        if req.provider.lower() not in supported_providers:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported provider '{req.provider}'. "
                    f"Allowed providers: {', '.join(sorted(supported_providers))}."
                ),
            )

        # Selected provider first, then anthropic -> gemini -> groq -> openai -> ollama
        try:
            llm = build_llm_with_fallbacks(req.provider, req.selected_llm)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        # Build state graph
        builder = GraphBuilder(llm)
        graph = await builder.setup_graph("basic_chatbot")

        # Set up initial state
        initial_state = {
            "subject": req.subject,
            "body": req.body,
            "category": None,
            "reason": None,
            "JudgeVerted": None,
            "JudgeReasoning": None,
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

        logger.info(
            f"API: Classification workflow completed successfully. "
            f"Resulting Category: '{result.get('category')}', "
            f"Judge Verted: '{result.get('JudgeVerted')}'"
        )

        return ClassificationResponse(
            subject=result.get("subject", req.subject),
            body=result.get("body", req.body),
            category=result.get("category"),
            reason=result.get("reason"),
            JudgeVerted=result.get("JudgeVerted"),
            JudgeReasoning=result.get("JudgeReasoning"),
        )
    except HTTPException as he:
        logger.warning(f"API: HTTP Exception during classification: {he.detail}")
        raise he
    except Exception as e:
        # Standard server exception handling
        logger.error(f"API: Unexpected error during classification: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Email classification failed: {str(e)}")
