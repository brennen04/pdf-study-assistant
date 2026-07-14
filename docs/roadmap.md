# Roadmap

The roadmap prioritizes measurable RAG quality and inspectable application boundaries.
Detailed architecture, evaluation results, and rationale live in their dedicated
documents rather than being repeated here.

Delivery loop:

```text
design a slice -> establish evidence -> implement -> verify -> record the decision
```

## Completed: Portfolio V1

- Thin Streamlit `/study` and `/logic` surfaces over reusable RAG modules.
- Page-aware PDF extraction, chunking, local embeddings, and in-memory retrieval.
- Intent routing between semantic factual lookup and coverage-aware study
  transformations.
- Structured `AnswerResult`, `ModelCall`, `RetrievedSource`, and `AnswerError`
  boundaries with raw-output retention and citation validation.
- Explicit answer submission, rerun-safe state, stable document caching, and
  public-facing error mapping.
- Visibly separated optional internet expansion through Gemini Google Search
  grounding, with web citations extracted from structured grounding metadata.
- Versioned retrieval evaluation enforced in CI; scored cases improved from 15/17
  to 17/17, with a 6/6 manual real-PDF scenario review.
- Successful public deployment through Streamlit Community Cloud.

## Next: AI Engineering Evidence

Each slice should produce concrete engineering evidence: an explicit contract, an
evaluation result, an operational measurement, or a documented tradeoff.

1. **Grounding evaluation:** map grounded claims to their supporting web chunks and
   measure redirect durability, citation validity, and source coverage.
2. **Evaluation engineering:** expand the versioned corpus and reviewed rubric
   across document types and lengths, especially faithfulness, unsupported answers,
   citation validity, and summary coverage.
3. **Observability:** record cold-start, indexing, retrieval, provider latency,
   failures, and token usage before making performance or cost claims.
4. **Document intelligence:** add OCR and layout-aware extraction only when a
   measured scanned-PDF or complex-layout failure rate justifies the slice.
5. **Model evaluation:** assess multi-pass summarization or an LLM judge only with a
   versioned rubric, fixed model configuration, recorded cost, and deterministic
   checks already in place.

## Later: Product-Driven Boundaries

Add these only when a concrete user workflow requires them:

- SQLite persistence for documents, question runs, retrieved sources, model calls,
  answers, and errors.
- Multi-document study sessions and user history.
- Persisted embeddings or a vector database when indexes must survive sessions or
  corpus size exceeds practical in-memory retrieval.
- A backend API when another client must consume the RAG workflow.
- Multi-pass summarization when reviewed quality shows that bounded coverage-aware
  context is insufficient.
- Orchestration frameworks when the workflow genuinely needs durable multi-step
  execution, not merely another abstraction.

For portfolio value, every larger boundary should include a before/after result and
an explanation of why the selected architecture fits better than the simpler one it
replaces.

## Definition Of Done For Future Slices

A feature is complete when its user behavior works, its application boundary is
inspectable, deterministic logic is tested, measurable quality is compared with a
baseline where applicable, and durable tradeoffs are recorded in `decisions.md`.
