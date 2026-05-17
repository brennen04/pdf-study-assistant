# Architecture

This project is a local PDF Study Assistant built as a learning RAG application.

The core product behavior is:

1. Upload a PDF.
2. Extract readable text.
3. Split the text into chunks.
4. Embed the chunks.
5. Embed the user's question.
6. Retrieve the most relevant PDF chunks.
7. Generate a PDF-first answer with Gemini.
8. Optionally add a separate internet supplement with Google Search grounding.

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

## Future Architecture Direction

The current app is a functional production-directed prototype. The prototype
stage is for learning and validating architecture incrementally, while still
preserving clean boundaries that can grow into a production-ready application.
Future implementation should improve reliability and maintainability before
adding too many new product features.

Near-term architecture priorities:

- add tests around pure logic modules before UI tests
- improve error boundaries around PDF loading, embedding model loading, and Gemini calls
- separate rendered PDF-based answer from rendered internet supplement
- expose source chunks and web citations in a clearer result model
- keep provider-specific logic inside client modules such as `gemini_client.py`

If document collections or larger PDFs become a focus, introduce persistence for document indexes before adding a vector database. A vector database should solve a real scale or persistence problem, not be added just because the project uses RAG.
