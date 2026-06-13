---
title: PDF Study Assistant
emoji: "\U0001F4DA"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: false
short_description: PDF-first RAG study assistant with optional internet context
---

# PDF Study Assistant

PDF Study Assistant is a Streamlit-based Retrieval-Augmented Generation (RAG)
study tool.

The project is being built incrementally for learning, but the target is a
production-ready study assistant with memory, traceability, debugging support,
evaluation, and user history.

## What The App Does

Current user flow:

1. Upload a text-based PDF.
2. Extract readable text.
3. Split the text into chunks.
4. Embed the chunks locally.
5. Retrieve relevant PDF chunks for a question.
6. Generate a PDF-first answer with Gemini.
7. Optionally add internet information as a clearly separated supplement.

The app has two Streamlit pages:

- `/study`: upload a PDF, ask a question, and read the generated answer.
- `/logic`: inspect extracted text, chunks, embeddings, retrieval results, and prompts.

## Quick Start

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create local environment config:

```powershell
Copy-Item .env.example .env
```

Set your Gemini API key in `.env`:

```env
LLM_API_KEY=your-real-api-key
EMBEDDING_MODEL_LOCAL_ONLY=false
```

Run the app:

```powershell
streamlit run app.py
```

Open:

```text
http://localhost:8501/study
```

First run note: the local embedding model may download the first time you
process a PDF. Later runs reuse the local model cache.

## Configuration

Required environment variables:

```env
LLM_API_KEY=your-llm-api-key-here
EMBEDDING_MODEL_LOCAL_ONLY=false
```

Do not commit real API keys. `.env` is local-only, and `.env.example` is the
safe public template.

The app intentionally does not collect API keys in the web UI. Provider secrets
belong in local environment variables or deployment secrets.

## Verification

Run lightweight checks:

```powershell
python -m compileall app.py src tests
python -m unittest discover -s tests
```

## Project Documentation

Each document has a distinct responsibility:

- `docs/architecture.md`: abstract architecture, data flow, layers, and current module boundaries.
- `docs/roadmap.md`: combined production-readiness and AI Engineer skill-alignment roadmap.
- `docs/decisions.md`: durable engineering decisions and tradeoffs.
- `docs/deployment.md`: Hugging Face Spaces deployment instructions.
- `AGENTS.md`: working instructions for Codex and other coding agents.

## Current Status

Implemented:

- PDF upload and text extraction
- chunking
- local embedding generation
- in-memory document index
- semantic retrieval
- PDF-first prompt construction
- Gemini answer generation
- explicit answer result and model-call objects
- optional Google Search grounding
- `/study` and `/logic` pages
- Streamlit state/runtime/page separation
- Hugging Face Spaces Docker deployment setup

Current production-oriented milestone:

```text
Complete the explicit answer result model.
```

The first slice now stores answers as structured application objects instead of
raw strings. The remaining work is to make PDF answer, internet supplement, web
citations, and error boundaries more explicit before database work, because
persistence should follow stable application models instead of defining them
prematurely.
