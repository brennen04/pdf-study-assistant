import unittest

from src.answer.result import build_retrieved_sources
from src.rag.document import DocumentChunk


class AnswerResultTests(unittest.TestCase):
    def test_build_retrieved_sources_numbers_sources(self):
        sources = build_retrieved_sources(
            [
                (DocumentChunk("document-1", "lecture.pdf", 4, 1, "First chunk"), 0.91),
                (DocumentChunk("document-1", "lecture.pdf", 7, 2, "Second chunk"), 0.82),
            ]
        )

        self.assertEqual(sources[0].source_number, 1)
        self.assertEqual(sources[0].filename, "lecture.pdf")
        self.assertEqual(sources[0].page_number, 4)
        self.assertEqual(sources[0].chunk_id, 1)
        self.assertEqual(sources[0].text, "First chunk")
        self.assertEqual(sources[0].similarity, 0.91)
        self.assertEqual(sources[1].source_number, 2)


if __name__ == "__main__":
    unittest.main()
