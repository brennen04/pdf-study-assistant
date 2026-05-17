import streamlit as st

from src.streamlit_state import get_current_pdf, remember_uploaded_pdf


def render_page_header(title: str, description: str) -> None:
    st.title(title)
    st.write(description)


def render_upload_control() -> None:
    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        key="uploaded_pdf",
    )

    remember_uploaded_pdf(uploaded_file)
    render_current_pdf_status()


def render_current_pdf_status() -> None:
    current_pdf = get_current_pdf()

    if current_pdf is not None:
        st.success(f"Current PDF: {current_pdf.file_name}")
