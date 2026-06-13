import unittest
from unittest.mock import patch

from src.rag_pipeline import DocumentIndex, build_document_index, build_question_context


class RagPipelineTests(unittest.TestCase):
    def test_build_document_index_chunks_and_embeds_text(self):
        with patch(
            "src.rag_pipeline.embed_texts",
            return_value=[[1.0], [0.5]],
        ) as embed_texts:
            document_index = build_document_index("abcdef", chunk_size=3, chunk_overlap=0)

        self.assertEqual(document_index.chunks, ["abc", "def"])
        self.assertEqual(document_index.embeddings, [[1.0], [0.5]])
        embed_texts.assert_called_once_with(["abc", "def"])

    def test_build_question_context_retrieves_chunks_and_builds_prompt(self):
        document_index = DocumentIndex(
            chunks=["less relevant", "most relevant"],
            embeddings=[[0.1, 0.9], [1.0, 0.0]],
        )

        with patch("src.rag_pipeline.embed_texts", return_value=[[1.0, 0.0]]):
            question_context = build_question_context(
                question="What matters?",
                document_index=document_index,
                internet_context_enabled=True,
                top_k=1,
            )

        self.assertEqual(question_context.query_embedding, [1.0, 0.0])
        self.assertEqual(question_context.question, "What matters?")
        self.assertEqual(question_context.retrieved_chunks[0][0], "most relevant")
        self.assertIn("What matters?", question_context.answer_prompt)
        self.assertIn("Google Search grounding", question_context.answer_prompt)


if __name__ == "__main__":
    unittest.main()
