# Roadmap

This is one combined roadmap for:

1. building a production-ready PDF Study Assistant, and
2. developing AI Engineer / LLM Engineer / RAG Engineer portfolio skills.

Do not maintain a separate "job roadmap" and "product roadmap." The same
engineering milestones serve both goals when they are sequenced well.

## Delivery Model

This roadmap is not waterfall.

It is an iterative SDLC roadmap:

```text
design a slice
-> implement it
-> test it
-> document it
-> deploy or smoke test it
-> review the next slice
```

Each milestone should leave the app working. Milestones are used for dependency
ordering, not for freezing all requirements up front.

## Product Direction

The production-ready app should support:

- memory: remember documents, questions, answers, and study history
- traceability: show which PDF chunks, prompts, model calls, and sources led to an answer
- debugging: make failures and AI behavior inspectable
- evaluation: compare outputs, inspect grounding quality, and measure regressions
- user history: let learners return to prior documents, questions, answers, and notes

## Engineering Principles

- Build stable domain models before adding persistence.
- Keep UI, runtime state, RAG workflow, provider clients, and storage separate.
- Make important data explicit instead of hiding it inside raw strings.
- Store enough metadata to debug and evaluate AI behavior later.
- Prefer simple infrastructure first, but avoid choices that force a rewrite.
- Add tests around pure logic and data contracts before broad UI tests.
- Keep every milestone deployable or at least locally verifiable.
- Update public docs when setup, behavior, or architecture changes.

## Milestone 1: Core RAG Baseline

Status: mostly complete.

Goal:

```text
PDF -> extracted text -> chunks -> embeddings -> retrieval -> prompt -> answer
```

Completed:

- PDF upload
- text extraction
- chunking
- local embedding generation
- in-memory `DocumentIndex`
- question embedding
- semantic retrieval
- PDF-first prompt construction
- Gemini answer generation
- optional Google Search grounding
- `/study` and `/logic` pages
- Streamlit state/runtime/page separation

Production value:

Proves the core RAG data flow and separates the first major responsibilities:
UI, runtime state, RAG workflow, and provider integration.

AI Engineer relevance:

Demonstrates Python, embeddings, semantic search, prompt construction, LLM API
integration, and RAG fundamentals.

Definition of done:

- user can upload a text-based PDF
- user can ask a question
- app retrieves PDF chunks
- app generates a PDF-first answer
- lightweight tests pass

## Milestone 2: Explicit AI Result Model

Status: in progress.

Goal:

Replace raw answer strings with structured application objects.

Target concepts:

```text
AnswerResult
ModelCall
RetrievedSource
AnswerError
```

The result model should represent:

- question
- PDF answer
- PDF sources
- internet supplement
- web citations
- raw model output
- prompt
- model name
- provider settings
- internet-context setting
- latency
- created timestamp
- error state

Completed first slice:

- `AnswerResult`, `ModelCall`, `RetrievedSource`, and `AnswerError` exist as application objects.
- answer generation stores a structured result instead of a raw answer string.
- `/study` renders from the structured result.
- `/logic` can inspect latest model-call metadata and raw output.

Remaining:

- make PDF answer, internet supplement, and web citations more explicit instead of relying on one raw Gemini answer string
- improve expected failure classification beyond exception class names
- decide whether prompt formatting should produce a more parseable response contract

Production value:

Creates the contract that UI rendering, monitoring, persistence, evaluation,
and future APIs can depend on.

AI Engineer relevance:

Matches job requirements around production LLM apps, traceability, monitoring,
hallucination debugging, and evaluation readiness.

Dependencies:

- Milestone 1

Definition of done:

- answer generation returns a structured result object
- UI renders from the structured result instead of a raw string
- `/logic` can inspect model call metadata and raw output
- tests cover result construction and basic failure cases

## Milestone 3: Error Boundaries

Goal:

Represent expected failures as structured application states.

Failure cases:

- missing API key
- invalid API key
- Gemini timeout or provider failure
- empty model response
- scanned PDF with no extractable text
- embedding model load or download failure
- retrieval with weak or empty matches

Production value:

Users get clear messages, developers get debug details, and tests can assert
stable error behavior.

AI Engineer relevance:

Matches production reliability requirements: robust services, safe failure
modes, and debuggable model workflows.

Dependencies:

- Milestone 2

Definition of done:

- expected errors have stable error codes or types
- user-facing messages are separated from developer details
- tests cover common failure paths

## Milestone 4: AI Traceability And Monitoring

Goal:

Capture enough information to inspect how an answer was produced.

Track:

- document identity
- question
- retrieved chunks
- retrieval scores
- generated prompt
- model name
- provider settings
- internet-context setting
- raw model output
- parsed answer result
- latency
- error details
- timestamp

Production value:

Makes AI behavior inspectable. This is necessary for debugging, evaluation, and
future user history.

AI Engineer relevance:

Matches job requirements around observability, monitoring, model behavior
debugging, cost/latency awareness, and production LLM operations.

Dependencies:

- Milestone 2
- Milestone 3

Definition of done:

- each answer has a trace object or trace fields
- `/logic` shows trace details clearly
- latency and model metadata are captured

## Milestone 5: Persistence And User History

Goal:

Persist study history and model traces beyond one Streamlit session.

Start with an application database before adding a vector database.

Likely first database:

```text
SQLite
```

Possible records:

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

Production value:

Enables memory, user history, debugging over time, and evaluation datasets.

AI Engineer relevance:

Matches job requirements around SQL, backend data modeling, persistence,
traceability, and production system design.

Dependencies:

- Milestone 2
- Milestone 4

Definition of done:

- previous question runs can be stored and loaded
- model call and answer metadata persist locally
- database schema follows application models

## Milestone 6: Source And Citation UX

Goal:

Render evidence clearly.

The UI should separate:

- PDF-based answer
- PDF chunks used
- internet supplement
- web citations
- disagreements between PDF and internet context

Production value:

Improves trust and keeps the product rule visible: PDF first, internet second.

AI Engineer relevance:

Matches job requirements around grounded generation, citation handling,
retrieval quality, and hallucination reduction.

Dependencies:

- Milestone 2
- Milestone 4

Definition of done:

- answer display separates PDF and internet sections
- source chunks are easy to inspect
- web citation metadata has a place in the result model

## Milestone 7: Evaluation Framework

Goal:

Create repeatable ways to check answer quality.

Evaluation should cover:

- retrieval quality
- groundedness against PDF chunks
- whether internet information stays separate
- answer completeness
- citation usefulness
- regression behavior across prompt/model changes

Start simple:

- curated example PDFs
- known questions
- expected source chunks
- manual review notes

Later:

- automated scoring helpers
- model comparison runs
- prompt version tracking

Production value:

Turns answer quality from subjective impressions into reviewable evidence.

AI Engineer relevance:

Directly matches job requirements around LLM evaluation, quality control,
feedback loops, and regression testing.

Dependencies:

- Milestone 4
- Milestone 5

Definition of done:

- repo contains at least one evaluation dataset or example set
- retrieval and answer outputs can be compared across runs
- evaluation notes or scores can be stored

## Milestone 8: Backend API Service

Goal:

Expose the RAG workflow through a backend API so the system is not tied only to
Streamlit.

Likely approach:

```text
Streamlit UI
-> FastAPI service
-> RAG/application services
-> provider clients
-> database
```

Production value:

Creates a more realistic service boundary and lets other clients use the RAG
system later.

AI Engineer relevance:

Matches common job requirements around FastAPI, backend AI services, REST APIs,
service boundaries, and production application architecture.

Dependencies:

- Milestone 2
- Milestone 5

Definition of done:

- API can accept a document or document ID
- API can accept a question
- API returns structured answer results
- Streamlit can remain as a frontend client or demo UI

## Milestone 9: Vector Persistence And Retrieval Infrastructure

Goal:

Persist or scale semantic retrieval when in-memory retrieval becomes limiting.

Possible options:

- SQLite plus stored embeddings for a local baseline
- FAISS for local vector search
- Chroma or Qdrant for vector database learning
- PostgreSQL with pgvector for production-style relational/vector storage

Production value:

Supports larger documents, multiple documents, persistent indexes, and faster
retrieval workflows.

AI Engineer relevance:

Matches RAG/vector database requirements in AI Engineer and LLM Engineer roles.

Dependencies:

- Milestone 5
- real need for persistent or multi-document retrieval

Definition of done:

- retrieval can use persisted embeddings or a vector index
- retrieval quality and latency can be compared against the in-memory baseline
- choice is documented in `docs/decisions.md`

## Milestone 10: CI/CD And Deployment Hardening

Goal:

Make the app safer to change and deploy.

Work:

- GitHub Actions test workflow
- compile and unit test checks
- Docker build check
- deployment smoke test
- environment validation
- clearer startup/runtime errors
- Hugging Face Spaces deployment verification

Production value:

Reduces deployment risk and makes public usage more reliable.

AI Engineer relevance:

Matches job requirements around Docker, CI/CD, cloud deployment, operational
readiness, and production workflows.

Dependencies:

- current Docker/Hugging Face deployment baseline

Definition of done:

- tests run automatically in CI
- Docker build is checked
- deployment instructions are validated

## Milestone 11: Orchestration, Agents, And Tool Use

Goal:

Evaluate whether orchestration frameworks or agent patterns add real value.

Possible exploration:

- LangChain
- LlamaIndex
- LangGraph
- MCP/tool integrations

Production value:

Adds workflow orchestration only if it solves a real product need, such as
multi-step study workflows, tool use, note generation, or evaluation runs.

AI Engineer relevance:

Matches job requirements around agents, LangChain/LangGraph, tool use, and
context orchestration.

Dependencies:

- clear baseline implementation
- explicit result and trace models

Definition of done:

- framework/tooling decision is documented
- any added framework has a clear responsibility
- baseline behavior remains testable

## Milestone 12: Production Hardening

Goal:

Improve reliability for real users.

Work:

- OCR support for scanned PDFs
- multi-document workflows
- stronger security boundaries
- request limits and timeouts
- cost/latency tracking
- dependency review
- user/account model if the app moves beyond local single-user usage
- fresh-clone verification

Production value:

Moves the app from production-directed learning project toward real product
readiness.

AI Engineer relevance:

Matches job requirements around reliability, scalability, security, cost,
latency, and production operations.

Dependencies:

- earlier model, traceability, persistence, and deployment milestones

Definition of done:

- major user-visible failure paths are handled
- app has documented operational assumptions
- deployment is repeatable

## Current Next Milestone

Continue Milestone 2: Explicit AI Result Model.

Why this is next:

- it is the contract for rendering, monitoring, persistence, APIs, and evaluation
- it prevents database schema design from happening too early
- it directly supports traceability and debugging
- it aligns with AI Engineer job requirements around production LLM systems
