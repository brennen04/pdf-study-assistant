# AGENTS.md

Guidance for Codex and other coding agents working in this repository.

## Project Context

PDF Study Assistant is a Streamlit RAG study tool. It is a learning project, but
the target is production readiness: memory, traceability, debugging support,
evaluation, and user history.

Core product rule:

```text
PDF first, internet second.
```

Answers should use the uploaded PDF as the primary source. Internet information
may be added only as a clearly separated supplement. If PDF and internet sources
disagree, surface the disagreement instead of blending the two.

## Read First

Use the repository docs as the source of truth and chat history as secondary source

1. `README.md` for setup, current status, and the documentation map.
2. `docs/architecture.md` for system shape, data flow, and module boundaries.
3. `docs/roadmap.md` for production-readiness sequencing.
4. `docs/decisions.md` for durable engineering decisions and tradeoffs.
5. `docs/deployment.md` for Hugging Face Spaces deployment notes.

## Engineering Style

Prefer small, focused changes that keep the app working after each step.

- Keep Streamlit thin: page rendering, session state, cache wrappers, and
  rerun-safe orchestration belong in focused Streamlit modules.
- Keep reusable RAG behavior in `src/`, especially workflow coordination in
  `src/rag_pipeline.py` or similarly focused modules.
- Make important application data explicit instead of hiding it inside raw
  strings.
- Do not add infrastructure before the application model needs it.
- Update public docs when setup, dependencies, behavior, or architecture
  changes.
- Keep secrets out of source code. Use `.env.example` for required variables and
  local `.env` files for real values.

## Architecture Priorities

The next production-oriented boundary is the answer result. Avoid permanently
treating Gemini output as one raw string. Prefer explicit application objects
for concepts such as:

- `AnswerResult`
- `ModelCall`
- `RetrievedSource`
- `AnswerError`

Future persistence should follow these application models instead of defining
the model too early through database tables.

## Verification

Run lightweight checks after code changes:

```powershell
python -m compileall app.py src tests
python -m unittest discover -s tests
```

As the project grows, add tests around pure logic first: chunking, retrieval,
prompt construction, pipeline behavior, result models, error mapping, and empty
input handling.

## Documentation Rules

Keep documentation responsibilities separate:

- `README.md`: public setup, current status, and links to deeper docs.
- `AGENTS.md`: working instructions for coding agents.
- `docs/architecture.md`: architecture, data flow, and module boundaries.
- `docs/roadmap.md`: planned sequencing and milestones.
- `docs/decisions.md`: durable decisions and tradeoffs.
- `docs/deployment.md`: deployment-specific instructions.

If a decision matters for future work, record it in the most specific document
above.
