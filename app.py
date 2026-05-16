from io import BytesIO

import streamlit as st

from src.answer_builder import build_grounded_answer_prompt
from src.chunker import chunk_text
from src.config import load_environment
from src.embedding_client import embed_texts
from src.gemini_client import generate_answer
from src.pdf_loader import extract_text_from_pdf
from src.retriever import rank_chunks_by_similarity


load_environment()


@st.cache_data(show_spinner=False)
def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    return extract_text_from_pdf(BytesIO(file_bytes))


@st.cache_data(show_spinner=False)
def get_text_chunks(text: str) -> list[str]:
    return chunk_text(text)


@st.cache_data(show_spinner=False)
def get_chunk_embeddings(chunks: tuple[str, ...]) -> list[list[float]]:
    return embed_texts(list(chunks))


@st.cache_data(show_spinner=False)
def get_query_embedding(question: str) -> list[float]:
    return embed_texts([question])[0]


st.set_page_config(
    page_title="PDF Study Assistant",
    page_icon="\U0001F4DA",
    layout="wide"
)

st.title("\U0001F4DA PDF Study Assistant")

st.write(
    "Upload a lecture note PDF and extract its text. "
    "Later, this app will let you ask questions grounded in the PDF."
)

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)

use_google_search = st.toggle(
    "Internet context",
    value=False,
    help="Answer from the PDF first, then supplement with Google Search grounding.",
)
st.caption(
    "Enabled: will add web context after the PDF answer."
    if use_google_search
    else "Disabled: will answer from the PDF context only."
)

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")

    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf_bytes(uploaded_file.getvalue())

    st.subheader("Extracted Text Preview")

    if extracted_text.strip():
        chunks = get_text_chunks(extracted_text)

        st.text_area(
            "PDF text",
            extracted_text[:5000],
            height=400
        )

        st.info(f"Extracted approximately {len(extracted_text):,} characters.")

        st.subheader("Chunk Preview")
        st.write(f"Created {len(chunks):,} text chunks.")

        st.text_area(
            "First chunk",
            chunks[0],
            height=250
        )

        with st.spinner("Generating embeddings for chunks..."):
            embeddings = get_chunk_embeddings(tuple(chunks))

        if embeddings:
            st.subheader("Embedding Summary")
            st.write(f"Generated {len(embeddings):,} embeddings.")
            st.write(f"Each embedding has {len(embeddings[0]):,} dimensions.")

            st.text_area(
                "First embedding preview",
                str(embeddings[0][:10]),
                height=120
            )

            st.subheader("Ask a Question")

            question = st.text_input(
                "Question",
                placeholder="What are the main ideas in this PDF?"
            )

            if question.strip():
                with st.spinner("Finding relevant PDF sections..."):
                    query_embedding = get_query_embedding(question.strip())
                    results = rank_chunks_by_similarity(
                        query_embedding=query_embedding,
                        chunk_embeddings=embeddings,
                        chunks=chunks,
                        top_k=3,
                    )

                answer_prompt = build_grounded_answer_prompt(
                    question=question,
                    retrieved_chunks=results,
                    internet_context_enabled=use_google_search,
                )

                st.subheader("Grounded Answer Draft")
                st.info(
                    "The next step is to send this grounded prompt to a language "
                    "model. For now, we show the exact context that would be used."
                )

                with st.expander("Prompt preview"):
                    st.text_area(
                        "LLM prompt",
                        answer_prompt,
                    height=350,
                    )

                with st.spinner("Generating PDF-first answer..."):
                    try:
                        answer = generate_answer(
                            prompt=answer_prompt,
                            use_google_search=use_google_search,
                        )
                    except Exception as error:
                        st.error(str(error))
                    else:
                        st.subheader("Answer")
                        st.write(answer)

                st.write("Most relevant sections:")

                for result_number, (chunk, score) in enumerate(results, start=1):
                    with st.expander(
                        f"Result {result_number} - similarity {score:.3f}",
                        expanded=result_number == 1,
                    ):
                        st.write(chunk)
    else:
        st.warning(
            "No text could be extracted. This PDF may be scanned or image-based."
        )
