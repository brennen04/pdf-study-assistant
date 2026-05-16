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

- render the UI
- load local environment variables
- manage Streamlit widgets
- cache expensive stable document work
- store generated answers in session state
- display extracted text, chunks, prompts, answers, and retrieved sources

`app.py` should stay mostly framework-specific. It should not own the core RAG algorithm.

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
-> pdf_loader.extract_text_from_pdf
-> rag_pipeline.build_document_index
   -> chunker.chunk_text
   -> embedding_client.embed_texts
-> DocumentIndex(chunks, embeddings)

user question
-> rag_pipeline.build_question_context
   -> embedding_client.embed_texts
   -> retriever.rank_chunks_by_similarity
   -> answer_builder.build_grounded_answer_prompt
-> gemini_client.generate_answer
-> Streamlit displays answer and sources
```

## Streamlit State And Caching

Streamlit reruns the script when widgets change. Because of that, expensive stable work must be cached.

Cached stable work:

- PDF bytes to extracted text
- extracted text to `DocumentIndex`

The app should not recompute the whole document pipeline just because the user changes a question or toggles internet context.

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

## Future Architecture Direction

The current app is a functional prototype. Future implementation should improve reliability and maintainability before adding too many new product features.

Near-term architecture priorities:

- add tests around pure logic modules before UI tests
- improve error boundaries around PDF loading, embedding model loading, and Gemini calls
- separate rendered PDF-based answer from rendered internet supplement
- expose source chunks and web citations in a clearer result model
- keep provider-specific logic inside client modules such as `gemini_client.py`

If document collections or larger PDFs become a focus, introduce persistence for document indexes before adding a vector database. A vector database should solve a real scale or persistence problem, not be added just because the project uses RAG.
