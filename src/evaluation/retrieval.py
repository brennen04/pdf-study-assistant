from src.evaluation.models import (
    EvaluationCase,
    RetrievalEvaluationReport,
    RetrievalEvaluationResult,
)
from src.rag.pipeline import QuestionContext


def score_retrieval_case(
    case: EvaluationCase,
    question_context: QuestionContext,
    latency_seconds: float | None = None,
) -> RetrievalEvaluationResult:
    """Score retrieved pages against the evidence expected for one question."""
    retrieved_page_numbers = tuple(
        dict.fromkeys(
            chunk.page_number
            for chunk, _similarity in question_context.retrieved_chunks
        )
    )
    expected_page_hits = tuple(
        page_number
        for page_number in case.expected_page_numbers
        if page_number in retrieved_page_numbers
    )

    if case.expected_behavior == "unsupported_by_pdf":
        passed = None
    else:
        passed = len(expected_page_hits) >= case.minimum_expected_page_hits

    return RetrievalEvaluationResult(
        case_id=case.case_id,
        document_id=case.document_id,
        expected_page_numbers=case.expected_page_numbers,
        retrieved_page_numbers=retrieved_page_numbers,
        expected_page_hits=expected_page_hits,
        passed=passed,
        expected_behavior=case.expected_behavior,
        task_intent=question_context.task_intent.value,
        context_strategy=question_context.context_strategy,
        latency_seconds=latency_seconds,
    )


def build_retrieval_report(
    results: list[RetrievalEvaluationResult],
) -> RetrievalEvaluationReport:
    """Aggregate scored and unsupported cases without hiding their distinction."""
    scored_results = [result for result in results if result.passed is not None]

    return RetrievalEvaluationReport(
        results=tuple(results),
        scored_case_count=len(scored_results),
        passed_case_count=sum(result.passed for result in scored_results),
        unsupported_case_count=sum(
            result.expected_behavior == "unsupported_by_pdf" for result in results
        ),
    )
