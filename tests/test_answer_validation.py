import unittest

from src.answer_parser import ParsedAnswer
from src.answer_result import RetrievedSource
from src.answer_validation import AnswerValidationError, validate_pdf_source_numbers


class AnswerValidationTests(unittest.TestCase):
    def test_accepts_source_numbers_that_were_retrieved(self):
        parsed_answer = ParsedAnswer(
            pdf_answer="The PDF says this.",
            pdf_source_numbers=[1, 2],
        )
        sources = [
            RetrievedSource(source_number=1, text="First chunk", similarity=0.9),
            RetrievedSource(source_number=2, text="Second chunk", similarity=0.8),
        ]

        validate_pdf_source_numbers(parsed_answer, sources)

    def test_rejects_source_numbers_that_were_not_retrieved(self):
        parsed_answer = ParsedAnswer(
            pdf_answer="The PDF says this.",
            pdf_source_numbers=[1, 3],
        )
        sources = [
            RetrievedSource(source_number=1, text="First chunk", similarity=0.9),
            RetrievedSource(source_number=2, text="Second chunk", similarity=0.8),
        ]

        with self.assertRaisesRegex(AnswerValidationError, r"\[3\]"):
            validate_pdf_source_numbers(parsed_answer, sources)


if __name__ == "__main__":
    unittest.main()
