# PDF Study Assistant

This project is a learning build for a local PDF study assistant using a Retrieval-Augmented Generation (RAG) architecture.

The goal is to understand how modern AI study tools are built step by step, while keeping the code structured like a real software project. Each part of the system has a clear responsibility so the app is easier to test, change, and extend.

## Why We Are Building This

Students often have long lecture notes, textbook chapters, research papers, or revision PDFs. Reading through all of that material manually can be slow, especially when trying to answer a specific question.

This app is being built to:

- upload a PDF
- extract its text
- split the text into smaller chunks
- create semantic embeddings for those chunks
- retrieve the most relevant chunks for a user question
- eventually generate answers grounded in the PDF content

The learning purpose is just as important as the app itself. As we build, we explain the architecture decisions, tradeoffs, and software engineering practices behind each step.

## Current Architecture

The app is intentionally split into small modules instead of placing all logic inside the Streamlit UI.

### `app.py`

This is the Streamlit application entry point.

It handles the user workflow:

- upload a PDF
- show extracted text
- create chunks
- create embeddings
- accept a question
- display the most relevant PDF sections
- generate an answer after the question is submitted

Why: the UI should coordinate the workflow, but it should not contain all business logic. Keeping app orchestration separate from core logic makes the project easier to maintain.

The app caches PDF extraction, chunking, and document embeddings so changing the question does not recompute the whole document pipeline.

### `src/pdf_loader.py`

This module extracts readable text from a PDF.

Why: PDF parsing is its own responsibility. If we later support OCR for scanned PDFs or better page metadata, we can improve this file without rewriting the app.

### `src/chunker.py`

This module splits extracted text into overlapping chunks.

Why: embedding an entire PDF at once is usually too broad and too large. Smaller chunks make retrieval more accurate because the app can find the specific section related to a question.

The overlap helps preserve context across chunk boundaries.

### `src/embedding_client.py`

This module loads a local SentenceTransformer model and converts text into embeddings.

Why: embeddings turn text into vectors that capture semantic meaning. Similar meanings should have similar vectors, which allows the app to search by meaning rather than exact keywords.

The model is cached so it is not reloaded every time embeddings are created.

### `src/retriever.py`

This module ranks PDF chunks by similarity to the user's question.

Why: this is the retrieval step in RAG. Before an AI model can answer from a document, the system first needs to find the most relevant pieces of that document.

Because the embeddings are normalized, cosine similarity can be computed efficiently with a dot product.

### `src/answer_builder.py`

This module builds the grounded prompt that will eventually be sent to a language model.

Why: answer generation should use the retrieved PDF context as the primary source. Internet context can be added later, but it should be clearly separated from the PDF-based answer. Keeping prompt construction in its own module makes the handoff from retrieval to generation explicit and easier to inspect.

## What RAG Means Here

RAG stands for Retrieval-Augmented Generation.

In this project, that means:

1. Load the document.
2. Break it into searchable chunks.
3. Convert chunks into embeddings.
4. Convert the user's question into an embedding.
5. Retrieve the most relevant chunks.
6. Later, send those chunks plus the question to a language model to generate a grounded PDF-first answer.
7. Optionally add internet context as a separate supplement after the PDF-based answer.

Right now, the app performs steps 1 through 5. The next major step is answer generation.
It also previews the grounded prompt for step 6 so we can inspect exactly what context a language model would receive.

## How To Run

Create and activate a virtual environment, then install dependencies:

```powershell
pip install -r requirements.txt
```

Run the Streamlit app:

```powershell
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Gemini API Key

The app can use Gemini to generate a PDF-first answer after retrieving relevant chunks.

Recommended local setup:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and replace the placeholder:

```env
LLM_API_KEY=your-real-api-key
```

Run the app:

```powershell
streamlit run app.py
```

You can also set the key directly in PowerShell:

```powershell
$env:LLM_API_KEY="your-api-key"
streamlit run app.py
```

Do not commit API keys to Git. The real `.env` file is ignored by Git, while `.env.example` is safe to commit as a template.

The API key is intentionally not collected in the web UI. Developers should configure it locally before running the app.

The "Internet context" toggle enables Gemini Google Search grounding. The prompt still tells the model to answer from the PDF first, then add internet information separately when useful.

## Engineering Principles For This Project

As this project grows, we are following these practices:

- Keep modules focused on one responsibility.
- Prefer clear names over clever abstractions.
- Explain why each major change exists.
- Keep UI code separate from reusable application logic.
- Add abstractions only when they reduce real complexity.
- Verify changes with lightweight checks before moving on.
- Build in small steps so each layer is understandable.

## Current Status

Built so far:

- PDF upload
- PDF text extraction
- text chunking
- local embedding generation
- semantic retrieval for user questions
- grounded answer prompt preview
- Gemini answer generation
- cached PDF processing and embeddings

Next likely steps:

- improve answer/source display
- extract Gemini citation metadata when internet grounding is enabled
- show source chunks alongside generated answers
- improve error handling for missing local embedding models
- add tests for chunking and retrieval behavior
- optionally persist document embeddings instead of recalculating them every run
