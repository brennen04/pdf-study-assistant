from hashlib import sha256
from io import BytesIO

import streamlit as st

from src.config import load_environment
from src.gemini_client import generate_answer
from src.pdf_loader import extract_text_from_pdf
from src.rag_pipeline import (
    DocumentIndex,
    QuestionContext,
    build_document_index,
    build_question_context,
)


load_environment()


@st.cache_data(show_spinner=False)
def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    return extract_text_from_pdf(BytesIO(file_bytes))


@st.cache_data(show_spinner=False)
def get_document_index(text: str) -> DocumentIndex:
    return build_document_index(text)


def get_question_context(
    question: str,
    document_index: DocumentIndex,
    internet_context_enabled: bool,
) -> QuestionContext:
    return build_question_context(
        question=question,
        document_index=document_index,
        internet_context_enabled=internet_context_enabled,
    )


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
        document_index = get_document_index(extracted_text)

        st.text_area(
            "PDF text",
            extracted_text[:5000],
            height=400
        )

        st.info(f"Extracted approximately {len(extracted_text):,} characters.")

        st.subheader("Chunk Preview")
        st.write(f"Created {len(document_index.chunks):,} text chunks.")

        st.text_area(
            "First chunk",
            document_index.chunks[0],
            height=250
        )

        embeddings = document_index.embeddings

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
                    question_context = get_question_context(
                        question=question.strip(),
                        document_index=document_index,
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
                        question_context.answer_prompt,
                        height=350,
                    )

                answer_cache_key = sha256(
                    f"{use_google_search}\n{question_context.answer_prompt}".encode(
                        "utf-8"
                    )
                ).hexdigest()

                if st.session_state.get("answer_cache_key") != answer_cache_key:
                    with st.spinner("Generating PDF-first answer..."):
                        try:
                            answer = generate_answer(
                                prompt=question_context.answer_prompt,
                                use_google_search=use_google_search,
                            )
                        except Exception as error:
                            st.session_state.answer_error = str(error)
                            st.session_state.answer = None
                        else:
                            st.session_state.answer_error = None
                            st.session_state.answer = answer

                        st.session_state.answer_cache_key = answer_cache_key

                if st.session_state.get("answer_error"):
                    st.error(st.session_state.answer_error)
                elif st.session_state.get("answer"):
                    st.subheader("Answer")
                    st.write(st.session_state.answer)

                st.write("Most relevant sections:")

                for result_number, (chunk, score) in enumerate(
                    question_context.retrieved_chunks,
                    start=1,
                ):
                    with st.expander(
                        f"Result {result_number} - similarity {score:.3f}",
                        expanded=result_number == 1,
                    ):
                        st.write(chunk)
    else:
        st.warning(
            "No text could be extracted. This PDF may be scanned or image-based."
        )
