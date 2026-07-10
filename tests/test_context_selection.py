import unittest

from src.rag.context_selection import select_coverage_chunks
from src.rag.document import DocumentChunk


def chunks(count: int) -> list[DocumentChunk]:
    return [
        DocumentChunk(
            document_id="document-1",
            filename="lecture.pdf",
            page_number=index,
            chunk_id=1,
            text=f"Page {index}",
        )
        for index in range(1, count + 1)
    ]


class CoverageChunkSelectionTests(unittest.TestCase):
    def test_returns_all_chunks_when_within_the_context_budget(self):
        document_chunks = chunks(3)

        self.assertEqual(select_coverage_chunks(document_chunks, 8), document_chunks)

    def test_selects_ordered_unique_chunks_across_a_long_document(self):
        selected_chunks = select_coverage_chunks(chunks(12), 8)

        self.assertEqual(
            [chunk.page_number for chunk in selected_chunks],
            [1, 3, 4, 6, 7, 9, 10, 12],
        )

    def test_rejects_non_positive_context_budget(self):
        with self.assertRaisesRegex(ValueError, "max_chunks"):
            select_coverage_chunks(chunks(3), 0)
