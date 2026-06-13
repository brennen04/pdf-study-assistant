import unittest

from src.answer_parser import AnswerParseError, parse_answer_output


class AnswerParserTests(unittest.TestCase):
    def test_parses_structured_answer_json(self):
        parsed_answer = parse_answer_output(
            """
            {
              "pdf_answer": "The PDF says this.",
              "pdf_source_numbers": [1, 2],
              "internet_supplement": "The web adds this.",
              "web_citations": ["https://example.com"],
              "disagreement_note": "The PDF and web disagree."
            }
            """,
            internet_context_enabled=True,
        )

        self.assertEqual(parsed_answer.pdf_answer, "The PDF says this.")
        self.assertEqual(parsed_answer.pdf_source_numbers, [1, 2])
        self.assertEqual(parsed_answer.internet_supplement, "The web adds this.")
        self.assertEqual(parsed_answer.web_citations, ["https://example.com"])
        self.assertEqual(parsed_answer.disagreement_note, "The PDF and web disagree.")

    def test_parses_json_code_fence(self):
        parsed_answer = parse_answer_output(
            """```json
{"pdf_answer": "The PDF says this.", "pdf_source_numbers": []}
```"""
        )

        self.assertEqual(parsed_answer.pdf_answer, "The PDF says this.")
        self.assertEqual(parsed_answer.pdf_source_numbers, [])

    def test_rejects_plain_text_output(self):
        with self.assertRaisesRegex(AnswerParseError, "valid JSON"):
            parse_answer_output("The PDF says this.")

    def test_rejects_missing_pdf_answer(self):
        with self.assertRaisesRegex(AnswerParseError, "pdf_answer"):
            parse_answer_output('{"pdf_source_numbers": []}')

    def test_rejects_invalid_source_numbers(self):
        with self.assertRaisesRegex(AnswerParseError, "pdf_source_numbers"):
            parse_answer_output(
                '{"pdf_answer": "Answer.", "pdf_source_numbers": ["one"]}'
            )

    def test_rejects_missing_internet_supplement_when_internet_enabled(self):
        with self.assertRaisesRegex(AnswerParseError, "internet_supplement"):
            parse_answer_output(
                '{"pdf_answer": "Answer.", "internet_supplement": null}',
                internet_context_enabled=True,
            )

    def test_rejects_internet_supplement_when_internet_disabled(self):
        with self.assertRaisesRegex(AnswerParseError, "internet_supplement"):
            parse_answer_output(
                '{"pdf_answer": "Answer.", "internet_supplement": "Web answer."}',
                internet_context_enabled=False,
            )


if __name__ == "__main__":
    unittest.main()
