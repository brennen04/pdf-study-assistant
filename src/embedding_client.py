from functools import lru_cache


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load and cache the local embedding model.

    Returns:
        A SentenceTransformer model ready to convert text into embeddings.
    """
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(DEFAULT_EMBEDDING_MODEL, local_files_only=True)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert text strings into embedding vectors.

    Args:
        texts: Text chunks to embed.

    Returns:
        A list of embedding vectors, one vector per input text.
    """
    if not texts:
        return []

    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.tolist()
