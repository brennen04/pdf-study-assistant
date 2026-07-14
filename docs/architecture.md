# Architecture

PDF Study Assistant is a layered Streamlit RAG application. This document owns
runtime shape, data flow, state, and module boundaries; product status and quality
results belong in the README and evaluation document.

Core product rule:

```text
PDF-grounded by default.
Internet-supplemented only when requested.
Source boundaries always visible.
```

The uploaded PDF is the primary authority. When internet context is requested,
the app should add a clearly separated web-based expansion that can add outside
context and fill gaps in the PDF answer, and disagreement between PDF and
internet sources should be surfaced instead of blended.

PDF-grounded answers have two important shapes:

- factual lookup: retrieve the most relevant PDF chunks and answer from them
- study transformation: synthesize summaries, notes, explanations, outlines,
  flashcards, or study guides from the PDF context

The app should not tell the user that the PDF lacks a summary merely because the
summary does not already exist as text. A summary is a transformation over the
PDF, not a fact that must be found verbatim.

## Architecture Goals

The architecture should make the RAG system explainable to both a user and a
future engineer:

- each workflow step has an owner and can be inspected
- Streamlit handles UI and rerun behavior, not core RAG logic
- provider details stay behind small integration modules
- answer content, citations, model calls, and expected errors are explicit
  application objects
- tests focus on deterministic logic before provider or UI behavior

## System Shape

The app has two main workflows:

```text
Document ingestion:
PDF bytes -> extracted text -> chunks -> embeddings -> DocumentIndex

Question answering:
question -> question embedding -> retrieved PDF chunks -> PDF-only model call
         -> validate PDF citations
         -> optional Google Search supplement call -> AnswerResult
```

The workflow is deliberately split at application boundaries. Provider responses
are parsed into an `AnswerResult`, citations are validated against the retrieved
sources held by the application, and expected provider failures are mapped to
stable `AnswerError` codes before presentation.

The `DocumentIndex` is stable for the current uploaded PDF and can be reused
across questions. A question, retrieved sources, prompt, model call, and answer
result are specific to one answer attempt.

Question answering routes by task intent:

```text
factual lookup -> semantic retrieval top-k -> answer from retrieved chunks
study transformation -> broad document context -> synthesize from PDF
```

This keeps the product PDF-grounded while allowing different retrieval strategies
for different study tasks.

When internet context is enabled, the validated PDF answer is completed before a
separate Google Search call creates the internet supplement. The supplement can
add distinct outside context, such as broader background, examples, related
concepts, caveats, or current context, without affecting PDF citation validation.

## Layers

```text
UI layer
  Streamlit pages and display components

Runtime layer
  Streamlit session state, cache wrappers, rerun-safe orchestration

RAG workflow layer
  document indexing, question context, retrieval, prompt construction

Domain service layer
  PDF loading, chunking, embeddings, vector ranking, answer result models

Provider layer
  Gemini API, optional Google Search grounding, environment loading
```

The important boundary is between Streamlit concerns and reusable RAG behavior.
Streamlit reruns, widgets, and session state should stay out of the core RAG
workflow as much as practical.

## Module Ownership

- `app.py`: entry point, environment loading, page setup, routing.
- `src/streamlit_app/`: Streamlit-specific runtime, state, and page modules.
- `src/streamlit_app/pages/`: `/study`, `/logic`, and shared Streamlit UI.
- `src/streamlit_app/state.py`: uploaded PDF state, loaded document state, latest `AnswerResult`, answer cache key.
- `src/streamlit_app/runtime.py`: Streamlit cache wrappers and answer-generation orchestration.
- `src/rag/`: reusable PDF-grounded workflow and retrieval services.
- `src/rag/pipeline.py`: build `DocumentIndex`, classify task intent, build `QuestionContext`, retrieve/select PDF context, build prompts.
- `src/rag/task_intent.py`: deterministic task-intent classification for lookup versus study transformation requests.
- `src/rag/pdf_loader.py`, `src/rag/chunker.py`, `src/rag/retriever.py`: focused RAG services.
- `src/answer/`: answer contract, prompt construction, parsing, validation, and citation display helpers.
- `src/answer/result.py`: `AnswerResult`, `ModelCall`, `RetrievedSource`, `WebCitation`, `AnswerError`.
- `src/answer/builder.py`: PDF-grounded prompt construction.
- `src/answer/parser.py`: parse structured model output into answer fields.
- `src/answer/validation.py`: validate parsed answer fields against trusted app state, such as retrieved PDF source numbers.
- `src/answer/web_citations.py`: safely format titled, absolute web citations for display.
- `src/providers/`: external provider integrations and provider-adjacent configuration.
- `src/providers/gemini_client.py`: Gemini integration, optional Google Search grounding, and structured grounding-source extraction.
- `src/providers/embedding_client.py`: local embedding model integration.
- `src/providers/config.py`: local `.env` loading.

## State And Caching

Cache stable document work:

- PDF bytes to extracted text
- extracted text to `DocumentIndex`

Do not rebuild the PDF index when the user changes a question or toggles
internet context. Do clear loaded document and answer state when the uploaded
PDF changes.

LLM calls are deduped by a stable answer cache key derived from the workflow
version, effective prompt, and internet-context setting. Failed calls should be
inspectable, but they should not poison the success cache.

## Current Boundary

The answer result model carries structured answer content, citations, retrieved PDF
sources, separate PDF and internet model-call metadata, raw provider output, and
application errors. A failed internet supplement remains inspectable without
discarding an already validated PDF answer. Future persistence should follow these
application models rather than define them first.

The current system is intentionally process-local: document indexes, answer state,
and caches live within the Streamlit session/runtime. That is appropriate for the
public single-session demo, but it means uploads and history are not durable across
session expiry or deployment restarts. Persistence is the next major architecture
boundary only when user history becomes a product requirement.
