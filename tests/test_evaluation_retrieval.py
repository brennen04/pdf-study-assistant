import unittest

from evals.dataset import CASES, DOCUMENTS
from src.evaluation.models import EvaluationCase
from src.evaluation.retrieval import build_retrieval_report, score_retrieval_case
from src.rag.document import DocumentChunk
from src.rag.pipeline import QuestionContext
from src.rag.task_intent import TaskIntent


def question_context(*page_numbers: int) -> QuestionContext:
    return QuestionContext(
        question="Question",
        task_intent=TaskIntent.FACTUAL_LOOKUP,
        context_strategy="semantic_top_k",
        query_embedding=[1.0],
        retrieved_chunks=[
            (
                DocumentChunk(
                    document_id="document-1",
                    filename="document.pdf",
                    page_number=page_number,
                    chunk_id=1,
                    text=f"Page {page_number}",
                ),
                0.9,
            )
            for page_number in page_numbers
        ],
        answer_prompt="Prompt",
    )


class RetrievalEvaluationTests(unittest.TestCase):
    def test_versioned_dataset_has_three_documents_and_twenty_cases(self):
        self.assertEqual(len(DOCUMENTS), 3)
        self.assertEqual(len(CASES), 20)
        self.assertEqual(len({case.case_id for case in CASES}), len(CASES))

    def test_passes_when_minimum_expected_page_hits_are_retrieved(self):
        case = EvaluationCase(
            case_id="multi-page",
            document_id="document-1",
            question="Question",
            expected_page_numbers=(2, 4),
            minimum_expected_page_hits=2,
            expected_behavior="answerable",
        )

        result = score_retrieval_case(case, question_context(2, 4, 5))

        self.assertTrue(result.passed)
        self.assertEqual(result.expected_page_hits, (2, 4))
        self.assertEqual(result.task_intent, "factual_lookup")
        self.assertEqual(result.context_strategy, "semantic_top_k")

    def test_fails_when_required_summary_coverage_is_missing(self):
        case = EvaluationCase(
            case_id="summary",
            document_id="document-1",
            question="Summarise this document.",
            expected_page_numbers=(1, 6, 12),
            minimum_expected_page_hits=3,
            expected_behavior="study_transformation",
        )

        result = score_retrieval_case(case, question_context(1, 6))

        self.assertFalse(result.passed)
        self.assertEqual(result.expected_page_hits, (1, 6))

    def test_reports_unsupported_cases_without_counting_them_as_retrieval_passes(self):
        unsupported_case = EvaluationCase(
            case_id="unsupported",
            document_id="document-1",
            question="Unsupported question",
            expected_page_numbers=(),
            minimum_expected_page_hits=0,
            expected_behavior="unsupported_by_pdf",
        )
        answerable_case = EvaluationCase(
            case_id="answerable",
            document_id="document-1",
            question="Answerable question",
            expected_page_numbers=(2,),
            minimum_expected_page_hits=1,
            expected_behavior="answerable",
        )

        report = build_retrieval_report(
            [
                score_retrieval_case(unsupported_case, question_context(1)),
                score_retrieval_case(answerable_case, question_context(2)),
            ]
        )

        self.assertEqual(report.scored_case_count, 1)
        self.assertEqual(report.passed_case_count, 1)
        self.assertEqual(report.unsupported_case_count, 1)
        self.assertEqual(report.retrieval_hit_rate, 1.0)
        self.assertIsNone(report.average_latency_seconds)
