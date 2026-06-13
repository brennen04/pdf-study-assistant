import streamlit as st

from src.streamlit_pages.shared import render_page_header, render_upload_control
from src.streamlit_runtime import (
    generate_answer_once,
    get_question_context,
    load_current_document,
)
from src.streamlit_state import get_answer_result


def render_study_page() -> None:
    render_page_header(
        "\U0001F4DA PDF Study Assistant",
        "Upload a PDF, ask a study question, and get an answer grounded in the "
        "document.",
    )

    render_upload_control()

    use_google_search = st.toggle(
        "Internet context",
        value=False,
        key="study_internet_context",
        help="Answer from the PDF, then supplement separately with Google Search grounding.",
    )
    st.caption(
        "Enabled: will add web context after the PDF answer."
        if use_google_search
        else "Disabled: will answer from the PDF context only."
    )

    loaded_document = load_current_document()

    if loaded_document is None:
        return

    _, document_index = loaded_document

    question = st.text_input(
        "Question",
        placeholder="What are the main ideas in this PDF?",
        key="study_question",
    )

    if not question.strip():
        return

    with st.spinner("Finding relevant PDF sections..."):
        question_context = get_question_context(
            question=question.strip(),
            document_index=document_index,
            internet_context_enabled=use_google_search,
        )

    generate_answer_once(
        question_context=question_context,
        use_google_search=use_google_search,
    )

    answer_result = get_answer_result()

    if answer_result and answer_result.error:
        st.error(answer_result.error.message)
    elif answer_result and answer_result.pdf_answer:
        st.subheader("PDF answer")
        st.write(answer_result.pdf_answer)

        if answer_result.disagreement_note:
            st.subheader("Disagreement note")
            st.write(answer_result.disagreement_note)

        if answer_result.internet_supplement:
            st.subheader("Internet supplement")
            st.write(answer_result.internet_supplement)

            if answer_result.web_citations:
                st.markdown("**Web citations**")
                for citation in answer_result.web_citations:
                    st.write(citation)

    with st.expander("PDF sources used"):
        sources = answer_result.sources if answer_result else []
        for source in sources:
            st.markdown(
                f"**Source {source.source_number} - "
                f"similarity {source.similarity:.3f}**"
            )
            st.write(source.text)
