import numpy as np


def rank_chunks_by_similarity(
    query_embedding: list[float],
    chunk_embeddings: list[list[float]],
    chunks: list[str],
    top_k: int = 3,
) -> list[tuple[str, float]]:
    """
    Rank text chunks by cosine similarity to the query embedding.

    Embeddings are expected to be normalized by the embedding model.
    """
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")

    if not query_embedding or not chunk_embeddings or not chunks:
        return []

    if len(chunk_embeddings) != len(chunks):
        raise ValueError("chunk_embeddings and chunks must have the same length.")

    query_vector = np.array(query_embedding, dtype=np.float32)
    document_vectors = np.array(chunk_embeddings, dtype=np.float32)

    scores = document_vectors @ query_vector
    top_indexes = np.argsort(scores)[::-1][:top_k]

    return [(chunks[index], float(scores[index])) for index in top_indexes]
