import unittest
from contextlib import nullcontext
from unittest.mock import patch

from src.rag_pipeline import QuestionContext
from src.streamlit_runtime import generate_answer_once


class GenerateAnswerOnceTests(unittest.TestCase):
    def test_does_not_cache_failed_answer_generation(self):
        question_context = QuestionContext(
            query_embedding=[1.0],
            retrieved_chunks=[("PDF context", 0.9)],
            answer_prompt="Answer from this PDF context.",
        )

        with (
            patch("src.streamlit_runtime.get_answer_cache_key", return_value=None),
            patch(
                "src.streamlit_runtime.generate_answer",
                side_effect=RuntimeError("provider unavailable"),
            ),
            patch("src.streamlit_runtime.remember_answer_error") as remember_error,
            patch("src.streamlit_runtime.remember_answer_cache_key") as remember_key,
            patch("src.streamlit_runtime.st.spinner", return_value=nullcontext()),
        ):
            generate_answer_once(question_context, use_google_search=False)

        remember_error.assert_called_once_with("provider unavailable")
        remember_key.assert_not_called()


if __name__ == "__main__":
    unittest.main()
