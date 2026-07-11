# AGENTS.md

Guidance for Codex and other coding agents working in this repository.

## Project Context

PDF Study Assistant is a Streamlit RAG study tool. It is a public portfolio demo, but
the target is production-shaped readiness: evidence-grade traceability, debugging
support, evaluation, memory, and user history.

The portfolio standard is to demonstrate measurable improvement to an AI system,
not simply accumulate frameworks or features. A feature is not complete when it is
only implemented; it should be inspectable, tested, and evaluated when its quality
can be measured.

Core product rule:

```text
PDF-grounded by default.
Internet-supplemented only when requested.
Source boundaries always visible.
```

The uploaded PDF is the primary authority. When internet context is requested,
add a clearly separated web-based expansion that can add outside context and
fill gaps in the PDF answer. If PDF and internet sources disagree, surface the
disagreement instead of blending the two.

PDF-grounded does not mean lookup-only. For study transformations such as
summaries, notes, outlines, explanations, flashcards, or study guides, synthesize
from the PDF instead of requiring the requested artifact to already exist in the
document.

## Read First

Use the repository docs as the source of truth and chat history as a secondary source.


1. `README.md` for setup, current status, and the documentation map.
2. `docs/architecture.md` for system shape, data flow, and module boundaries.
3. `docs/roadmap.md` for production-readiness sequencing.
4. `docs/decisions.md` for durable engineering decisions and tradeoffs.
5. `docs/deployment.md` for Streamlit Community Cloud operations and legacy Docker notes.

## Engineering Style

Prefer small, focused changes that keep the app working after each step.

- Design the slice before coding it. Read the relevant docs first, decide
  whether their direction still fits the current code, then implement the
  smallest useful step.
- Avoid full file rewrites when a focused patch can make the change safely.
  Preserve existing structure, wording, and formatting unless there is a clear
  reason to reshape them.
- When editing documentation or code, keep token use low by changing only the
  necessary lines. Reuse existing text when it is still accurate instead of
  deleting and rewriting whole sections.
- Keep Streamlit thin: page rendering, session state, cache wrappers, and
  rerun-safe orchestration belong in focused Streamlit modules.
- Keep reusable RAG behavior in `src/`, especially workflow coordination in
  `src/rag/pipeline.py` or similarly focused modules.
- Add features by extending the smallest responsible boundary. A typical feature
  should not require touching many unrelated files; if it does, pause and
  reconsider the design before editing.
- Follow SOLID-style design where it helps keep the code easy to change:
  focused modules, single-purpose functions, explicit interfaces between
  layers, dependency direction from UI toward application services, and tests
  around reusable logic.
- Make important application data explicit instead of hiding it inside raw
  strings.
- Preserve evidence through the pipeline. Chunks and retrieved sources should keep
  document identity, page number, chunk identity, and text where the source format
  supports them.
- Establish a baseline before changing retrieval or summarization behavior, then
  record whether the change improved the relevant evaluation result.
- Do not add infrastructure before the application model needs it.
- Update public docs only when setup, dependencies, user-visible behavior,
  architecture, or durable decisions change. Do not create extra documentation
  just to narrate routine code changes.
- Keep secrets out of source code. Use `.env.example` for required variables and
  local `.env` files for real values.
- Do not parrot the documents. Use them as direction, then check whether the
  direction still fits the current code and product goal. If you are unsure on
  certain stuff, ask before assuming

## Architecture Priorities

The answer boundary is established. Preserve and extend its explicit application
objects rather than collapsing Gemini output back into a raw string:

- `AnswerResult`
- `ModelCall`
- `RetrievedSource`
- `AnswerError`

Future persistence should follow these application models instead of defining
the model too early through database tables.

Evidence-grade PDF RAG is also established through page-aware chunks, validated PDF
citations, coverage-aware context selection, and a versioned evaluation suite. The
next useful slices are stronger web-grounding metadata and broader reviewed answer
quality. Persistence, vector databases, and orchestration frameworks remain later
options unless a concrete product requirement justifies them.

## Verification

Run lightweight checks after code changes:

```powershell
.\venv\Scripts\python.exe -m compileall app.py src tests
.\venv\Scripts\python.exe -m unittest discover -s tests
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

Record durable design decisions and rationale in `docs/decisions.md`.

If a decision matters for future work, record it in the most specific document
above.

Prefer improving an existing document over adding a new one. If documentation
starts feeling repetitive, consolidate it instead of expanding the set of docs.
