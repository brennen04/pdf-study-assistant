---
title: PDF Study Assistant
emoji: "\U0001F4DA"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: false
short_description: PDF-grounded RAG study assistant with optional internet context
---

# PDF Study Assistant

[![Test and evaluate](https://github.com/brennen04/pdf-study-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/brennen04/pdf-study-assistant/actions/workflows/ci.yml)

PDF Study Assistant is a Streamlit-based Retrieval-Augmented Generation (RAG)
study tool and public portfolio demo.

The goal is to build a useful PDF-grounded assistant while learning the
architecture of production-oriented AI systems: ingestion, retrieval, prompt
construction, model boundaries, traceability, evaluation, and deployment. The
deployed app should be recruiter- and technical-manager-friendly: easy to try,
clear about source boundaries, and resilient when demo inputs fail.

Product rule:

```text
PDF-grounded by default.
Internet-supplemented only when requested.
Source boundaries always visible.
```

The uploaded PDF is the primary authority. When internet context is requested,
the app should add a separate web-based expansion that can add outside context
and fill gaps in the PDF answer. Internet information must remain visibly
separate from PDF-grounded content.

## What The App Does

Target user flow for the immediate portfolio milestone:

1. Upload a text-based PDF.
2. Extract readable text while retaining document/page metadata.
3. Split the text into page-aware chunks.
4. Embed the chunks locally.
5. Retrieve relevant PDF chunks for a question.
6. Generate a PDF-grounded answer with Gemini after an explicit user submission.
7. If requested, add a clearly separated internet expansion.
8. Show useful PDF citations and readable web citation links with source boundaries.

The app has two Streamlit pages:

- `/study`: upload a PDF, ask a question, and read the generated answer.
- `/logic`: inspect extracted text, chunks, embeddings, retrieval results, and prompts.

## Engineering Goals

This project should read like an AI Engineer showcase, not a notebook demo.
Every major feature should make one part of the RAG architecture easier to
understand, test, or explain:

- keep Streamlit thin and move reusable behavior into `src/`
- make important data explicit with application objects
- preserve traceability from question to sources to model output
- test pure logic before UI behavior
- add infrastructure only when the application model needs it

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
.\venv\Scripts\python.exe -m compileall app.py src tests
.\venv\Scripts\python.exe -m unittest discover -s tests
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

- PDF ingestion, chunking, local embeddings, in-memory indexing, and retrieval
- task-intent routing for lookup versus study transformation requests
- PDF-grounded prompt construction and Gemini answer generation
- structured answer results with parsed answer sections, citations, and model-call metadata
- optional Google Search grounding with a visibly separated web expansion
- `/study` and `/logic` pages for user flow and architecture inspection
- Streamlit state/runtime/page separation and Hugging Face Spaces Docker setup
- page-aware PDF citations, coverage-aware long-document context, and explicit answer submission
- versioned retrieval evaluation: 17/17 scored cases pass in CI
- manual real-PDF review: 6/6 scenarios passed; see `docs/evaluation.md`

Portfolio V1 demonstrates a measured RAG improvement: coverage-aware context
selection and narrower intent routing raised the versioned retrieval result from
15/17 to 17/17 scored cases. Persistence and database work remain later options
that should follow stable application models.

Known limitation: web citations remain experimental until the app extracts Google
grounding metadata from provider responses. They are not equivalent to verified PDF
evidence.
