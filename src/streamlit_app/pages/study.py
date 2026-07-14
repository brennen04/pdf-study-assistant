import streamlit as st

from src.answer.web_citations import format_web_citation
from src.streamlit_app.pages.shared import render_page_header, render_upload_control
from src.streamlit_app.runtime import (
    generate_answer_once,
    get_question_context,
    load_current_document,
)
from src.streamlit_app.state import (
    get_answer_result,
    get_latest_internet_context_enabled,
    get_latest_question,
    remember_question_settings,
)


def render_study_page() -> None:
    render_page_header(
        "\U0001F4DA PDF Study Assistant",
        "Upload a PDF, ask a study question, and get an answer grounded in the "
        "document.",
    )

    render_upload_control()

    loaded_document = load_current_document()

    if loaded_document is None:
        return

    _, document_index = loaded_document

    st.session_state.setdefault("study_question", get_latest_question())
    st.session_state.setdefault(
        "study_internet_context",
        get_latest_internet_context_enabled(),
    )

    with st.form("study_question_form", enter_to_submit=False):
        question = st.text_input(
            "Question",
            placeholder="Ask a question regarding the PDF content",
            key="study_question",
        )
        use_google_search = st.toggle(
            "Internet context",
            value=False,
            key="study_internet_context",
            help="Answer from the PDF, then supplement separately with Google Search grounding.",
        )
        submitted = st.form_submit_button("Generate answer")

    st.caption(
        "Enabled: will validate the PDF answer, then add web context separately."
        if use_google_search
        else "Disabled: will answer from the PDF context only."
    )

    if submitted:
        remember_question_settings(
            question=question,
            internet_context_enabled=use_google_search,
        )

        if not question.strip():
            st.warning("Enter a question before generating an answer.")
        else:
            with st.spinner("Finding relevant PDF sections..."):
                question_context = get_question_context(
                    question=question.strip(),
                    document_index=document_index,
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
                for citation_number, citation in enumerate(
                    answer_result.web_citations,
                    start=1,
                ):
                    st.markdown(format_web_citation(citation, citation_number))

        if answer_result.internet_error:
            st.warning(answer_result.internet_error.message)

    with st.expander("PDF sources used"):
        sources = answer_result.sources if answer_result else []
        if answer_result and answer_result.pdf_source_numbers:
            sources = [
                source
                for source in sources
                if source.source_number in answer_result.pdf_source_numbers
            ]
        for source in sources:
            source_label = (
                f"similarity {source.similarity:.3f}"
                if source.similarity is not None
                else "broad document context"
            )
            st.markdown(
                f"**Source {source.source_number} - {source.filename}, "
                f"page {source.page_number}, chunk {source.chunk_id} - "
                f"{source_label}**"
            )
            excerpt = source.text[:500]
            st.write(f"{excerpt}{'...' if len(source.text) > len(excerpt) else ''}")
