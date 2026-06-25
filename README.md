# Email Agent

A full-stack email classification app: a **FastAPI** backend (LangGraph + multiple LLM providers) and a **React** frontend for classifying emails.

## Prerequisites

- **Python 3.13+** (see `.python-version`)
- **Node.js 18+** and npm (for the frontend)
- An API key for at least one LLM provider (OpenAI, Groq, Gemini, Anthropic, or Azure OpenAI), or a local [Ollama](https://ollama.com/) instance

---

## 1. Install uv

[uv](https://docs.astral.sh/uv/) is a fast Python package and project manager. Use it to create the virtual environment and install backend dependencies.

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify the install:

```bash
uv --version
```

---

## 2. Set up the application

### Clone the repository

```bash
git clone <your-repo-url>
cd email-agent
```

### Backend (Python)

From the project root, install dependencies and create a virtual environment:

```bash
uv sync
```

This reads `pyproject.toml` and `uv.lock`, creates `.venv`, and installs all Python packages.

### Environment variables

Create a `.env` file in the project root. The backend loads it automatically on startup.

Add the keys for the provider(s) you plan to use:

```env
# OpenAI (default provider in the UI)
OPENAI_API_KEY=your-key-here

# Optional — other providers
GROQ_API_KEY=
GEMINI_API_KEY=
ANTHROPIC_API_KEY=

# Azure OpenAI (also used by the email judge node)
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-5.4

# Ollama (no API key — runs locally)
OLLAMA_BASE_URL=http://localhost:11434

# Optional — Langfuse observability
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
```

You only need the variables for the provider you select in the UI. Ollama does not require an API key if it is already running locally.

### Frontend (React)

Install Node dependencies:

```bash
npm install --prefix frontend
```

---

## 3. Run the application

You need **two terminals**, both from the project root.

### Terminal 1 — Backend API (port 8000)

```bash
uv run python main.py
```

Or, with the virtual environment activated:

```bash
# Windows
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

python main.py
```

The API starts at **http://127.0.0.1:8000**. Docs are at **http://127.0.0.1:8000/docs**.

### Terminal 2 — Frontend (port 5173)

```bash
npm run dev --prefix frontend
```

Open **http://localhost:5173** in your browser. The UI talks to the backend at `http://localhost:8000` by default (configurable in the app).

---

## Quick test

1. Start both the backend and frontend.
2. Open the frontend in your browser.
3. Paste an email subject and body, choose an LLM provider, and click classify.

If you see a connection error, confirm the backend is running on port 8000.

---

## Project layout

```
email-agent/
├── backend/          # FastAPI app, LangGraph agent, LLM integrations
├── frontend/         # React + Vite UI
├── main.py           # Backend entry point
├── pyproject.toml    # Python dependencies (managed by uv)
└── .env              # API keys (create this — not committed to git)
```
