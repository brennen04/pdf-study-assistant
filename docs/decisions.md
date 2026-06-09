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

## Use `LLM_API_KEY` Instead Of `GEMINI_API_KEY`

Decision: use the provider-neutral name `LLM_API_KEY`.

Reason:

- the current provider is Gemini
- the app may support other LLM providers later
- the public setup stays less tightly coupled to one provider

## Do Not Collect API Keys In The Frontend

Decision: the web UI does not include an API key input.

Reason:

- infrastructure secrets belong in local configuration
- public repo users should configure `.env`
- frontend controls should represent product behavior, not secret management

## PDF First, Internet Second

Decision: the answer should use the uploaded PDF as the primary source and internet context only as a separate supplement.

Reason:

- the product is a PDF study assistant, not a general web-search chatbot
- the user should be able to distinguish document-grounded information from external information
- disagreements between the PDF and internet sources should be visible instead of blended

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
