# Evaluation

This document records how the project measures retrieval quality before and after
RAG changes. It separates deterministic checks from model-dependent review so the
repository does not present unstable LLM behavior as a reproducible metric.

## Current Dataset

`evals/dataset.py` contains three original, page-aware fixture documents: a short
cyber-hygiene guide, a medium explainable-AI guide, and a longer AI-governance
guide. They are intentionally original text fixtures so the baseline is versioned,
rights-clear, and reproducible without downloading external data.

The current corpus exercises retrieval and summary-context coverage. It does not yet
claim to evaluate PDF layout extraction against external source PDFs; loader behavior
is covered separately by focused tests.

## Deterministic Baseline

Run:

```powershell
$env:EMBEDDING_MODEL_LOCAL_ONLY='true'
.\venv\Scripts\python.exe -m evals.run_retrieval
```

Run this after the configured embedding model is cached locally. The command runs the
current local-embedding retrieval pipeline against the versioned cases and reports:

- retrieval hit rate for answerable and study-transformation cases
- expected and retrieved page numbers for every case
- unsupported-question case count, kept separate from retrieval hit rate

Citation validity is enforced through deterministic application tests: a successful
PDF answer must cite at least one retrieved PDF source, and every cited source number
must refer to retrieved evidence.

GitHub Actions runs the same command with `--require-perfect`, so CI fails if any
scored retrieval case regresses.

## Before: Baseline Results

Baseline run: 2026-07-10, using the cached configured local embedding model.

| Metric | Result |
| --- | ---: |
| Versioned cases | 20 |
| Scored retrieval cases | 17 |
| Passed retrieval cases | 15 |
| Retrieval hit rate | 88.24% |
| Unsupported-question cases | 3, tracked separately |
| Average question-context latency | 0.011 seconds |

The latency is machine-specific and excludes initial model loading and document
indexing. It is useful as a baseline for later changes on the same environment, not as
a public performance claim.

Two cases failed:

1. `long-summary` expected early, middle, and late-page coverage (pages 1, 6, and 12),
   but the current broad-context strategy supplies only the first eight chunks.
2. `long-transparency` is a factual question about page 12, but the word `explain`
   routes it to the broad-context strategy. That confirms the current intent classifier
   is too broad for some factual questions.

## After: Coverage-Aware Retrieval Results

After replacing first-eight-chunk selection with ordered coverage-aware selection and
removing the bare `explain` transformation trigger, the same command produced:

| Metric | Before | After |
| --- | ---: | ---: |
| Scored retrieval cases | 17 | 17 |
| Passed retrieval cases | 15 | 17 |
| Retrieval hit rate | 88.24% | 100.00% |
| Average question-context latency | 0.011 seconds | 0.0106 seconds |

Both previously failing cases now pass:

- `long-summary` receives coverage that includes pages 1, 6, and 12.
- `long-transparency` uses semantic top-k retrieval and finds page 12.

This demonstrates an improvement to deterministic context selection and intent routing.
It does not yet claim that final Gemini summaries are more faithful or more helpful;
that remains a reviewed criterion below.

## Reviewed Criteria

Run this small manual review against a real text-based PDF in the app before making a
public faithfulness claim. Do not commit a private uploaded PDF or raw model output.

| Scenario | What to check |
| --- | --- |
| Factual lookup | Answer is faithful and cited pages support it. |
| Factual `explain` question | Semantic retrieval finds the relevant later page. |
| Summary / main ideas | Answer covers early, middle, and late material. |
| Unsupported question | Answer says the PDF lacks evidence rather than inventing it. |
| Internet context on | Web supplement remains separate from the PDF answer. |
| Internet context off | No web content or web citations appear. |

Record only an aggregate pass/fail count and concise limitations in this document.
The review assesses:

- PDF-answer faithfulness
- unsupported-question handling
- separation of PDF answers from internet supplements
- summary coverage across early, middle, and late pages

LLM-as-judge evaluation is intentionally deferred until the deterministic baseline is
stable.
