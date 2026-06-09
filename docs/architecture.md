# Architecture

This project is a local PDF Study Assistant built as a learning RAG application
on the path to a production-ready study assistant.

The MVP/prototype stage is how we learn and validate the architecture
incrementally. It is not the final product target. The production direction is a
study assistant with memory, traceability, debugging support, evaluation, and
user history.

The core product behavior is:

1. Upload a PDF.
2. Extract readable text.
3. Split the text into chunks.
4. Embed the chunks.
5. Embed the user's question.
6. Retrieve the most relevant PDF chunks.
7. Generate a PDF-first answer with Gemini.
8. Optionally add a separate internet supplement with Google Search grounding.

## Abstract Architecture

At a high level, the app has two major workflows:

1. Document ingestion: turn an uploaded PDF into a searchable document index.
2. Question answering: turn a user question into a PDF-grounded answer.

These workflows are connected by the document index. The index is the prepared
representation of the uploaded PDF: it contains text chunks plus embeddings for
those chunks. Once the index exists, the app can answer multiple questions
without extracting, chunking, and embedding the PDF again.

```text
                         Document ingestion

user uploads PDF
      |
      v
PDF bytes
      |
      v
text extraction
      |
      v
plain text
      |
      v
chunking
      |
      v
text chunks
      |
      v
embedding
      |
      v
document index


                         Question answering

user asks question
      |
      v
question embedding
      |
      v
semantic retrieval against document index
      |
      v
relevant PDF chunks
      |
      v
PDF-first prompt construction
      |
      v
Gemini answer generation
      |
      v
answer + PDF sources
      |
      v
optional separate internet supplement
```

### Architecture Layers

The system is organized into layers. Each layer has a different reason to
change, which is why they should not all live in one file.

```text
User interface layer
  Streamlit pages, controls, routing, answer display, debug/learning views

Application runtime layer
  Streamlit session state, cache wrappers, rerun-safe answer generation

RAG workflow layer
  Build document index, retrieve question context, build grounded prompt

Domain service layer
  PDF loading, text chunking, embedding client, vector retrieval, prompt builder

Provider/integration layer
  Gemini API, optional Google Search grounding, local environment loading
```

The most important boundary is between the UI/runtime layers and the RAG
workflow layer. Streamlit reruns, widgets, and session state are framework
concerns. Chunking, retrieval, prompt construction, and answer-generation
contracts are application concerns. Keeping that boundary clear makes the app
easier to test and easier to move beyond Streamlit later if needed.

The production roadmap includes persistence later, but architecture should first
make the application models explicit. Storage should persist real domain
concepts such as documents, chunks, question runs, retrieved sources, model
calls, answer results, errors, and evaluations.

### Data Ownership

The uploaded PDF passes through several representations:

```text
PDF bytes
-> extracted text
-> text chunks
-> chunk embeddings
-> DocumentIndex
-> retrieved chunks for one question
-> prompt
-> model call
-> answer result
```

Each representation has a different lifetime:

- PDF bytes: kept while the user is working with the current document.
- Extracted text: stable for the current PDF and useful for debugging.
- Text chunks and embeddings: stable for the current PDF and reused across questions.
- Retrieved chunks: specific to one question.
- Prompt: specific to one question and internet-context setting.
- Model call: specific to one prompt, provider, model, and settings.
- Answer result: specific to one model call and should separate PDF answer, internet supplement, citations, and errors.

This is why the app caches document-level work separately from answer
generation. A new question should not rebuild the document index. A page
navigation should not restart extraction or embedding. But a new PDF should
clear the old document and answer state.

The next production-oriented boundary is the answer result. The app should not
permanently treat Gemini output as one raw string. It should turn model output
into an explicit application object that can be rendered, tested, monitored, and
eventually persisted.

## Module Responsibilities

### `app.py`

Streamlit entry point.

Responsibilities:

- load local environment variables
- configure Streamlit page metadata and small app-wide styles
- provide URL-based navigation between `/study` and `/logic`

`app.py` should stay as the entry point only. Page rendering, session-state
document lifecycle, cache wrappers, and answer orchestration should live in
focused Streamlit modules under `src/`.

### `src/streamlit_state.py`

Streamlit session-state boundary.

Responsibilities:

- remember the uploaded PDF bytes, file name, and content hash
- remember the extracted text and prepared `DocumentIndex` for the current PDF
- clear document and answer state when the uploaded PDF changes
- store generated answer text, answer errors, and the current answer cache key

This module is intentionally Streamlit-specific. It keeps raw `st.session_state`
keys centralized instead of scattering string keys through the page code.

### `src/streamlit_runtime.py`

Streamlit runtime services.

Responsibilities:

- wrap PDF text extraction with `st.cache_data`
- wrap document indexing with `st.cache_data`
- load the current PDF into an extracted-text/document-index pair
- build question context through the core RAG pipeline
- generate an answer once for a stable prompt/internet-context key

This module coordinates Streamlit caching and rerun behavior, while the actual
RAG algorithm still lives in `src/rag_pipeline.py`.

### `src/streamlit_pages/`

Streamlit page renderers.

Responsibilities:

- `study.py`: render `/study`, the primary upload/question/answer workflow
- `logic.py`: render `/logic`, the learning/debug page for extracted text, chunks, embeddings, retrieval results, and prompt inspection
- `shared.py`: render small shared UI elements such as the page header and current PDF status

The `/study` page is the primary user workflow: upload a PDF, ask a question,
and read the generated answer. The `/logic` page keeps the learning/debugging
surfaces separate: extracted text preview, chunk preview, embedding preview,
retrieved sources, and prompt inspection.

### `src/rag_pipeline.py`

Core RAG workflow coordination.

Responsibilities:

- build a searchable document index from extracted PDF text
- embed the user question
- retrieve relevant PDF chunks
- build the grounded answer prompt

This module is the boundary between UI code and application behavior.

### `src/pdf_loader.py`

PDF text extraction.

This module currently extracts readable text with `pypdf`. Scanned/image-based PDFs may need OCR later.

### `src/chunker.py`

Text chunking.

The app splits long PDF text into overlapping chunks because retrieval works better on focused passages than on entire documents.

### `src/embedding_client.py`

Embedding model loading and text embedding.

The app uses SentenceTransformers to convert chunks and questions into normalized vectors. The model is cached so it is not repeatedly loaded.

Fresh clones can download the embedding model on first use. Set `EMBEDDING_MODEL_LOCAL_ONLY=true` only when the model is already cached locally and offline-only behavior is desired.

### `src/retriever.py`

Vector similarity ranking.

Given a query embedding, chunk embeddings, and original chunks, this module returns the highest-scoring chunks. Because embeddings are normalized, cosine similarity can be computed with a dot product.

### `src/answer_builder.py`

Prompt construction.

The prompt enforces the product rule:

- answer from the PDF first
- add internet information only as a separate supplement
- clearly state when the PDF context is insufficient
- surface disagreement between PDF and internet context

### `src/gemini_client.py`

Gemini API integration.

This module reads `LLM_API_KEY` from the environment and calls Gemini. Google Search grounding is optional and controlled by the UI toggle.

### `src/config.py`

Local environment loading.

This module loads `.env` so developers can keep API keys out of source code.

## Data Flow

```text
uploaded PDF
-> streamlit_state.remember_uploaded_pdf
-> streamlit_runtime.load_current_document
   -> pdf_loader.extract_text_from_pdf
   -> rag_pipeline.build_document_index
   -> chunker.chunk_text
   -> embedding_client.embed_texts
-> DocumentIndex(chunks, embeddings)

user question
-> streamlit_runtime.get_question_context
   -> rag_pipeline.build_question_context
   -> embedding_client.embed_texts
   -> retriever.rank_chunks_by_similarity
   -> answer_builder.build_grounded_answer_prompt
-> streamlit_runtime.generate_answer_once
   -> gemini_client.generate_answer
-> /study displays answer and sources
```

## Streamlit State And Caching

Streamlit reruns the script when widgets change. Because of that, expensive stable work must be cached.

Cached stable work:

- PDF bytes to extracted text
- extracted text to `DocumentIndex`

The app should not recompute the whole document pipeline just because the user changes a question or toggles internet context.

The uploaded PDF bytes, file name, extracted text, and prepared document index
are stored in Streamlit session state for the current PDF hash. This keeps the
selected document available when the user navigates between `/study` and
`/logic` without restarting the visible loading flow. The cached extraction and
indexing functions remain underneath as a second layer of protection against
repeated expensive work for the same PDF content.

LLM calls are guarded with a stable answer key in `st.session_state`. The app generates immediately after a question is submitted, but it should not repeatedly call Gemini for the same question, retrieved context, and internet toggle.

## UI Direction

This is a study tool, not a marketing site.

The interface should feel:

- clear
- calm
- practical
- focused on reading and learning
- easy to inspect while debugging

During learning mode, transparent intermediate outputs are useful: extracted text preview, chunk preview, prompt preview, retrieved sources, and answer output.

Those intermediate outputs live on the `/logic` page so the main `/study` page can
stay focused on the task a learner would perform repeatedly: ask a question and
read the answer.

## Architecture Priorities

The next architecture boundary is the answer result. The app should move from a
raw Gemini string toward explicit answer result and model-call objects.

The roadmap in `docs/roadmap.md` owns the full implementation sequence. This
file owns the system shape and current module boundaries.
