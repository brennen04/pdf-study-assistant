# Deployment

The public demo is deployed from GitHub to Streamlit Community Cloud. This is the
primary release path because it matches the Streamlit runtime directly and has
successfully run the complete PDF-to-answer workflow.

## Streamlit Community Cloud Contract

Configure the deployment with:

- repository: `brennen04/pdf-study-assistant`
- entry point: `app.py`
- Python: 3.11, matching CI and the Docker image
- secret: `LLM_API_KEY`
- optional setting: `EMBEDDING_MODEL_LOCAL_ONLY=false`

Streamlit installs `requirements.txt` during the build. The first document may take
longer to process while `sentence-transformers` downloads and initializes
`all-MiniLM-L6-v2`; later work in the same running instance can reuse Streamlit's
cached resource.

Add secrets through the Community Cloud app settings, using TOML syntax:

```toml
LLM_API_KEY = "your-real-api-key"
EMBEDDING_MODEL_LOCAL_ONLY = "false"
```

Never commit deployment secrets to `.env`, `.env.example`, source files, or docs.
The application intentionally has no frontend API-key field.

## Release Flow

1. Run the local compile, unit-test, and retrieval-evaluation checks.
2. Push the reviewed revision to GitHub and confirm the `Test and evaluate` workflow.
3. Let Streamlit Community Cloud rebuild from the configured branch.
4. Inspect build logs if dependency installation or model initialization fails.
5. Run the smoke test below against the deployed revision.

This keeps CI and deployment separate: GitHub Actions proves deterministic code and
retrieval behavior, while the deployment smoke test covers cloud secrets, model
download, provider access, and Streamlit runtime behavior.

## Smoke Test

1. Open `/study` and upload a text-based PDF.
2. Confirm extraction, chunking, embedding, and indexing complete.
3. Ask a factual question and verify that the answer cites relevant PDF pages.
4. Ask for a summary and verify coverage beyond the document's opening pages.
5. Ask an unsupported question and verify that the app reports insufficient PDF
   evidence instead of inventing an answer.
6. Enable internet context and verify that the web expansion remains visually
   separate from the PDF answer.
7. Open `/logic` and inspect the selected strategy, chunks, prompt, model metadata,
   raw output, and any application error details.

## Operational Constraints

- Uploaded documents, indexes, and answer history are session-scoped and not durable.
- Text extraction supports text-based PDFs; scanned documents require future OCR.
- Cold starts and first-use model downloads can be slower than local cached runs.
- Community Cloud resource limits make very large PDFs a bounded public-demo case,
  not a high-throughput production workload.
- Web citations use structured Google grounding metadata, but Google can return
  redirect URIs rather than final publisher URLs.

## Legacy Hugging Face Target

The repository retains a `Dockerfile` and manual GitHub workflow for the earlier
Hugging Face Spaces target. That route is not the primary deployment: updates to the
existing Docker Space on CPU Basic were rejected with `402 Payment Required`, an
external platform constraint rather than an application build failure.

The Docker contract remains useful as a portable runtime specification: Python 3.11,
port `8501`, and `streamlit run app.py`. Do not rewrite Space history or add deployment
infrastructure unless Hugging Face becomes an active target again.
