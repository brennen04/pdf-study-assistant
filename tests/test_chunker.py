import unittest

from src.rag.chunker import chunk_pages, chunk_text
from src.rag.document import PdfPage


class ChunkTextTests(unittest.TestCase):
    def test_returns_empty_list_for_blank_text(self):
        self.assertEqual(chunk_text("   \n\t   "), [])

    def test_splits_text_with_overlap(self):
        chunks = chunk_text("abcdefghij", chunk_size=4, chunk_overlap=1)

        self.assertEqual(chunks, ["abcd", "defg", "ghij", "j"])

    def test_rejects_invalid_chunk_size(self):
        with self.assertRaisesRegex(ValueError, "chunk_size"):
            chunk_text("abc", chunk_size=0)

    def test_rejects_overlap_equal_to_chunk_size(self):
        with self.assertRaisesRegex(ValueError, "chunk_overlap"):
            chunk_text("abc", chunk_size=3, chunk_overlap=3)

    def test_preserves_page_metadata_when_chunking_pages(self):
        chunks = chunk_pages(
            [PdfPage(page_number=3, text="abcdefgh")],
            document_id="document-1",
            filename="lecture.pdf",
            chunk_size=4,
            chunk_overlap=0,
        )

        self.assertEqual([chunk.text for chunk in chunks], ["abcd", "efgh"])
        self.assertEqual([chunk.chunk_id for chunk in chunks], [1, 2])
        self.assertEqual([chunk.page_number for chunk in chunks], [3, 3])
        self.assertTrue(all(chunk.filename == "lecture.pdf" for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
