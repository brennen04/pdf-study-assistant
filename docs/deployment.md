# Deployment

This project should be deployed to Hugging Face Spaces first.

Hugging Face Spaces is a good fit because the app is ML-heavy: it uses Streamlit, SentenceTransformers, Torch, and a local embedding model.

## Recommended Target: Hugging Face Spaces With Docker

Use the **Docker SDK** when creating the Space.

The Hugging Face docs note that the older built-in Streamlit SDK path is deprecated in favor of Docker SDK with a Streamlit template. Docker is also a better engineering choice for this project because it makes the runtime explicit.

## Files Required For Deployment

The repo should include:

- `Dockerfile`
- `app.py`
- `requirements.txt`
- `src/`
- `.env.example`
- `README.md`
- `docs/`

`README.md` must start with Hugging Face Space configuration front matter:

```yaml
---
title: PDF Study Assistant
emoji: "\U0001F4DA"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: false
short_description: PDF-first RAG study assistant with optional internet context
---
```

Why: Hugging Face reads the YAML block at the top of `README.md` to decide how the Space should build and run. For this project, `sdk: docker` tells Hugging Face to use the Dockerfile, and `app_port: 8501` matches Streamlit's port.

Do not commit:

- `.env`
- real API keys
- `venv/`
- `__pycache__/`
- local model caches

## Dockerfile Contract

The Dockerfile:

- starts from Python 3.11
- installs dependencies from `requirements.txt`
- copies the project files
- exposes port `8501`
- runs `streamlit run app.py`

Hugging Face Spaces will build this image and run the Streamlit app.

The Docker command disables Streamlit XSRF protection because Hugging Face
Spaces serves Streamlit through its own proxy. With the default Streamlit XSRF
setting, file uploads can fail in the deployed Space with a browser-side `403`
error even though local uploads work.

## Create The Hugging Face Space

1. Go to Hugging Face Spaces.
2. Create a new Space.
3. Choose **Docker** as the SDK.
4. Choose public or private visibility.
5. Push this repository to the Space.

## Configure Secrets

In the Space settings, add these secrets or variables:

```text
LLM_API_KEY=your-real-api-key
EMBEDDING_MODEL_LOCAL_ONLY=false
```

The deployed app should not use `.env`. Hugging Face injects secrets as environment variables.

## Push The App To The Space

You can either push directly to the Space repository or connect from GitHub.

Direct Git flow:

```powershell
git remote add space https://huggingface.co/spaces/<your-username>/<your-space-name>
git push space main
```

If the Space uses a different default branch, push to that branch instead.

## Expected Browser Behavior

After the Space builds successfully:

1. `/study` loads as the main study workflow.
2. Uploading a text-based PDF prepares the document index.
3. Asking a question retrieves relevant PDF sections.
4. The app generates a PDF-first answer.
5. If internet context is enabled, Gemini may add a separate internet supplement.
6. `/logic` shows the learning/debug view for extracted text, chunks, embeddings, retrieved sections, and prompt inspection.

## Deployment Caveats

### First Run May Be Slow

The embedding model may download the first time the app processes a PDF.

That is expected when:

```env
EMBEDDING_MODEL_LOCAL_ONLY=false
```

### Build May Be Heavy

`sentence-transformers` and `torch` are large dependencies.

If the build or runtime is too slow, consider:

- upgrading the Space hardware
- replacing local embeddings with a hosted embedding API
- caching or persisting document indexes later
- reducing dependency pins once the project is more stable

### API Keys

Never place real keys in:

- `.env.example`
- source code
- README examples
- frontend UI fields

Use Hugging Face Space secrets.

## Alternative: Streamlit Community Cloud

Streamlit Community Cloud can also deploy this app, but it may struggle more with ML-heavy dependencies.

If using Streamlit Community Cloud:

1. Create a Streamlit app from the GitHub repo.
2. Set the main file path to `app.py`.
3. Add `LLM_API_KEY` and `EMBEDDING_MODEL_LOCAL_ONLY` as secrets.

## Future Deployment Improvements

Before treating the app as production-ready, add:

- automated tests
- deployment smoke tests
- stronger Gemini API failure handling
- clearer embedding model download errors
- optional persistent storage for document indexes
