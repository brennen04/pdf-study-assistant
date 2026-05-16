from functools import lru_cache
import os


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def should_use_local_embedding_files_only() -> bool:
    """
    Return whether embedding model loading should avoid network downloads.

    Public users should be able to clone the repo and run it after installing
    dependencies, so the default allows SentenceTransformers to download the
    model on first use. Offline/local-only mode remains available through env.
    """
    value = os.getenv("EMBEDDING_MODEL_LOCAL_ONLY", "false")

    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load and cache the local embedding model.

    Returns:
        A SentenceTransformer model ready to convert text into embeddings.
    """
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        DEFAULT_EMBEDDING_MODEL,
        local_files_only=should_use_local_embedding_files_only(),
    )


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
