# Decisions

This file records important project decisions and the reasoning behind them.

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
and should appear only as a clearly separated supplement when requested. Source
boundaries must remain visible.

Reason:

- the product is a PDF study assistant, not a general web-search chatbot
- the user should be able to distinguish document-grounded information from external information
- disagreements between the PDF and internet sources should be visible instead of blended
- study transformations such as summaries, notes, outlines, explanations, and
  flashcards should synthesize from the PDF instead of requiring that artifact
  to already exist in the document

Tradeoff:

- different question types need different PDF-grounded context strategies

Mitigation:

- use semantic top-k retrieval for factual lookup questions
- use deterministic task-intent routing for study transformation requests
- use broad document context for study transformations as the first simple
  strategy
- improve broad context later with section-aware context or future multi-pass
  summarization for long documents

## Use `src/rag_pipeline.py`

Decision: move core RAG workflow coordination into `src/rag_pipeline.py`.

Reason:

- `app.py` should stay focused on Streamlit app setup and route registration
- the RAG workflow should be reusable outside Streamlit later
- the architecture is easier to test and explain when framework code and application logic are separated

Related boundary:

- Streamlit session state lives in `src/streamlit_state.py`
- Streamlit cache/runtime orchestration lives in `src/streamlit_runtime.py`
- Streamlit page rendering lives in `src/streamlit_pages/`

## Generate Immediately, But Dedupe LLM Calls

Decision: generate an answer as soon as the user submits a question, without a separate Ask/Generate button.

Reason:

- this matches the desired user experience
- the app should feel direct and conversational

Tradeoff:

- Streamlit reruns can accidentally repeat API calls

Mitigation:

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
- keep raw output on `ModelCall`
- represent malformed model output as an application error and avoid caching it
  as a successful answer
- require a non-empty `internet_supplement` when internet context is enabled,
  and reject internet supplements when internet context is disabled
