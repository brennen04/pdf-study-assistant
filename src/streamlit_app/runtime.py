from hashlib import sha256
from io import BytesIO
from time import perf_counter

import streamlit as st

from src.answer.errors import map_answer_generation_error
from src.answer.builder import build_internet_supplement_prompt
from src.answer.parser import (
    AnswerParseError,
    parse_answer_output,
    parse_internet_supplement_output,
)
from src.answer.result import (
    AnswerError,
    AnswerResult,
    ModelCall,
    WebCitation,
    build_retrieved_sources,
)
from src.answer.validation import (
    AnswerValidationError,
    MissingPdfSourceReferenceError,
    validate_pdf_source_numbers,
)
from src.providers.gemini_client import DEFAULT_GEMINI_MODEL, generate_answer
from src.rag.document import PdfPage
from src.rag.pdf_loader import extract_pages_from_pdf
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


ANSWER_WORKFLOW_VERSION = "two-stage-grounding-metadata-v1"


@st.cache_data(show_spinner=False)
def extract_pages_from_pdf_bytes(file_bytes: bytes) -> list[PdfPage]:
    return extract_pages_from_pdf(BytesIO(file_bytes))


@st.cache_data(show_spinner=False)
def get_document_index(
    pages: list[PdfPage],
    document_id: str,
    filename: str,
) -> DocumentIndex:
    return build_document_index(
        pages,
        document_id=document_id,
        filename=filename,
    )


def get_question_context(
    question: str,
    document_index: DocumentIndex,
) -> QuestionContext:
    return build_question_context(
        question=question,
        document_index=document_index,
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
        pages = extract_pages_from_pdf_bytes(current_pdf.file_bytes)
        extracted_text = "\n\n".join(page.text for page in pages)

    if not extracted_text.strip():
        st.warning(
            "No text could be extracted. This PDF may be scanned or image-based."
        )
        return None

    with st.spinner("Preparing searchable PDF index..."):
        document_index = get_document_index(
            pages,
            document_id=current_pdf.file_hash,
            filename=current_pdf.file_name,
        )

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
        (
            f"{ANSWER_WORKFLOW_VERSION}\n{DEFAULT_GEMINI_MODEL}\n"
            f"{use_google_search}\n"
            f"{question_context.answer_prompt}"
        ).encode("utf-8")
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

    sources = build_retrieved_sources(question_context.retrieved_chunks)

    with st.spinner("Generating answer..."):
        pdf_started_at = perf_counter()
        try:
            pdf_response = generate_answer(
                prompt=question_context.answer_prompt,
                use_google_search=False,
                model_name=DEFAULT_GEMINI_MODEL,
            )
        except Exception as error:
            pdf_model_call = ModelCall(
                provider="google",
                model_name=DEFAULT_GEMINI_MODEL,
                prompt=question_context.answer_prompt,
                use_google_search=False,
                latency_seconds=perf_counter() - pdf_started_at,
                raw_output=None,
            )
            remember_answer_result(
                AnswerResult(
                    question=question_context.question,
                    pdf_answer=None,
                    internet_supplement=None,
                    sources=sources,
                    model_call=pdf_model_call,
                    error=map_answer_generation_error(error),
                    internet_context_requested=use_google_search,
                )
            )
            return

        pdf_output = pdf_response.text

        pdf_model_call = ModelCall(
            provider="google",
            model_name=DEFAULT_GEMINI_MODEL,
            prompt=question_context.answer_prompt,
            use_google_search=False,
            latency_seconds=perf_counter() - pdf_started_at,
            raw_output=pdf_output,
        )

        try:
            parsed_answer = parse_answer_output(
                pdf_output,
                internet_context_enabled=False,
            )
            validate_pdf_source_numbers(
                parsed_answer=parsed_answer,
                sources=sources,
            )
        except AnswerParseError as error:
            answer_error = AnswerError(
                code="unparseable_model_output",
                message=str(error),
                details=pdf_output,
            )
        except MissingPdfSourceReferenceError:
            answer_error = AnswerError(
                code="missing_pdf_source_reference",
                message=(
                    "I couldn't verify a PDF-grounded answer because the "
                    "model did not identify the PDF excerpts it used. Try "
                    "rephrasing the question or check whether the topic "
                    "appears in the document."
                ),
                details=pdf_output,
            )
        except AnswerValidationError as error:
            answer_error = AnswerError(
                code="invalid_pdf_source_reference",
                message=str(error),
                details=pdf_output,
            )
        else:
            answer_error = None

        if answer_error is not None:
            remember_answer_result(
                AnswerResult(
                    question=question_context.question,
                    pdf_answer=None,
                    internet_supplement=None,
                    sources=sources,
                    model_call=pdf_model_call,
                    error=answer_error,
                    internet_context_requested=use_google_search,
                )
            )
            return

        internet_supplement = None
        web_citations: list[WebCitation] = []
        disagreement_note = None
        internet_model_call = None
        internet_error = None

        if use_google_search:
            internet_prompt = build_internet_supplement_prompt(
                question=question_context.question,
                pdf_answer=parsed_answer.pdf_answer,
            )
            internet_started_at = perf_counter()
            try:
                internet_response = generate_answer(
                    prompt=internet_prompt,
                    use_google_search=True,
                    model_name=DEFAULT_GEMINI_MODEL,
                )
            except Exception as error:
                internet_model_call = ModelCall(
                    provider="google",
                    model_name=DEFAULT_GEMINI_MODEL,
                    prompt=internet_prompt,
                    use_google_search=True,
                    latency_seconds=perf_counter() - internet_started_at,
                    raw_output=None,
                )
                internet_error = map_answer_generation_error(error)
            else:
                internet_output = internet_response.text
                internet_model_call = ModelCall(
                    provider="google",
                    model_name=DEFAULT_GEMINI_MODEL,
                    prompt=internet_prompt,
                    use_google_search=True,
                    latency_seconds=perf_counter() - internet_started_at,
                    raw_output=internet_output,
                )
                try:
                    parsed_supplement = parse_internet_supplement_output(
                        internet_output
                    )
                except AnswerParseError as error:
                    internet_error = AnswerError(
                        code="unparseable_internet_supplement",
                        message=(
                            "The PDF answer was verified, but the separate internet "
                            "supplement could not be read. Try generating it again."
                        ),
                        details=f"{error}\n\n{internet_output}",
                    )
                else:
                    internet_supplement = parsed_supplement.internet_supplement
                    web_citations = internet_response.web_citations
                    disagreement_note = parsed_supplement.disagreement_note

        remember_answer_result(
            AnswerResult(
                question=question_context.question,
                pdf_answer=parsed_answer.pdf_answer,
                internet_supplement=internet_supplement,
                sources=sources,
                model_call=pdf_model_call,
                pdf_source_numbers=parsed_answer.pdf_source_numbers,
                web_citations=web_citations,
                disagreement_note=disagreement_note,
                internet_context_requested=use_google_search,
                internet_model_call=internet_model_call,
                internet_error=internet_error,
            )
        )

        if internet_error is None:
            remember_answer_cache_key(answer_cache_key)
