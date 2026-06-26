import os
import sys
import logging
from pathlib import Path

import dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in sys.path
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.api.router import api_router

dotenv.load_dotenv()

# Configure logging for backend package to ensure logs are shown properly in all environments
backend_logger = logging.getLogger("backend")
backend_logger.setLevel(logging.INFO)
if not backend_logger.handlers:
    # 1. Stdout Handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    stdout_handler.setFormatter(stdout_formatter)
    backend_logger.addHandler(stdout_handler)

    # 2. File Handler (saves to backend.log in project root)
    try:
        log_file_path = project_root / "backend.log"
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        file_handler.setFormatter(file_formatter)
        backend_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not configure FileHandler for backend.log: {e}", file=sys.stderr)

    backend_logger.propagate = False

app = FastAPI(
    title="Email Classifier API",
    description="FastAPI service for classifying emails using LangGraph and various LLMs",
    version="0.1.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
