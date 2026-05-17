from dataclasses import dataclass
from hashlib import sha256

import streamlit as st

from src.rag_pipeline import DocumentIndex


PDF_FILE_NAME_KEY = "pdf_file_name"
PDF_FILE_BYTES_KEY = "pdf_file_bytes"
PDF_FILE_HASH_KEY = "pdf_file_hash"
LOADED_PDF_HASH_KEY = "loaded_pdf_hash"
EXTRACTED_TEXT_KEY = "extracted_text"
DOCUMENT_INDEX_KEY = "document_index"
ANSWER_CACHE_KEY = "answer_cache_key"
ANSWER_KEY = "answer"
ANSWER_ERROR_KEY = "answer_error"


@dataclass(frozen=True)
class CurrentPdf:
    file_name: str
    file_bytes: bytes
    file_hash: str


@dataclass(frozen=True)
class LoadedDocument:
    extracted_text: str
    document_index: DocumentIndex


def remember_uploaded_pdf(uploaded_file) -> None:
    if uploaded_file is None:
        return

    file_bytes = uploaded_file.getvalue()
    file_hash = sha256(file_bytes).hexdigest()

    if st.session_state.get(PDF_FILE_HASH_KEY) == file_hash:
        return

    st.session_state[PDF_FILE_NAME_KEY] = uploaded_file.name
    st.session_state[PDF_FILE_BYTES_KEY] = file_bytes
    st.session_state[PDF_FILE_HASH_KEY] = file_hash
    clear_loaded_document()
    clear_answer()


def get_current_pdf() -> CurrentPdf | None:
    file_name = st.session_state.get(PDF_FILE_NAME_KEY)
    file_bytes = st.session_state.get(PDF_FILE_BYTES_KEY)
    file_hash = st.session_state.get(PDF_FILE_HASH_KEY)

    if file_name is None or file_bytes is None or file_hash is None:
        return None

    return CurrentPdf(
        file_name=file_name,
        file_bytes=file_bytes,
        file_hash=file_hash,
    )


def clear_loaded_document() -> None:
    st.session_state[LOADED_PDF_HASH_KEY] = None
    st.session_state[EXTRACTED_TEXT_KEY] = None
    st.session_state[DOCUMENT_INDEX_KEY] = None


def get_loaded_document_for_current_pdf() -> LoadedDocument | None:
    current_pdf = get_current_pdf()

    if current_pdf is None:
        return None

    if st.session_state.get(LOADED_PDF_HASH_KEY) != current_pdf.file_hash:
        return None

    extracted_text = st.session_state.get(EXTRACTED_TEXT_KEY)
    document_index = st.session_state.get(DOCUMENT_INDEX_KEY)

    if extracted_text is None or document_index is None:
        return None

    return LoadedDocument(
        extracted_text=extracted_text,
        document_index=document_index,
    )


def remember_loaded_document(
    extracted_text: str,
    document_index: DocumentIndex,
) -> None:
    current_pdf = get_current_pdf()

    if current_pdf is None:
        return

    st.session_state[LOADED_PDF_HASH_KEY] = current_pdf.file_hash
    st.session_state[EXTRACTED_TEXT_KEY] = extracted_text
    st.session_state[DOCUMENT_INDEX_KEY] = document_index


def clear_answer() -> None:
    st.session_state[ANSWER_CACHE_KEY] = None
    st.session_state[ANSWER_KEY] = None
    st.session_state[ANSWER_ERROR_KEY] = None


def get_answer_cache_key() -> str | None:
    return st.session_state.get(ANSWER_CACHE_KEY)


def remember_answer_cache_key(answer_cache_key: str) -> None:
    st.session_state[ANSWER_CACHE_KEY] = answer_cache_key


def remember_answer(answer: str) -> None:
    st.session_state[ANSWER_KEY] = answer
    st.session_state[ANSWER_ERROR_KEY] = None


def remember_answer_error(error_message: str) -> None:
    st.session_state[ANSWER_ERROR_KEY] = error_message
    st.session_state[ANSWER_KEY] = None


def get_answer() -> str | None:
    return st.session_state.get(ANSWER_KEY)


def get_answer_error() -> str | None:
    return st.session_state.get(ANSWER_ERROR_KEY)
