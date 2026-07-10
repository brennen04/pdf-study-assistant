from src.rag.document import DocumentChunk, PdfPage


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: The full extracted PDF text.
        chunk_size: Maximum number of characters in each chunk.
        chunk_overlap: Number of characters repeated between neighboring chunks.

    Returns:
        A list of text chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be 0 or greater.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    cleaned_text = text.strip()

    if not cleaned_text:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(cleaned_text):
        end = start + chunk_size
        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks


def chunk_pages(
    pages: list[PdfPage],
    document_id: str,
    filename: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[DocumentChunk]:
    """Split each readable page into independently citable chunks."""
    chunks: list[DocumentChunk] = []

    for page in pages:
        for chunk_id, text in enumerate(
            chunk_text(
                page.text,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ),
            start=1,
        ):
            chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    filename=filename,
                    page_number=page.page_number,
                    chunk_id=chunk_id,
                    text=text,
                )
            )

    return chunks
