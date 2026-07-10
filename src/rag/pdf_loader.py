from pypdf import PdfReader
from typing import BinaryIO

from src.rag.document import PdfPage


def extract_pages_from_pdf(file: BinaryIO) -> list[PdfPage]:
    """Extract readable text while preserving original PDF page numbers."""
    reader = PdfReader(file)
    pages: list[PdfPage] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text and text.strip():
            pages.append(PdfPage(page_number=page_number, text=text.strip()))

    return pages


def extract_text_from_pdf(file: BinaryIO) -> str:
    """
    Extract text from an uploaded PDF file.

    Args:
        file: A file-like object uploaded through Streamlit.

    Returns:
        Extracted text from all readable PDF pages.
    """
    return "\n\n".join(page.text for page in extract_pages_from_pdf(file))
