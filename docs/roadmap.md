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
- PDF-grounded prompt construction
- deterministic task-intent routing for lookup versus study transformation
  requests
- Gemini answer generation
- optional Google Search grounding
- `/study` and `/logic` pages
- Streamlit state/runtime/page separation

The product rule is now framed as:

```text
PDF-grounded by default.
Internet-supplemented only when requested.
Source boundaries always visible.
```

This keeps the PDF as the primary authority while allowing study
transformations, such as summaries or notes, to synthesize from the document
instead of looking for pre-written summaries inside it.

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
- Gemini is prompted for a stricter JSON answer contract
- parsed answer fields include PDF answer, internet supplement, PDF source
  numbers, web citations, and disagreement notes
- `/study` renders from the structured result
- `/logic` can inspect model-call metadata, parsed fields, and raw output
- parsed PDF source numbers are validated against retrieved PDF sources before
  an answer is treated as successful
- tests cover result construction, answer parsing, malformed model output, and
  basic provider failure behavior

Remaining:

- improve expected error classification beyond exception class names
- improve the study transformation context strategy beyond first chunks, likely
  with section-aware context or a future multi-pass summary flow
- decide how strict web citation extraction should be with Google Search
  grounding metadata

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

This should reinforce the product rule: PDF-grounded by default,
internet-supplemented only when requested, and source boundaries always visible.

### Task Intent And Context Strategy

Use different PDF-grounded strategies for different study tasks:

- factual lookup: semantic retrieval top-k
- summaries, notes, outlines, flashcards, explanations, and study guides: broad
  document context

This should fix cases where the app says the PDF does not contain a summary even
though the user is asking the assistant to create one from the PDF.

Future improvements should make the broad context strategy section-aware and add
a multi-pass summary flow for long documents.

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

Continue the explicit answer result model and task routing by tightening
validation and expected error boundaries. The next useful slice is to classify
common failures with stable application error codes.
