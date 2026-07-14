import unittest

from src.answer.result import WebCitation
from src.answer.web_citations import format_web_citation


class WebCitationTests(unittest.TestCase):
    def test_formats_google_grounding_redirect_url_with_readable_label(self):
        uri = (
            "https://vertexaisearch.cloud.google.com/grounding-api-redirect/"
            "AUZIYQF8sBAGuYjrqfPhYRzGbLZeEEwMbhX"
        )
        citation = WebCitation(title="Example source", uri=uri)

        self.assertEqual(
            format_web_citation(citation, citation_number=2),
            f"[Example source]({uri})",
        )

    def test_formats_regular_url_with_domain_label(self):
        citation = WebCitation(title="Example article", uri="https://www.example.com/article")

        self.assertEqual(
            format_web_citation(citation, citation_number=1),
            "[Example article](https://www.example.com/article)",
        )

    def test_does_not_link_relative_redirect(self):
        self.assertEqual(
            format_web_citation(
                WebCitation("Example source", "/grounding-api-redirect/token"),
                citation_number=1,
            ),
            "Example source",
        )


if __name__ == "__main__":
    unittest.main()
