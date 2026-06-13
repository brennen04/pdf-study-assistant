from dataclasses import dataclass

from src.answer.builder import build_grounded_answer_prompt
from src.providers.embedding_client import embed_texts
from src.rag.chunker import chunk_text
from src.rag.retriever import rank_chunks_by_similarity
from src.rag.task_intent import TaskIntent, classify_task_intent


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
    question: str
    task_intent: TaskIntent
    context_strategy: str
    query_embedding: list[float]
    retrieved_chunks: list[tuple[str, float]]
    answer_prompt: str


def build_document_index(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> DocumentIndex:
    """
    Build a searchable document index from extracted PDF text.
    """
    chunks = chunk_text(
        text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    embeddings = embed_texts(chunks)

    return DocumentIndex(chunks=chunks, embeddings=embeddings)


def build_question_context(
    question: str,
    document_index: DocumentIndex,
    internet_context_enabled: bool = False,
    top_k: int = 3,
    transformation_context_chunks: int = 8,
) -> QuestionContext:
    """
    Retrieve PDF context and build the LLM prompt for one question.
    """
    cleaned_question = question.strip()
    task_intent = classify_task_intent(cleaned_question)
    query_embedding = embed_texts([cleaned_question])[0]

    if task_intent == TaskIntent.STUDY_TRANSFORMATION:
        context_strategy = "broad_document_context"
        retrieved_chunks = [
            (chunk, 1.0)
            for chunk in document_index.chunks[:transformation_context_chunks]
        ]
    else:
        context_strategy = "semantic_top_k"
        retrieved_chunks = rank_chunks_by_similarity(
            query_embedding=query_embedding,
            chunk_embeddings=document_index.embeddings,
            chunks=document_index.chunks,
            top_k=top_k,
        )

    answer_prompt = build_grounded_answer_prompt(
        question=cleaned_question,
        retrieved_chunks=retrieved_chunks,
        internet_context_enabled=internet_context_enabled,
        task_intent=task_intent,
    )

    return QuestionContext(
        question=cleaned_question,
        task_intent=task_intent,
        context_strategy=context_strategy,
        query_embedding=query_embedding,
        retrieved_chunks=retrieved_chunks,
        answer_prompt=answer_prompt,
    )
