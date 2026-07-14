import streamlit as st

from src.answer.result import ModelCall
from src.answer.web_citations import format_web_citation
from src.streamlit_app.pages.shared import render_current_pdf_status, render_page_header
from src.streamlit_app.runtime import get_question_context, load_current_document
from src.streamlit_app.state import (
    get_answer_result,
    get_current_pdf,
    get_latest_internet_context_enabled,
    get_latest_question,
    remember_question_settings,
)


def render_logic_page() -> None:
    render_page_header(
        "RAG Logic",
        "Inspect the intermediate data behind the answer: extracted text, chunks, "
        "embeddings, retrieved sources, and the final prompt.",
    )

    if get_current_pdf() is None:
        st.info("Upload a PDF on the Study page, then return here to inspect it.")
        return

    render_current_pdf_status()
    loaded_document = load_current_document()

    if loaded_document is None:
        return

    extracted_text, document_index = loaded_document

    st.subheader("Extracted Text")
    st.info(f"Extracted approximately {len(extracted_text):,} characters.")
    st.text_area(
        "PDF text preview",
        extracted_text[:5000],
        height=400,
    )

    st.subheader("Chunks")
    st.write(f"Created {len(document_index.chunks):,} text chunks.")
    st.text_area(
        "First chunk",
        document_index.chunks[0].text,
        height=250,
    )

    embeddings = document_index.embeddings

    st.subheader("Embeddings")
    if embeddings:
        st.write(f"Generated {len(embeddings):,} embeddings.")
        st.write(f"Each embedding has {len(embeddings[0]):,} dimensions.")
        st.text_area(
            "First embedding preview",
            str(embeddings[0][:10]),
            height=120,
        )
    else:
        st.warning("No embeddings were generated.")

    st.subheader("Question Pipeline")
    answer_result = get_answer_result()

    if answer_result is not None:
        remember_question_settings(
            question=answer_result.question,
            internet_context_enabled=answer_result.internet_context_requested,
        )
        if st.session_state.get("logic_synced_answer_question") != answer_result.question:
            st.session_state["logic_question"] = answer_result.question
            st.session_state["logic_internet_context"] = (
                answer_result.internet_context_requested
            )
            st.session_state["logic_synced_answer_question"] = answer_result.question

    st.session_state.setdefault(
        "logic_internet_context",
        get_latest_internet_context_enabled(),
    )
    st.session_state.setdefault("logic_question", get_latest_question())

    use_google_search = st.toggle(
        "Internet context for prompt",
        value=False,
        key="logic_internet_context",
        help="Shows how the prompt changes when internet context is enabled.",
    )
    question = st.text_input(
        "Question to inspect",
        placeholder="What are the main ideas in this PDF?",
        key="logic_question",
    )

    remember_question_settings(
        question=question,
        internet_context_enabled=use_google_search,
    )

    if not question.strip():
        return

    question_context = get_question_context(
        question=question.strip(),
        document_index=document_index,
    )

    st.write(f"Task intent: {question_context.task_intent.value}")
    st.write(f"Context strategy: {question_context.context_strategy}")

    st.write("PDF sections used:")
    for result_number, (chunk, score) in enumerate(
        question_context.retrieved_chunks,
        start=1,
    ):
        source_label = (
            f"similarity {score:.3f}"
            if score is not None
            else "broad document context"
        )
        with st.expander(
            f"Result {result_number} - {chunk.filename}, page {chunk.page_number}, "
            f"chunk {chunk.chunk_id} - {source_label}",
            expanded=result_number == 1,
        ):
            st.write(chunk.text)

    st.subheader("PDF Answer Prompt")
    st.text_area(
        "PDF-only LLM prompt",
        question_context.answer_prompt,
        height=350,
    )

    if answer_result is None:
        return

    st.subheader("Latest Answer Result")
    st.write(f"Question: {answer_result.question}")

    if answer_result.error:
        st.error(answer_result.error.message)
        st.write(f"Error code: {answer_result.error.code}")
        if answer_result.error.details:
            st.text_area(
                "Error details",
                answer_result.error.details,
                height=120,
            )
    else:
        st.success("Latest answer generated successfully.")
        cited_sources = [
            source
            for source in answer_result.sources
            if source.source_number in answer_result.pdf_source_numbers
        ]
        st.write("PDF evidence cited:")
        for source in cited_sources:
            st.write(
                f"Source {source.source_number}: {source.filename}, "
                f"page {source.page_number}, chunk {source.chunk_id}"
            )

        st.text_area(
            "Parsed PDF answer",
            answer_result.pdf_answer or "",
            height=180,
        )

        st.text_area(
            "Parsed internet supplement",
            answer_result.internet_supplement or "",
            height=140,
        )

        if answer_result.web_citations:
            st.write("Web citations:")
            for citation_number, citation in enumerate(
                answer_result.web_citations,
                start=1,
            ):
                st.markdown(format_web_citation(citation, citation_number))

        if answer_result.disagreement_note:
            st.write("Disagreement note:")
            st.write(answer_result.disagreement_note)

        if answer_result.internet_error:
            st.warning(answer_result.internet_error.message)
            st.write(f"Internet error code: {answer_result.internet_error.code}")
            if answer_result.internet_error.details:
                st.text_area(
                    "Internet error details",
                    answer_result.internet_error.details,
                    height=120,
                )

    st.subheader("PDF Model Call")
    _render_model_call(answer_result.model_call, "PDF")

    if answer_result.internet_model_call is not None:
        st.subheader("Internet Supplement Model Call")
        _render_model_call(answer_result.internet_model_call, "Internet")


def _render_model_call(model_call: ModelCall, label: str) -> None:
    st.write(f"Provider: {model_call.provider}")
    st.write(f"Model: {model_call.model_name}")
    st.write(f"Google Search enabled: {model_call.use_google_search}")

    if model_call.latency_seconds is not None:
        st.write(f"Latency: {model_call.latency_seconds:.2f} seconds")

    st.write(f"Created at: {model_call.created_at.isoformat()}")

    st.text_area(
        f"{label} prompt",
        model_call.prompt,
        height=250,
    )

    st.text_area(
        f"{label} raw model output",
        model_call.raw_output or "",
        height=250,
    )
