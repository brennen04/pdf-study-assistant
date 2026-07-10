from dataclasses import dataclass


@dataclass(frozen=True)
class PdfPage:
    """Readable text extracted from one PDF page."""

    page_number: int
    text: str


@dataclass(frozen=True)
class DocumentChunk:
    """A page-bounded piece of a PDF that can be embedded and cited."""

    document_id: str
    filename: str
    page_number: int
    chunk_id: int
    text: str
