import unittest

from src.answer.web_citations import format_web_citation


class WebCitationTests(unittest.TestCase):
    def test_formats_google_grounding_redirect_url_with_readable_label(self):
        citation = (
            "https://vertexaisearch.cloud.google.com/grounding-api-redirect/"
            "AUZIYQF8sBAGuYjrqfPhYRzGbLZeEEwMbhX"
        )

        self.assertEqual(
            format_web_citation(citation, citation_number=2),
            f"[Google Search result 2]({citation})",
        )

    def test_formats_regular_url_with_domain_label(self):
        citation = "https://www.example.com/article"

        self.assertEqual(
            format_web_citation(citation, citation_number=1),
            "[example.com](https://www.example.com/article)",
        )

    def test_leaves_plain_text_citation_unchanged(self):
        self.assertEqual(
            format_web_citation("Example source", citation_number=1),
            "Example source",
        )

    def test_leaves_existing_markdown_link_unchanged(self):
        citation = "[Example](https://example.com)"

        self.assertEqual(format_web_citation(citation, citation_number=1), citation)


if __name__ == "__main__":
    unittest.main()
