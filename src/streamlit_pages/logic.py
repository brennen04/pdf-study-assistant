import streamlit as st

from src.streamlit_pages.shared import render_current_pdf_status, render_page_header
from src.streamlit_runtime import get_question_context, load_current_document
from src.streamlit_state import get_answer_result, get_current_pdf


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
        document_index.chunks[0],
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

    if not question.strip():
        return

    question_context = get_question_context(
        question=question.strip(),
        document_index=document_index,
        internet_context_enabled=use_google_search,
    )

    st.write(f"Task intent: {question_context.task_intent.value}")
    st.write(f"Context strategy: {question_context.context_strategy}")

    st.write("PDF sections used:")
    for result_number, (chunk, score) in enumerate(
        question_context.retrieved_chunks,
        start=1,
    ):
        with st.expander(
            f"Result {result_number} - similarity {score:.3f}",
            expanded=result_number == 1,
        ):
            st.write(chunk)

    st.subheader("Prompt")
    st.text_area(
        "LLM prompt",
        question_context.answer_prompt,
        height=350,
    )

    answer_result = get_answer_result()

    if answer_result is None:
        return

    st.subheader("Latest Answer Result")
    st.write(f"Question: {answer_result.question}")

    if answer_result.error:
        st.error(answer_result.error.message)
        st.write(f"Error code: {answer_result.error.code}")
    else:
        st.success("Latest answer generated successfully.")
        st.write("PDF source numbers cited:")
        st.write(answer_result.pdf_source_numbers or [])

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
            st.write(answer_result.web_citations)

        if answer_result.disagreement_note:
            st.write("Disagreement note:")
            st.write(answer_result.disagreement_note)

    model_call = answer_result.model_call
    st.write(f"Provider: {model_call.provider}")
    st.write(f"Model: {model_call.model_name}")
    st.write(f"Internet context enabled: {model_call.use_google_search}")

    if model_call.latency_seconds is not None:
        st.write(f"Latency: {model_call.latency_seconds:.2f} seconds")

    st.write(f"Created at: {model_call.created_at.isoformat()}")

    st.text_area(
        "Raw model output",
        model_call.raw_output or "",
        height=250,
    )
