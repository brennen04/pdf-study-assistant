from hashlib import sha256
from io import BytesIO
from time import perf_counter

import streamlit as st

from src.answer.parser import AnswerParseError, parse_answer_output
from src.answer.result import AnswerError, AnswerResult, ModelCall, build_retrieved_sources
from src.answer.validation import AnswerValidationError, validate_pdf_source_numbers
from src.providers.gemini_client import DEFAULT_GEMINI_MODEL, generate_answer
from src.rag.pdf_loader import extract_text_from_pdf
from src.rag.pipeline import (
    DocumentIndex,
    QuestionContext,
    build_document_index,
    build_question_context,
)
from src.streamlit_app.state import (
    get_answer_cache_key,
    get_current_pdf,
    get_loaded_document_for_current_pdf,
    remember_answer_cache_key,
    remember_answer_result,
    remember_loaded_document,
)


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


def load_current_document() -> tuple[str, DocumentIndex] | None:
    current_pdf = get_current_pdf()

    if current_pdf is None:
        st.info("Upload a text-based PDF on the Study page to begin.")
        return None

    loaded_document = get_loaded_document_for_current_pdf()

    if loaded_document is not None:
        return loaded_document.extracted_text, loaded_document.document_index

    with st.spinner("Reading PDF..."):
        extracted_text = extract_text_from_pdf_bytes(current_pdf.file_bytes)

    if not extracted_text.strip():
        st.warning(
            "No text could be extracted. This PDF may be scanned or image-based."
        )
        return None

    with st.spinner("Preparing searchable PDF index..."):
        document_index = get_document_index(extracted_text)

    remember_loaded_document(
        extracted_text=extracted_text,
        document_index=document_index,
    )

    return extracted_text, document_index


def build_answer_cache_key(
    question_context: QuestionContext,
    use_google_search: bool,
) -> str:
    return sha256(
        f"{use_google_search}\n{question_context.answer_prompt}".encode("utf-8")
    ).hexdigest()


def generate_answer_once(
    question_context: QuestionContext,
    use_google_search: bool,
) -> None:
    answer_cache_key = build_answer_cache_key(
        question_context=question_context,
        use_google_search=use_google_search,
    )

    if get_answer_cache_key() == answer_cache_key:
        return

    with st.spinner("Generating PDF-grounded answer..."):
        started_at = perf_counter()
        try:
            answer = generate_answer(
                prompt=question_context.answer_prompt,
                use_google_search=use_google_search,
                model_name=DEFAULT_GEMINI_MODEL,
            )
        except Exception as error:
            latency_seconds = perf_counter() - started_at
            remember_answer_result(
                AnswerResult(
                    question=question_context.question,
                    pdf_answer=None,
                    internet_supplement=None,
                    sources=build_retrieved_sources(
                        question_context.retrieved_chunks
                    ),
                    model_call=ModelCall(
                        provider="google",
                        model_name=DEFAULT_GEMINI_MODEL,
                        prompt=question_context.answer_prompt,
                        use_google_search=use_google_search,
                        latency_seconds=latency_seconds,
                        raw_output=None,
                    ),
                    error=AnswerError(
                        code=type(error).__name__,
                        message=str(error),
                        details=repr(error),
                    ),
                )
            )
        else:
            latency_seconds = perf_counter() - started_at
            model_call = ModelCall(
                provider="google",
                model_name=DEFAULT_GEMINI_MODEL,
                prompt=question_context.answer_prompt,
                use_google_search=use_google_search,
                latency_seconds=latency_seconds,
                raw_output=answer,
            )
            try:
                parsed_answer = parse_answer_output(
                    answer,
                    internet_context_enabled=use_google_search,
                )
                sources = build_retrieved_sources(question_context.retrieved_chunks)
                validate_pdf_source_numbers(
                    parsed_answer=parsed_answer,
                    sources=sources,
                )
            except AnswerParseError as error:
                remember_answer_result(
                    AnswerResult(
                        question=question_context.question,
                        pdf_answer=None,
                        internet_supplement=None,
                        sources=build_retrieved_sources(
                            question_context.retrieved_chunks
                        ),
                        model_call=model_call,
                        error=AnswerError(
                            code="unparseable_model_output",
                            message=str(error),
                            details=answer,
                        ),
                    )
                )
            except AnswerValidationError as error:
                remember_answer_result(
                    AnswerResult(
                        question=question_context.question,
                        pdf_answer=None,
                        internet_supplement=None,
                        sources=build_retrieved_sources(
                            question_context.retrieved_chunks
                        ),
                        model_call=model_call,
                        error=AnswerError(
                            code="invalid_pdf_source_reference",
                            message=str(error),
                            details=answer,
                        ),
                    )
                )
            else:
                remember_answer_result(
                    AnswerResult(
                        question=question_context.question,
                        pdf_answer=parsed_answer.pdf_answer,
                        internet_supplement=parsed_answer.internet_supplement,
                        sources=sources,
                        model_call=model_call,
                        pdf_source_numbers=parsed_answer.pdf_source_numbers,
                        web_citations=parsed_answer.web_citations,
                        disagreement_note=parsed_answer.disagreement_note,
                    )
                )
                remember_answer_cache_key(answer_cache_key)
