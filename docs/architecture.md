# Architecture

PDF Study Assistant is a Streamlit RAG study tool moving toward production
readiness while staying small enough to learn from.

Core product rule:

```text
PDF first, internet second.
```

Answers should use the uploaded PDF as the primary source. Internet context may
be added only as a clearly separated supplement, and disagreement between PDF
and internet sources should be surfaced instead of blended.

## System Shape

The app has two main workflows:

```text
Document ingestion:
PDF bytes -> extracted text -> chunks -> embeddings -> DocumentIndex

Question answering:
question -> question embedding -> retrieved PDF chunks -> prompt -> model call -> AnswerResult
```

The `DocumentIndex` is stable for the current uploaded PDF and can be reused
across questions. A question, retrieved sources, prompt, model call, and answer
result are specific to one answer attempt.

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
- `src/streamlit_pages/`: `/study`, `/logic`, and shared Streamlit UI.
- `src/streamlit_state.py`: uploaded PDF state, loaded document state, latest `AnswerResult`, answer cache key.
- `src/streamlit_runtime.py`: Streamlit cache wrappers and answer-generation orchestration.
- `src/rag_pipeline.py`: build `DocumentIndex`, build `QuestionContext`, retrieve chunks, build prompts.
- `src/answer_result.py`: `AnswerResult`, `ModelCall`, `RetrievedSource`, `AnswerError`.
- `src/answer_builder.py`: PDF-first prompt construction.
- `src/pdf_loader.py`, `src/chunker.py`, `src/embedding_client.py`, `src/retriever.py`: focused RAG services.
- `src/gemini_client.py`: Gemini integration and optional Google Search grounding.
- `src/config.py`: local `.env` loading.

## State And Caching

Cache stable document work:

- PDF bytes to extracted text
- extracted text to `DocumentIndex`

Do not rebuild the PDF index when the user changes a question or toggles
internet context. Do clear loaded document and answer state when the uploaded
PDF changes.

LLM calls are deduped by a stable answer cache key derived from the effective
prompt and internet-context setting. Failed calls should be inspectable, but
they should not poison the success cache.

## Current Boundary

The active architecture boundary is the answer result.

The first slice introduced structured answer and model-call objects while
preserving raw Gemini output. Next slices should make PDF answer, internet
supplement, citations, and expected failures more explicit before adding
persistence.
