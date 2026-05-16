from dataclasses import dataclass

from src.answer_builder import build_grounded_answer_prompt
from src.chunker import chunk_text
from src.embedding_client import embed_texts
from src.retriever import rank_chunks_by_similarity


@dataclass(frozen=True)
class DocumentIndex:
    """
    Searchable representation of an uploaded document.

    The raw chunks are kept for display and prompt construction. The embeddings
    are kept separately because retrieval works on vectors, not text.
    """
    chunks: list[str]
    embeddings: list[list[float]]


@dataclass(frozen=True)
class QuestionContext:
    """
    Retrieved context and prompt for a single user question.
    """
    query_embedding: list[float]
    retrieved_chunks: list[tuple[str, float]]
    answer_prompt: str


def build_document_index(text: str) -> DocumentIndex:
    """
    Build a searchable document index from extracted PDF text.
    """
    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)

    return DocumentIndex(chunks=chunks, embeddings=embeddings)


def build_question_context(
    question: str,
    document_index: DocumentIndex,
    internet_context_enabled: bool = False,
    top_k: int = 3,
) -> QuestionContext:
    """
    Retrieve PDF context and build the LLM prompt for one question.
    """
    query_embedding = embed_texts([question.strip()])[0]
    retrieved_chunks = rank_chunks_by_similarity(
        query_embedding=query_embedding,
        chunk_embeddings=document_index.embeddings,
        chunks=document_index.chunks,
        top_k=top_k,
    )
    answer_prompt = build_grounded_answer_prompt(
        question=question,
        retrieved_chunks=retrieved_chunks,
        internet_context_enabled=internet_context_enabled,
    )

    return QuestionContext(
        query_embedding=query_embedding,
        retrieved_chunks=retrieved_chunks,
        answer_prompt=answer_prompt,
    )
