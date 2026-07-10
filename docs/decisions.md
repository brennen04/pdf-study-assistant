# Decisions

This file records important project decisions and the reasoning behind them.

## Build As A RAG Architecture Showcase

Decision: build PDF Study Assistant as both a usable study tool and a public AI
engineering portfolio demo.

Reason:

- the project should demonstrate architecture judgment, not only API usage
- RAG systems are easiest to explain when ingestion, retrieval, prompting,
  model calls, answer contracts, traceability, and evaluation are visible
- learning the architecture while building is a primary project goal
- recruiters and technical managers should be able to try the deployed app and
  see professional behavior even when demo inputs fail

Tradeoff:

- some features may take longer because the code should be inspectable,
  testable, and easy to explain
- the app should feel demo-ready without prematurely optimizing for high-scale
  public usage

Mitigation:

- ship small vertical slices
- keep Streamlit thin and reusable behavior in `src/`
- prefer explicit application objects over raw strings at important boundaries
- document durable decisions, not routine implementation notes
- prioritize evidence-grade citations and evaluation before persistence or heavier
  infrastructure

## Use `.env.example` And Ignore `.env`

Decision: commit `.env.example`, ignore `.env`.

Reason:

- public users need to know which environment variables are required
- real API keys must not be committed
- each developer can keep local secrets in `.env`

Current variables:

```env
LLM_API_KEY=your-llm-api-key-here
EMBEDDING_MODEL_LOCAL_ONLY=false
```

## Do Not Collect API Keys In The Frontend

Decision: the web UI does not include an API key input.

Reason:

- infrastructure secrets belong in local configuration
- public repo users should configure `.env`
- frontend controls should represent product behavior, not secret management

## PDF-Grounded By Default

Decision: the uploaded PDF is the primary authority. Internet context is optional
and should appear only as a clearly separated supplement when requested. When
requested, it should add a distinct web-based expansion that can add outside
context and fill gaps in the PDF answer. Source boundaries must remain visible.

Reason:

- the product is a PDF study assistant, not a general web-search chatbot
- the user should be able to distinguish document-grounded information from external information
- users who enable internet context expect a visible web-based addition
- disagreements between the PDF and internet sources should be visible instead of blended
- study transformations such as summaries, notes, outlines, explanations, and
  flashcards should synthesize from the PDF instead of requiring that artifact
  to already exist in the document

Tradeoff:

- different question types need different PDF-grounded context strategies

Mitigation:

- use semantic top-k retrieval for factual lookup questions
- use deterministic task-intent routing for study transformation requests
- use coverage-aware document context for study transformations, selecting ordered
  chunks across the full document within the existing prompt budget
- reserve multi-pass summarization for a later step if reviewed summary quality still
  needs it after coverage-aware selection
- treat factual questions as lookup by default; a bare word such as `explain` is not
  enough to route a question away from semantic retrieval
- when internet context is enabled, ask for a separate expansion with broader
  background, examples, related concepts, caveats, or current context
- improve broad context later with section-aware context or future multi-pass
  summarization for long documents

## Keep RAG Workflow Coordination In `src/rag/pipeline.py`

Decision: keep core RAG workflow coordination in `src/rag/pipeline.py`.

Reason:

- `app.py` should stay focused on Streamlit app setup and route registration
- the RAG workflow should be reusable outside Streamlit later
- the architecture is easier to test and explain when framework code and application logic are separated

Related boundary:

- Streamlit session state lives in `src/streamlit_app/state.py`
- Streamlit cache/runtime orchestration lives in `src/streamlit_app/runtime.py`
- Streamlit page rendering lives in `src/streamlit_app/pages/`

## Prefer Small Feature Boundaries

Decision: add new features by extending the smallest responsible module or
application object instead of spreading changes across many unrelated files.

Reason:

- broad edits make behavior harder to review, test, and debug
- production-ready learning should build good design habits from the start
- SOLID-style boundaries keep UI, workflow, domain logic, and providers from
  collapsing into each other

Tradeoff:

- some features may need a short design pass before implementation instead of
  immediate code changes

Mitigation:

- design the feature slice before coding
- keep modules focused on one reason to change
- pass explicit application objects across boundaries
- add tests around reusable logic before expanding UI behavior

## Require Explicit Answer Submission

Decision: require an explicit Generate answer action before making an LLM call.

Reason:

- typing or changing a question should not trigger provider calls
- explicit submission makes cost, latency, and answer state predictable in a
  public demo
- the interaction remains simple while making the user intent unambiguous

Tradeoff:

- the experience is one deliberate step less conversational

Mitigation:

- use a Streamlit form or equivalent submit boundary
- store the generated answer in `st.session_state`
- key the answer by the effective input: prompt plus internet-context setting

## Cache Stable Document Work

Decision: cache PDF extraction and document indexing.

Reason:

- Streamlit reruns the app on widget changes
- PDF extraction and document embeddings are expensive relative to UI rendering
- the PDF pipeline should only rerun when the uploaded PDF changes

## Allow Embedding Model Download By Default

Decision: `EMBEDDING_MODEL_LOCAL_ONLY=false` by default.

Reason:

- a fresh clone should work after documented setup
- requiring the embedding model to already exist locally is a hidden assumption

Tradeoff:

- first run may need internet access and time to download the model

Mitigation:

- support `EMBEDDING_MODEL_LOCAL_ONLY=true` for offline/local-only usage

## Keep Documentation Responsibilities Separate

Decision: keep each project document focused on one type of knowledge.

Responsibility map:

- `README.md`: public setup, current status, and pointers to deeper docs
- `docs/architecture.md`: system architecture, data flow, and module boundaries
- `docs/roadmap.md`: production-readiness sequence and future milestones
- `docs/decisions.md`: durable decisions and tradeoffs
- `docs/deployment.md`: deployment instructions and operational caveats
- `AGENTS.md`: Codex-agent prompt and working rules

Reason:

- duplicated docs drift quickly
- future sessions need a clear source of truth
- public users need a concise entry point
- Codex needs instructions without duplicating every architecture detail

## Preserve Raw Model Output In Answer Results

Decision: introduce structured `AnswerResult`, `ModelCall`, `RetrievedSource`,
and `AnswerError` objects while still preserving Gemini's raw answer text.

Reason:
- UI, tracing, tests, persistence, and evaluation need a stable application contract
- preserving raw output keeps debugging possible while the structured contract evolves
- malformed model output should be inspectable without being cached as a
  successful answer

Tradeoff:

- the prompt now asks for JSON, but LLM output can still be malformed or missing
  fields

Mitigation:

- parse model output into explicit PDF answer, internet supplement, source,
  citation, and disagreement fields
- validate parsed PDF source numbers against retrieved PDF sources before
  storing an answer as successful
- keep raw output on `ModelCall`
- represent malformed model output as an application error and avoid caching it
  as a successful answer
- request a non-empty `internet_supplement` when internet context is enabled,
  but use an explicit fallback message if the model returns `null`
- reject internet supplements when internet context is disabled

## Render Grounding Redirects As Readable Citations

Decision: keep raw web citation URLs in answer results, but treat web citations as
experimental until provider grounding metadata is extracted and rendered.

Reason:

- Gemini/Google grounding can return long `vertexaisearch.cloud.google.com`
  redirect URLs
- those URLs are valid link targets but poor reading material
- the user needs clear source boundaries without visual noise
- preserving the original URL keeps traceability and debugging possible
- model-generated URLs are not equivalent to verified provider grounding records

Tradeoff:

- the current app does not yet extract richer grounding metadata such as source
  title, publisher, or final destination URL

Mitigation:

- render Google grounding redirects as stable labels such as
  `Google Search result 1`
- render normal URLs by domain
- keep the original URL as the Markdown link target
- revisit provider metadata extraction when the Gemini client returns structured
  model-call metadata instead of only response text

## Make PDF Evidence Page-Aware

Decision: preserve filename, page number, chunk identity, and chunk text with every
PDF chunk and retrieved source.

Reason:

- numbered prompt sources are difficult for users to audit against the document
- page-level citations make answers more useful and make retrieval failures visible
- source metadata is required for meaningful citation-validity evaluation

Tradeoff:

- the loader, chunker, retrieval models, prompts, and source rendering need a
  coordinated but focused change

Mitigation:

- keep the metadata in explicit application objects
- keep chunks page-bounded so a citation always points to one auditable PDF page
- require every successful PDF answer to cite at least one retrieved PDF source,
  including when an internet supplement is enabled
- show citations such as `Lecture 3, page 12, chunk 2` with a short excerpt
- keep `/study` readable and expose the detailed mapping on `/logic`

## Evaluate Before And After Retrieval Changes

Decision: create a small versioned evaluation suite before changing retrieval or
long-document summarization behavior.

Reason:

- a portfolio project should show that an AI system improved, not only that code
  changed
- deterministic retrieval and citation checks provide a useful baseline before
  introducing an LLM judge
- evaluation discourages adding infrastructure that does not improve outcomes

Initial measurements:

- retrieval hit rate against expected pages or chunks
- citation validity and unsupported-question behavior
- answer faithfulness and summary coverage through reviewed criteria
- latency and recorded failures

Mitigation:

- begin with a small local dataset of representative PDFs and 20-30 questions
- publish baseline and post-change results in `docs/evaluation.md`
- keep LLM-as-judge optional until deterministic checks are stable

Implementation note: begin with versioned original page-aware fixtures for the
deterministic retrieval baseline. Add external PDF fixtures only after their reuse
terms and stable source handling are documented.

Improvement note: coverage-aware selection and narrower transformation phrases improved
the deterministic retrieval baseline from 15/17 to 17/17 scored cases without adding
model calls. Reviewed answer quality remains the next evidence boundary.

CI note: cache the configured embedding model, then run the retrieval benchmark in
local-only mode with a required 17/17 scored-case result. This keeps the CI check
meaningful without making the benchmark itself depend on a live model download.

## Map Provider Failures To Stable Answer Errors

Decision: convert answer-generation exceptions into stable `AnswerError` codes
before they reach the Streamlit pages.

Reason:

- `/study` needs public-demo-friendly messages instead of provider internals
- `/logic` still needs developer details for inspection and debugging
- tests and future persistence should depend on application error codes, not
  Python exception class names

Mitigation:

- keep raw exception details on `AnswerError.details`
- show friendly messages on `/study`
- show codes and details on `/logic`

## Do Not Fake Similarity Scores For Broad Context

Decision: use a missing similarity score for broad document context selected for
study transformations instead of assigning `1.000`.

Reason:

- broad context is selected by task strategy, not semantic nearest-neighbor
  ranking
- showing `similarity 1.000` made study-transformation sources look like perfect
  embedding matches
- source labels should explain why a chunk was included

Tradeoff:

- retrieved source scores are now optional because not every context strategy
  produces a numeric score

Mitigation:

- render semantic retrieval sources with similarity scores
- render study-transformation sources as broad document context
