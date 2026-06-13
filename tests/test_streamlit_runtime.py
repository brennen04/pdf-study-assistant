import unittest
from contextlib import nullcontext
from unittest.mock import patch

from src.rag.pipeline import QuestionContext
from src.rag.task_intent import TaskIntent
from src.streamlit_app.runtime import generate_answer_once


class GenerateAnswerOnceTests(unittest.TestCase):
    def test_does_not_cache_failed_answer_generation(self):
        question_context = QuestionContext(
            question="What does the PDF say?",
            task_intent=TaskIntent.FACTUAL_LOOKUP,
            context_strategy="semantic_top_k",
            query_embedding=[1.0],
            retrieved_chunks=[("PDF context", 0.9)],
            answer_prompt="Answer from this PDF context.",
        )

        with (
            patch("src.streamlit_app.runtime.get_answer_cache_key", return_value=None),
            patch(
                "src.streamlit_app.runtime.generate_answer",
                side_effect=RuntimeError("provider unavailable"),
            ),
            patch(
                "src.streamlit_app.runtime.remember_answer_result"
            ) as remember_result,
            patch("src.streamlit_app.runtime.remember_answer_cache_key") as remember_key,
            patch("src.streamlit_app.runtime.st.spinner", return_value=nullcontext()),
        ):
            generate_answer_once(question_context, use_google_search=False)

        answer_result = remember_result.call_args.args[0]
        self.assertEqual(answer_result.question, "What does the PDF say?")
        self.assertEqual(answer_result.error.message, "provider unavailable")
        self.assertEqual(answer_result.error.code, "RuntimeError")
        self.assertIsNone(answer_result.model_call.raw_output)
        remember_key.assert_not_called()

    def test_stores_successful_answer_result_and_cache_key(self):
        question_context = QuestionContext(
            question="What does the PDF say?",
            task_intent=TaskIntent.FACTUAL_LOOKUP,
            context_strategy="semantic_top_k",
            query_embedding=[1.0],
            retrieved_chunks=[("PDF context", 0.9)],
            answer_prompt="Answer from this PDF context.",
        )

        with (
            patch("src.streamlit_app.runtime.get_answer_cache_key", return_value=None),
            patch(
                "src.streamlit_app.runtime.generate_answer",
                return_value=(
                    '{"pdf_answer": "The PDF says this.", '
                    '"pdf_source_numbers": [1], '
                    '"internet_supplement": "The web adds this.", '
                    '"web_citations": ["https://example.com"], '
                    '"disagreement_note": null}'
                ),
            ),
            patch(
                "src.streamlit_app.runtime.remember_answer_result"
            ) as remember_result,
            patch("src.streamlit_app.runtime.remember_answer_cache_key") as remember_key,
            patch("src.streamlit_app.runtime.st.spinner", return_value=nullcontext()),
        ):
            generate_answer_once(question_context, use_google_search=True)

        answer_result = remember_result.call_args.args[0]
        self.assertTrue(answer_result.is_success)
        self.assertEqual(answer_result.pdf_answer, "The PDF says this.")
        self.assertEqual(answer_result.internet_supplement, "The web adds this.")
        self.assertEqual(answer_result.pdf_source_numbers, [1])
        self.assertEqual(answer_result.web_citations, ["https://example.com"])
        self.assertIn("The PDF says this.", answer_result.model_call.raw_output)
        self.assertTrue(answer_result.model_call.use_google_search)
        self.assertEqual(answer_result.sources[0].text, "PDF context")
        remember_key.assert_called_once()

    def test_does_not_cache_unparseable_model_output(self):
        question_context = QuestionContext(
            question="What does the PDF say?",
            task_intent=TaskIntent.FACTUAL_LOOKUP,
            context_strategy="semantic_top_k",
            query_embedding=[1.0],
            retrieved_chunks=[("PDF context", 0.9)],
            answer_prompt="Answer from this PDF context.",
        )

        with (
            patch("src.streamlit_app.runtime.get_answer_cache_key", return_value=None),
            patch(
                "src.streamlit_app.runtime.generate_answer",
                return_value="The PDF says this.",
            ),
            patch(
                "src.streamlit_app.runtime.remember_answer_result"
            ) as remember_result,
            patch("src.streamlit_app.runtime.remember_answer_cache_key") as remember_key,
            patch("src.streamlit_app.runtime.st.spinner", return_value=nullcontext()),
        ):
            generate_answer_once(question_context, use_google_search=False)

        answer_result = remember_result.call_args.args[0]
        self.assertEqual(answer_result.error.code, "unparseable_model_output")
        self.assertEqual(answer_result.error.details, "The PDF says this.")
        self.assertEqual(answer_result.model_call.raw_output, "The PDF says this.")
        remember_key.assert_not_called()

    def test_uses_fallback_for_missing_internet_supplement_when_search_enabled(self):
        question_context = QuestionContext(
            question="What does the PDF say?",
            task_intent=TaskIntent.FACTUAL_LOOKUP,
            context_strategy="semantic_top_k",
            query_embedding=[1.0],
            retrieved_chunks=[("PDF context", 0.9)],
            answer_prompt="Answer from this PDF context.",
        )

        with (
            patch("src.streamlit_app.runtime.get_answer_cache_key", return_value=None),
            patch(
                "src.streamlit_app.runtime.generate_answer",
                return_value=(
                    '{"pdf_answer": "The PDF says this.", '
                    '"pdf_source_numbers": [1], '
                    '"internet_supplement": null, '
                    '"web_citations": [], '
                    '"disagreement_note": null}'
                ),
            ),
            patch(
                "src.streamlit_app.runtime.remember_answer_result"
            ) as remember_result,
            patch("src.streamlit_app.runtime.remember_answer_cache_key") as remember_key,
            patch("src.streamlit_app.runtime.st.spinner", return_value=nullcontext()),
        ):
            generate_answer_once(question_context, use_google_search=True)

        answer_result = remember_result.call_args.args[0]
        self.assertTrue(answer_result.is_success)
        self.assertEqual(
            answer_result.internet_supplement,
            "No separate internet supplement was returned by the model.",
        )
        self.assertTrue(answer_result.model_call.use_google_search)
        remember_key.assert_called_once()

    def test_does_not_cache_invalid_pdf_source_reference(self):
        question_context = QuestionContext(
            question="What does the PDF say?",
            task_intent=TaskIntent.FACTUAL_LOOKUP,
            context_strategy="semantic_top_k",
            query_embedding=[1.0],
            retrieved_chunks=[("PDF context", 0.9)],
            answer_prompt="Answer from this PDF context.",
        )

        with (
            patch("src.streamlit_app.runtime.get_answer_cache_key", return_value=None),
            patch(
                "src.streamlit_app.runtime.generate_answer",
                return_value=(
                    '{"pdf_answer": "The PDF says this.", '
                    '"pdf_source_numbers": [2], '
                    '"internet_supplement": null, '
                    '"web_citations": [], '
                    '"disagreement_note": null}'
                ),
            ),
            patch(
                "src.streamlit_app.runtime.remember_answer_result"
            ) as remember_result,
            patch("src.streamlit_app.runtime.remember_answer_cache_key") as remember_key,
            patch("src.streamlit_app.runtime.st.spinner", return_value=nullcontext()),
        ):
            generate_answer_once(question_context, use_google_search=False)

        answer_result = remember_result.call_args.args[0]
        self.assertEqual(answer_result.error.code, "invalid_pdf_source_reference")
        self.assertIn("[2]", answer_result.error.message)
        self.assertEqual(answer_result.sources[0].source_number, 1)
        remember_key.assert_not_called()

if __name__ == "__main__":
    unittest.main()
