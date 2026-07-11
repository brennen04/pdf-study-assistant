# Deployment

Primary target: Hugging Face Spaces with the Docker SDK.

Use Docker because the app depends on Streamlit, SentenceTransformers, Torch,
and a local embedding model. Streamlit Community Cloud is possible, but Hugging
Face Spaces is the better first deployment target for this ML-heavy app.

## Current Hosting Constraint

Hugging Face has deprecated its built-in Streamlit SDK, so this app requires a
Docker Space there. The existing Space was previously deployed as Docker, but its
current runtime reports a scheduling failure and both attempted update paths have
been rejected by the remote. This is an external deployment incident; it does not
establish that the application or Docker configuration is invalid.

Do not force-push or rewrite the Space Git history while the remote update failure
is unresolved. Keep the GitHub repository, green CI, and local smoke-test evidence
as the public Portfolio V1 proof in the meantime.

## Required Files

- `Dockerfile`
- `app.py`
- `requirements.txt`
- `src/`
- `.env.example`
- `README.md`
- `docs/`

`README.md` must keep the Hugging Face Space front matter at the top:

```yaml
---
title: PDF Study Assistant
emoji: "\U0001F4DA"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: false
short_description: PDF-grounded RAG study assistant with optional internet context
---
```

## Docker Contract

The Dockerfile should:

- start from Python 3.11
- install `requirements.txt`
- copy the project files
- expose port `8501`
- run `streamlit run app.py`

The Streamlit command disables XSRF protection because Hugging Face serves the
app through its own proxy. Without that setting, deployed file uploads may fail
with browser-side `403` errors.

## Secrets

Set these in Hugging Face Space settings:

```text
LLM_API_KEY=your-real-api-key
EMBEDDING_MODEL_LOCAL_ONLY=false
```

Never commit real secrets in `.env`, `.env.example`, source code, README
examples, or frontend UI fields.

## Deploy

After the remote update path is working, deploy with the Hugging Face HTTP uploader.
Authenticate with a Hugging Face write token:

```powershell
.\venv\Scripts\hf.exe auth login
```

Then upload the local repository files:

```powershell
.\venv\Scripts\hf.exe upload draxnebula/pdf-study-assistant . . --repo-type space --commit-message "Deploy Portfolio V1"
```

Wait for the subsequent Space build to finish.

## Smoke Test

After the Space builds:

1. Open `/study`.
2. Upload a text-based PDF.
3. Confirm the document index prepares successfully.
4. Ask a question.
5. Confirm the answer is PDF-grounded.
6. Enable internet context and confirm the answer includes a separate web-based
   expansion.
7. Open `/logic` and confirm extracted text, chunks, sources, prompt, and answer metadata are inspectable.

## Caveats

- First PDF processing may be slow while the embedding model downloads.
- `sentence-transformers` and `torch` make builds heavy.
- If deployment becomes too slow, consider hosted embeddings, upgraded Space hardware, or persisted indexes.
- Do not add deployment complexity until the app model needs it.
