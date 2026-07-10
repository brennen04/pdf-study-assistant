from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCase:
    """One versioned question with expected PDF evidence behavior."""

    case_id: str
    document_id: str
    question: str
    expected_page_numbers: tuple[int, ...]
    minimum_expected_page_hits: int
    expected_behavior: str


@dataclass(frozen=True)
class RetrievalEvaluationResult:
    """Deterministic retrieval result for one evaluation case."""

    case_id: str
    document_id: str
    expected_page_numbers: tuple[int, ...]
    retrieved_page_numbers: tuple[int, ...]
    expected_page_hits: tuple[int, ...]
    passed: bool | None
    expected_behavior: str
    task_intent: str
    context_strategy: str
    latency_seconds: float | None = None


@dataclass(frozen=True)
class RetrievalEvaluationReport:
    """Aggregate deterministic retrieval metrics for one dataset run."""

    results: tuple[RetrievalEvaluationResult, ...]
    scored_case_count: int
    passed_case_count: int
    unsupported_case_count: int

    @property
    def retrieval_hit_rate(self) -> float | None:
        if not self.scored_case_count:
            return None

        return self.passed_case_count / self.scored_case_count

    @property
    def average_latency_seconds(self) -> float | None:
        measured_latencies = [
            result.latency_seconds
            for result in self.results
            if result.latency_seconds is not None
        ]

        if not measured_latencies:
            return None

        return sum(measured_latencies) / len(measured_latencies)
