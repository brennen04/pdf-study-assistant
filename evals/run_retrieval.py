import json
from dataclasses import asdict
from time import perf_counter

from evals.dataset import CASES, DOCUMENTS
from src.evaluation.retrieval import build_retrieval_report, score_retrieval_case
from src.rag.pipeline import build_document_index, build_question_context


def run() -> dict:
    """Run the versioned retrieval baseline against the current RAG pipeline."""
    indexes = {
        document.document_id: build_document_index(
            list(document.pages),
            document_id=document.document_id,
            filename=document.filename,
        )
        for document in DOCUMENTS
    }
    results = []

    for case in CASES:
        started_at = perf_counter()
        question_context = build_question_context(
            question=case.question,
            document_index=indexes[case.document_id],
        )
        results.append(
            score_retrieval_case(
                case,
                question_context,
                latency_seconds=perf_counter() - started_at,
            )
        )
    report = build_retrieval_report(results)

    return {
        "retrieval_hit_rate": report.retrieval_hit_rate,
        "scored_case_count": report.scored_case_count,
        "passed_case_count": report.passed_case_count,
        "unsupported_case_count": report.unsupported_case_count,
        "average_latency_seconds": report.average_latency_seconds,
        "results": [asdict(result) for result in report.results],
    }


def main() -> None:
    try:
        print(json.dumps(run(), indent=2))
    except Exception as error:
        raise SystemExit(
            "Retrieval baseline could not run because the project embedding model "
            "is unavailable. Download/cache the configured model, then rerun the "
            "command. Original error: "
            f"{error}"
        ) from error


if __name__ == "__main__":
    main()
