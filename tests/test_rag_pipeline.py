import unittest
from unittest.mock import patch

from src.rag.document import DocumentChunk, PdfPage
from src.rag.pipeline import DocumentIndex, build_document_index, build_question_context
from src.rag.task_intent import TaskIntent


class RagPipelineTests(unittest.TestCase):
    def test_build_document_index_chunks_and_embeds_text(self):
        with patch(
            "src.rag.pipeline.embed_texts",
            return_value=[[1.0], [0.5]],
        ) as embed_texts:
            document_index = build_document_index(
                [PdfPage(page_number=4, text="abcdef")],
                document_id="document-1",
                filename="lecture.pdf",
                chunk_size=3,
                chunk_overlap=0,
            )

        self.assertEqual([chunk.text for chunk in document_index.chunks], ["abc", "def"])
        self.assertEqual([chunk.page_number for chunk in document_index.chunks], [4, 4])
        self.assertEqual(document_index.embeddings, [[1.0], [0.5]])
        embed_texts.assert_called_once_with(["abc", "def"])

    def test_build_question_context_retrieves_chunks_and_builds_prompt(self):
        document_index = DocumentIndex(
            document_id="document-1",
            filename="lecture.pdf",
            chunks=[
                DocumentChunk("document-1", "lecture.pdf", 1, 1, "less relevant"),
                DocumentChunk("document-1", "lecture.pdf", 2, 1, "most relevant"),
            ],
            embeddings=[[0.1, 0.9], [1.0, 0.0]],
        )

        with patch("src.rag.pipeline.embed_texts", return_value=[[1.0, 0.0]]):
            question_context = build_question_context(
                question="What matters?",
                document_index=document_index,
                internet_context_enabled=True,
                top_k=1,
            )

        self.assertEqual(question_context.query_embedding, [1.0, 0.0])
        self.assertEqual(question_context.question, "What matters?")
        self.assertEqual(question_context.task_intent, TaskIntent.FACTUAL_LOOKUP)
        self.assertEqual(question_context.context_strategy, "semantic_top_k")
        self.assertEqual(question_context.retrieved_chunks[0][0].text, "most relevant")
        self.assertEqual(question_context.retrieved_chunks[0][0].page_number, 2)
        self.assertIn("What matters?", question_context.answer_prompt)
        self.assertIn("Google Search grounding", question_context.answer_prompt)

    def test_build_question_context_uses_coverage_aware_context_for_study_transformation(self):
        document_index = DocumentIndex(
            document_id="document-1",
            filename="lecture.pdf",
            chunks=[
                DocumentChunk("document-1", "lecture.pdf", page, 1, f"page {page}")
                for page in range(1, 13)
            ],
            embeddings=[[1.0] for _page in range(1, 13)],
        )

        with (
            patch("src.rag.pipeline.embed_texts", return_value=[[1.0]]),
            patch("src.rag.pipeline.rank_chunks_by_similarity") as rank_chunks,
        ):
            question_context = build_question_context(
                question="Summarise this document.",
                document_index=document_index,
                transformation_context_chunks=8,
            )

        self.assertEqual(
            question_context.task_intent,
            TaskIntent.STUDY_TRANSFORMATION,
        )
        self.assertEqual(
            question_context.context_strategy,
            "coverage_aware_document_context",
        )
        self.assertEqual(
            [chunk.page_number for chunk, _score in question_context.retrieved_chunks],
            [1, 3, 4, 6, 7, 9, 10, 12],
        )
        self.assertIn(
            "Source 1 (lecture.pdf, page 1, chunk 1; broad document context)",
            question_context.answer_prompt,
        )
        self.assertIn("Task intent:\nstudy_transformation", question_context.answer_prompt)
        rank_chunks.assert_not_called()


if __name__ == "__main__":
    unittest.main()
