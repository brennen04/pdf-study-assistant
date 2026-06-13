# Roadmap

This roadmap serves both goals:

1. build a real PDF Study Assistant, not a disposable demo
2. learn production-oriented RAG engineering by shipping useful slices

The delivery loop is:

```text
design a slice -> implement it -> test it -> document only what matters -> review the next slice
```

Do not add infrastructure before the application model needs it. Keep every
milestone locally verifiable.

## Current Status

Core RAG baseline is mostly complete:

- PDF upload and text extraction
- chunking
- local embeddings
- in-memory `DocumentIndex`
- semantic retrieval
- PDF-first prompt construction
- Gemini answer generation
- optional Google Search grounding
- `/study` and `/logic` pages
- Streamlit state/runtime/page separation

## Current Milestone: Explicit AI Result Model

Status: in progress.

Goal: replace raw answer strings with structured application objects that can
support rendering, debugging, persistence, evaluation, and future APIs.

Current objects:

```text
AnswerResult
ModelCall
RetrievedSource
AnswerError
```

Completed first slice:

- answer generation stores an `AnswerResult`
- `/study` renders from the structured result
- `/logic` can inspect model-call metadata and raw output
- tests cover result construction and basic provider failure behavior

Remaining:

- separate PDF answer, internet supplement, and citations more explicitly
- improve expected error classification beyond exception class names
- decide whether the prompt should request a stricter parseable response format

Definition of done:

- UI no longer depends on raw answer strings
- result objects carry answer content, sources, model-call metadata, and errors
- `/logic` exposes enough detail to debug a single answer run
- tests cover success and common failure paths

## Next Milestones

### Error Boundaries

Represent expected failures as stable application states:

- missing or invalid API key
- provider failure or timeout
- empty model response
- scanned PDF with no extractable text
- embedding model load/download failure
- weak or empty retrieval results

Keep user-facing messages separate from developer details.

### Traceability

Capture enough information to explain how an answer was produced:

- document identity
- question
- retrieved chunks and similarity scores
- prompt
- model name and settings
- raw output
- parsed result fields
- latency
- error details
- timestamp

The `/logic` page is the first home for this.

### Persistence And History

Add persistence only after result and trace models are stable.

Likely first database: SQLite.

Likely records:

```text
documents
document_chunks
question_runs
retrieved_sources
model_calls
answer_results
errors
evaluations
```

Storage should follow application models, not define them too early.

### Source And Citation UX

Make evidence clearer:

- PDF answer
- PDF chunks used
- internet supplement
- web citations
- disagreements between PDF and internet context

This should reinforce the product rule: PDF first, internet second.

## Later Backlog

Keep these as future options until the product needs them:

- evaluation dataset and regression checks
- backend API service, likely FastAPI
- persisted embeddings or vector database
- CI/CD and deployment hardening
- OCR for scanned PDFs
- multi-document workflows
- cost and latency tracking
- orchestration frameworks or agent patterns, only if they solve a real workflow

## Current Next Step

Continue the explicit answer result model by designing a stricter answer output
contract. The key question is whether Gemini should return structured sections
that can be parsed into `pdf_answer`, `internet_supplement`, and citations.
