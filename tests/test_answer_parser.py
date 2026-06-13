import unittest

from src.answer.parser import AnswerParseError, parse_answer_output


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

    def test_parses_json_embedded_in_extra_model_text(self):
        parsed_answer = parse_answer_output(
            """
            Here is the structured answer:

            {
              "pdf_answer": "This PDF is about retrieval.",
              "pdf_source_numbers": [1],
              "internet_supplement": null,
              "web_citations": [],
              "disagreement_note": null
            }
            """
        )

        self.assertEqual(parsed_answer.pdf_answer, "This PDF is about retrieval.")
        self.assertEqual(parsed_answer.pdf_source_numbers, [1])

    def test_repairs_missing_pdf_source_numbers_list(self):
        parsed_answer = parse_answer_output(
            """
            {
              "pdf_answer": "This PDF is about Design by Contract.",
              "pdf_source_numbers":,
              "internet_supplement": null,
              "web_citations": [],
              "disagreement_note": null
            }
            """
        )

        self.assertEqual(
            parsed_answer.pdf_answer,
            "This PDF is about Design by Contract.",
        )
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

    def test_uses_fallback_when_internet_supplement_missing_but_enabled(self):
        parsed_answer = parse_answer_output(
            '{"pdf_answer": "Answer.", "internet_supplement": null}',
            internet_context_enabled=True,
        )

        self.assertEqual(
            parsed_answer.internet_supplement,
            "No separate internet supplement was returned by the model.",
        )

    def test_rejects_internet_supplement_when_internet_disabled(self):
        with self.assertRaisesRegex(AnswerParseError, "internet_supplement"):
            parse_answer_output(
                '{"pdf_answer": "Answer.", "internet_supplement": "Web answer."}',
                internet_context_enabled=False,
            )


if __name__ == "__main__":
    unittest.main()
