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
instead of looking for pre-written summaries inside it. When internet context is
enabled, the app should add a separate web-based expansion that can add outside
context and fill gaps in the PDF answer.

## Completed Foundation: Error Boundaries

Status: core answer-generation boundary complete; document-preparation and
retrieval edge cases remain follow-up work.

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

## Immediate Portfolio Milestone: Evidence And Evaluation

The project’s next definition of done is not another infrastructure component. It
is evidence that the RAG system became more reliable and more auditable.

### 1. Explicit Submission

- require a Generate answer action before making an LLM call
- keep `/study` calm and predictable for public users
- preserve detailed diagnostics and the effective run inputs on `/logic`

### 2. Page-Aware PDF Evidence

- preserve filename, page number, chunk ID, and text through loading, chunking,
  retrieval, prompts, and answer results
- render citations such as `Lecture 3, page 12, chunk 2` with a short excerpt
- validate that cited pages and chunks belong to the retrieved evidence

### 3. Baseline Evaluation

- add a small versioned dataset under `evals/` with representative PDFs and
  20-30 questions
- cover factual lookup, study transformations, unsupported questions, and citation
  behavior
- measure retrieval hit rate, citation validity, latency, failures, and reviewed
  faithfulness/summary-coverage criteria
- publish baseline results and limitations in `docs/evaluation.md`

### 4. Improve And Re-measure

- replace first-chunk summary behavior with page/section-aware coverage
- use multi-pass summarization for long documents when the baseline shows a need
- compare post-change results with the baseline and keep the change only when the
  evidence supports it

### 5. CI And Public Proof

- run unit tests and deterministic evaluation checks on every push
- add the CI status to the README
- keep the README focused on the demo, architecture, measured results, and known
  limitations

## Existing Production Milestones

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
- internet supplement as a distinct web-based expansion
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

The immediate evaluation work above supersedes this section’s placement as a
future milestone. Keep these principles:

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
- broader CI/CD and deployment hardening after the deterministic checks exist
- OCR for scanned PDFs
- multi-document workflows
- cost and latency tracking
- orchestration frameworks or agent patterns, only if they solve a real workflow

## Current Next Step

Implement the explicit submission boundary, then preserve page-aware PDF metadata
through the smallest end-to-end citation slice. Capture a baseline evaluation
before changing long-document summary behavior.
