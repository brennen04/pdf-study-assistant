from pypdf import PdfReader
from typing import BinaryIO


def extract_text_from_pdf(file: BinaryIO) -> str:
    """
    Extract text from an uploaded PDF file.

    Args:
        file: A file-like object uploaded through Streamlit.

    Returns:
        Extracted text from all readable PDF pages.
    """
    reader = PdfReader(file)

    pages_text: list[str] = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages_text.append(text)

    return "\n\n".join(pages_text)