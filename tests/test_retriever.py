import unittest

from src.rag.retriever import rank_chunks_by_similarity


class RankChunksBySimilarityTests(unittest.TestCase):
    def test_returns_chunks_ordered_by_similarity(self):
        results = rank_chunks_by_similarity(
            query_embedding=[1.0, 0.0],
            chunk_embeddings=[
                [0.2, 0.8],
                [0.9, 0.1],
                [0.5, 0.5],
            ],
            chunks=["low", "high", "middle"],
            top_k=2,
        )

        self.assertEqual([chunk for chunk, _score in results], ["high", "middle"])
        self.assertAlmostEqual(results[0][1], 0.9, places=6)

    def test_returns_empty_list_when_inputs_are_empty(self):
        self.assertEqual(rank_chunks_by_similarity([], [], []), [])

    def test_rejects_non_positive_top_k(self):
        with self.assertRaisesRegex(ValueError, "top_k"):
            rank_chunks_by_similarity([1.0], [[1.0]], ["chunk"], top_k=0)

    def test_rejects_mismatched_chunk_and_embedding_counts(self):
        with self.assertRaisesRegex(ValueError, "same length"):
            rank_chunks_by_similarity(
                query_embedding=[1.0],
                chunk_embeddings=[[1.0], [0.5]],
                chunks=["only one chunk"],
            )


if __name__ == "__main__":
    unittest.main()
