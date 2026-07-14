import unittest

from src.answer.builder import (
    build_grounded_answer_prompt,
    build_internet_supplement_prompt,
)
from src.rag.document import DocumentChunk
from src.rag.task_intent import TaskIntent


def chunk(text: str) -> DocumentChunk:
    return DocumentChunk("document-1", "lecture.pdf", 12, 2, text)


class BuildGroundedAnswerPromptTests(unittest.TestCase):
    def test_builds_pdf_first_prompt_without_internet(self):
        prompt = build_grounded_answer_prompt(
            question="What is retrieval?",
            retrieved_chunks=[(chunk("Retrieval finds relevant chunks."), 0.91)],
        )

        self.assertIn("Question:\nWhat is retrieval?", prompt)
        self.assertIn("Task intent:\nfactual_lookup", prompt)
        self.assertIn("Source 1 (lecture.pdf, page 12, chunk 2; similarity: 0.910)", prompt)
        self.assertIn("Do not use outside or internet information", prompt)
        self.assertIn("Return only valid JSON", prompt)
        self.assertIn('"pdf_answer"', prompt)
        self.assertNotIn('"internet_supplement"', prompt)
        self.assertIn("Always include one or more PDF source numbers", prompt)
        self.assertIn("Never return an empty pdf_source_numbers list", prompt)
        self.assertIn("For study transformations", prompt)
        self.assertIn("synthesize from the PDF context", prompt)

    def test_includes_study_transformation_task_intent(self):
        prompt = build_grounded_answer_prompt(
            question="Summarise this PDF.",
            retrieved_chunks=[(chunk("PDF source."), None)],
            task_intent=TaskIntent.STUDY_TRANSFORMATION,
        )

        self.assertIn("Task intent:\nstudy_transformation", prompt)
        self.assertIn("Source 1 (lecture.pdf, page 12, chunk 2; broad document context)", prompt)

    def test_keeps_broad_context_summary_prompt_pdf_only(self):
        prompt = build_grounded_answer_prompt(
            question="Summarise this PDF.",
            retrieved_chunks=[(chunk("PDF source."), None)],
            task_intent=TaskIntent.STUDY_TRANSFORMATION,
        )

        self.assertIn("Source 1 (lecture.pdf, page 12, chunk 2; broad document context)", prompt)
        self.assertNotIn("Google Search", prompt)
        self.assertNotIn('"web_citations"', prompt)

    def test_rejects_empty_question(self):
        with self.assertRaisesRegex(ValueError, "question"):
            build_grounded_answer_prompt(" ", [(chunk("chunk"), 0.5)])

    def test_rejects_empty_retrieved_chunks(self):
        with self.assertRaisesRegex(ValueError, "retrieved_chunks"):
            build_grounded_answer_prompt("Question?", [])

    def test_builds_separate_internet_supplement_prompt(self):
        prompt = build_internet_supplement_prompt(
            question="What changed recently?",
            pdf_answer="The PDF gives the baseline.",
        )

        self.assertIn("Use Google Search", prompt)
        self.assertIn("Validated PDF answer", prompt)
        self.assertIn("The PDF gives the baseline.", prompt)
        self.assertIn('"internet_supplement"', prompt)
        self.assertNotIn('"pdf_source_numbers"', prompt)
        self.assertNotIn('"web_citations"', prompt)
        self.assertIn("grounding metadata", prompt)


if __name__ == "__main__":
    unittest.main()
