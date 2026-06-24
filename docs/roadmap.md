# Roadmap

This roadmap serves both goals:

1. build a real PDF Study Assistant, not a disposable demo
2. learn production-oriented RAG engineering by shipping useful slices
3. produce a public portfolio demo that clearly shows AI engineering judgment

The delivery loop is:

```text
design a slice -> implement it -> test it -> document only what matters -> review the next slice
```

Do not add infrastructure before the application model needs it. Keep every
milestone locally verifiable.

## Product Rule

The product rule is:

```text
PDF-grounded by default.
Internet-supplemented only when requested.
Source boundaries always visible.
```

This keeps the PDF as the primary authority while allowing study
transformations, such as summaries or notes, to synthesize from the document
instead of looking for pre-written summaries inside it.

## Current Milestone: Error Boundaries

Status: in progress.

Goal: represent expected failures as stable application states before adding
persistence. The public demo should fail gracefully for recruiters or technical
managers who try the app with ordinary PDFs, incomplete configuration, or
temporary provider issues.

Common failures:

- missing or invalid API key
- provider failure or timeout
- empty model response
- scanned PDF with no extractable text
- embedding model load/download failure
- weak or empty retrieval results

Keep user-facing messages separate from developer details.

Definition of done:

- `AnswerError` uses stable codes for common expected failures
- `/study` shows helpful messages without leaking provider internals
- `/logic` exposes developer details for debugging and architectural inspection
- tests cover success and expected failure paths

## Next Milestones

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

### Result And Citation Hardening

Make answer boundaries clearer:

- PDF answer
- PDF chunks used
- internet supplement
- readable web citations
- disagreements between PDF and internet context

Decide how strict web citation extraction should be with Google Search
grounding metadata.

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

### Task Intent And Context Strategy

Use different PDF-grounded strategies for different study tasks:

- factual lookup: semantic retrieval top-k
- summaries, notes, outlines, flashcards, explanations, and study guides: broad
  document context

This should fix cases where the app says the PDF does not contain a summary even
though the user is asking the assistant to create one from the PDF.

Future improvements should make the broad context strategy section-aware and add
a multi-pass summary flow for long documents.

### Evaluation

Start evaluation before adding orchestration frameworks:

1. Create a small local golden dataset with PDFs, questions, expected answer
   traits, expected source behavior, and expected error states.
2. Add deterministic checks for parser behavior, citation boundaries, source
   references, task intent, and retrieval quality.
3. Add LLM-as-judge evaluation only after deterministic checks exist, using it
   for answer helpfulness, faithfulness, and separation of PDF versus internet
   content.
4. Consider LangChain or LangGraph only when evaluation needs multi-step
   orchestration, repeated judge prompts, dataset runners, or report generation.

## Later Backlog

Keep these as future options until the product needs them:

- backend API service, likely FastAPI
- persisted embeddings or vector database
- CI/CD and deployment hardening
- OCR for scanned PDFs
- multi-document workflows
- cost and latency tracking
- orchestration frameworks or agent patterns, only if they solve a real workflow

## Current Next Step

Classify common failures with stable application error codes, then expose those
codes through `AnswerError`, `/study`, `/logic`, and focused tests.
