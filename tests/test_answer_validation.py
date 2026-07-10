import unittest

from src.answer.parser import ParsedAnswer
from src.answer.result import RetrievedSource
from src.answer.validation import (
    AnswerValidationError,
    MissingPdfSourceReferenceError,
    validate_pdf_source_numbers,
)


def source(source_number: int, text: str, similarity: float) -> RetrievedSource:
    return RetrievedSource(
        source_number=source_number,
        document_id="document-1",
        filename="lecture.pdf",
        page_number=source_number,
        chunk_id=1,
        text=text,
        similarity=similarity,
    )


class AnswerValidationTests(unittest.TestCase):
    def test_accepts_source_numbers_that_were_retrieved(self):
        parsed_answer = ParsedAnswer(
            pdf_answer="The PDF says this.",
            pdf_source_numbers=[1, 2],
        )
        sources = [
            source(1, "First chunk", 0.9),
            source(2, "Second chunk", 0.8),
        ]

        validate_pdf_source_numbers(parsed_answer, sources)

    def test_rejects_source_numbers_that_were_not_retrieved(self):
        parsed_answer = ParsedAnswer(
            pdf_answer="The PDF says this.",
            pdf_source_numbers=[1, 3],
        )
        sources = [
            source(1, "First chunk", 0.9),
            source(2, "Second chunk", 0.8),
        ]

        with self.assertRaisesRegex(AnswerValidationError, r"\[3\]"):
            validate_pdf_source_numbers(parsed_answer, sources)

    def test_rejects_empty_pdf_source_numbers(self):
        parsed_answer = ParsedAnswer(
            pdf_answer="The PDF says this.",
            pdf_source_numbers=[],
        )

        with self.assertRaisesRegex(
            MissingPdfSourceReferenceError,
            "at least one",
        ):
            validate_pdf_source_numbers(parsed_answer, [source(1, "First chunk", 0.9)])


if __name__ == "__main__":
    unittest.main()
