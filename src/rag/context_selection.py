from src.rag.document import DocumentChunk


def select_coverage_chunks(
    chunks: list[DocumentChunk],
    max_chunks: int,
) -> list[DocumentChunk]:
    """Select ordered chunks that cover the full document within a fixed budget."""
    if max_chunks <= 0:
        raise ValueError("max_chunks must be greater than 0.")

    if len(chunks) <= max_chunks:
        return chunks

    last_index = len(chunks) - 1
    selected_indexes = [
        round(position * last_index / (max_chunks - 1))
        for position in range(max_chunks)
    ]

    return [chunks[index] for index in selected_indexes]
