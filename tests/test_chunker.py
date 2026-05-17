import unittest

from src.chunker import chunk_text


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


if __name__ == "__main__":
    unittest.main()
