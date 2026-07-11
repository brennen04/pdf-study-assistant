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
study tool and publicly deployed AI engineering portfolio project.

It demonstrates a production-shaped RAG system: page-aware ingestion, local
embeddings, intent-aware context selection, structured model output, evidence
validation, observable failure boundaries, deterministic evaluation, and cloud
deployment. The public experience stays easy to try while `/logic` exposes the
technical path from PDF extraction to the final answer.

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

Core user flow:

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

## Technical Highlights

This is designed as an inspectable application rather than a notebook demo:

- Streamlit is a thin UI/runtime layer over reusable services in `src/`.
- `AnswerResult`, `ModelCall`, `RetrievedSource`, and `AnswerError` make the
  answer boundary explicit instead of passing provider output as an opaque string.
- Page and chunk identity survive ingestion, retrieval, prompting, validation,
  and rendering, so citations can be audited against retrieved evidence.
- Factual questions use semantic top-k retrieval; study transformations use
  ordered, coverage-aware context across the document.
- Stable application error codes keep `/study` calm while `/logic` retains raw
  provider output and diagnostics.
- CI compiles the project, runs unit tests, and enforces the versioned retrieval
  benchmark without a live LLM call.

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

Runtime configuration:

```env
LLM_API_KEY=your-llm-api-key-here
EMBEDDING_MODEL_LOCAL_ONLY=false
```

`LLM_API_KEY` is required for answer generation. `EMBEDDING_MODEL_LOCAL_ONLY`
defaults to `false`; set it to `true` only when the embedding model is already
cached and network access must be disabled.

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

- `docs/architecture.md`: runtime shape, data flow, and module boundaries.
- `docs/evaluation.md`: reproducible quality evidence and its limitations.
- `docs/roadmap.md`: completed milestones and prioritized future work.
- `docs/decisions.md`: durable engineering decisions and tradeoffs.
- `docs/deployment.md`: Streamlit Community Cloud operations and legacy Docker notes.
- `AGENTS.md`: working rules for coding agents.

## Current Status

Implemented:

- PDF ingestion, chunking, local embeddings, in-memory indexing, and retrieval
- task-intent routing for lookup versus study transformation requests
- PDF-grounded prompt construction and Gemini answer generation
- structured answer results with parsed answer sections, citations, and model-call metadata
- optional Google Search grounding with a visibly separated web expansion
- `/study` and `/logic` pages for user flow and architecture inspection
- Streamlit state/runtime/page separation and Streamlit Community Cloud deployment
- page-aware PDF citations, coverage-aware long-document context, and explicit answer submission
- versioned retrieval evaluation: 17/17 scored cases pass in CI
- manual real-PDF review: 6/6 scenarios passed; see `docs/evaluation.md`

Portfolio V1 demonstrates a measured RAG improvement: coverage-aware context
selection and narrower intent routing raised the versioned retrieval result from
15/17 to 17/17 scored cases. The full method, before/after table, and limitations
live in `docs/evaluation.md`; persistence remains a later option that should follow
the stable application models.

Known limitation: web citations remain experimental until the app extracts Google
grounding metadata from provider responses. They are not equivalent to verified PDF
evidence.

## Future Improvements

Future work is selected to demonstrate deeper AI engineering capability through
measurable product value rather than technology added for its own sake:

- **Grounding and provenance:** extract structured Google grounding metadata for
  verified titles, publishers, and destination URLs, demonstrating trustworthy
  multi-source RAG and provider-response handling.
- **Evaluation engineering:** broaden the versioned dataset across document types
  and lengths; measure retrieval, citation validity, faithfulness, unsupported
  answers, and summary coverage with reproducible reports.
- **Observability and performance:** capture cold-start, indexing, retrieval, model
  latency, failures, and token usage before optimizing the embedding or generation
  path.
- **Document intelligence:** add OCR and layout-aware extraction when evaluation
  shows that scanned or structurally complex PDFs are an important failure mode.
- **RAG at larger scope:** add persistent runs, multi-document retrieval, and a
  vector database only when history or corpus size exceeds the current in-memory
  design, documenting the baseline and tradeoffs.
- **Model quality controls:** evaluate multi-pass summarization or an LLM judge only
  after defining versioned rubrics, model configuration, cost, and deterministic
  checks.

See `docs/roadmap.md` for sequencing and the conditions that justify each larger
architecture boundary.
