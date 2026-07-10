import unittest
from io import BytesIO
from unittest.mock import patch

from src.rag.pdf_loader import extract_pages_from_pdf


class FakePage:
    def __init__(self, text: str | None) -> None:
        self.text = text

    def extract_text(self) -> str | None:
        return self.text


class ExtractPagesFromPdfTests(unittest.TestCase):
    def test_preserves_original_page_numbers_when_a_page_has_no_text(self):
        pages = [
            FakePage("First page"),
            FakePage(None),
            FakePage("Third page"),
        ]

        reader = type("Reader", (), {"pages": pages})()
        with patch("src.rag.pdf_loader.PdfReader", return_value=reader):
            extracted_pages = extract_pages_from_pdf(BytesIO(b"pdf"))

        self.assertEqual([page.page_number for page in extracted_pages], [1, 3])
        self.assertEqual([page.text for page in extracted_pages], ["First page", "Third page"])


if __name__ == "__main__":
    unittest.main()
