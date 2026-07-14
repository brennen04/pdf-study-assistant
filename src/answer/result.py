from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.rag.document import DocumentChunk


@dataclass(frozen=True)
class RetrievedSource:
    """
    A PDF chunk that was retrieved for one question.
    """
    source_number: int
    document_id: str
    filename: str
    page_number: int
    chunk_id: int
    text: str
    similarity: float | None


@dataclass(frozen=True)
class WebCitation:
    """A web source returned by provider grounding metadata."""
    title: str
    uri: str


@dataclass(frozen=True)
class ModelCall:
    """
    Metadata for one LLM call.
    """
    provider: str
    model_name: str
    prompt: str
    use_google_search: bool
    latency_seconds: float | None
    raw_output: str | None
    settings: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class AnswerError:
    """
    Structured representation of an expected answer-generation failure.
    """
    code: str
    message: str
    details: str | None = None


@dataclass(frozen=True)
class AnswerResult:
    """
    Application-level result for one question.

    The model is prompted to return structured answer sections. Raw output is
    still preserved on the model call so malformed responses remain debuggable.
    """
    question: str
    pdf_answer: str | None
    internet_supplement: str | None
    sources: list[RetrievedSource]
    model_call: ModelCall
    pdf_source_numbers: list[int] = field(default_factory=list)
    web_citations: list[WebCitation] = field(default_factory=list)
    disagreement_note: str | None = None
    error: AnswerError | None = None
    internet_context_requested: bool = False
    internet_model_call: ModelCall | None = None
    internet_error: AnswerError | None = None

    @property
    def is_success(self) -> bool:
        return self.error is None


def build_retrieved_sources(
    retrieved_chunks: list[tuple[DocumentChunk, float | None]],
) -> list[RetrievedSource]:
    return [
        RetrievedSource(
            source_number=index,
            document_id=chunk.document_id,
            filename=chunk.filename,
            page_number=chunk.page_number,
            chunk_id=chunk.chunk_id,
            text=chunk.text,
            similarity=similarity,
        )
        for index, (chunk, similarity) in enumerate(retrieved_chunks, start=1)
    ]
