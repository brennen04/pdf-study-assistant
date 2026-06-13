import unittest

from src.answer_builder import build_grounded_answer_prompt
from src.task_intent import TaskIntent


class BuildGroundedAnswerPromptTests(unittest.TestCase):
    def test_builds_pdf_first_prompt_without_internet(self):
        prompt = build_grounded_answer_prompt(
            question="What is retrieval?",
            retrieved_chunks=[("Retrieval finds relevant chunks.", 0.91)],
            internet_context_enabled=False,
        )

        self.assertIn("Question:\nWhat is retrieval?", prompt)
        self.assertIn("Task intent:\nfactual_lookup", prompt)
        self.assertIn("Source 1 (similarity: 0.910)", prompt)
        self.assertIn("Do not add internet information", prompt)
        self.assertIn("Internet context is disabled.", prompt)
        self.assertIn("Return only valid JSON", prompt)
        self.assertIn('"pdf_answer"', prompt)
        self.assertIn('"internet_supplement"', prompt)
        self.assertIn("For study transformations", prompt)
        self.assertIn("synthesize from the PDF context", prompt)

    def test_builds_prompt_with_google_search_grounding_instruction(self):
        prompt = build_grounded_answer_prompt(
            question="What changed recently?",
            retrieved_chunks=[("The PDF gives the baseline.", 0.8)],
            internet_context_enabled=True,
        )

        self.assertIn("use Google Search grounding", prompt)
        self.assertIn("separate Internet supplement", prompt)
        self.assertIn("internet_supplement must be a non-empty string", prompt)
        self.assertIn('"web_citations"', prompt)

    def test_includes_explicit_web_context_when_provided(self):
        prompt = build_grounded_answer_prompt(
            question="Compare sources.",
            retrieved_chunks=[("PDF source.", 0.8)],
            internet_context_enabled=True,
            web_context=["Web source text."],
        )

        self.assertIn("Web source 1:\nWeb source text.", prompt)

    def test_includes_study_transformation_task_intent(self):
        prompt = build_grounded_answer_prompt(
            question="Summarise this PDF.",
            retrieved_chunks=[("PDF source.", 1.0)],
            task_intent=TaskIntent.STUDY_TRANSFORMATION,
        )

        self.assertIn("Task intent:\nstudy_transformation", prompt)

    def test_rejects_empty_question(self):
        with self.assertRaisesRegex(ValueError, "question"):
            build_grounded_answer_prompt(" ", [("chunk", 0.5)])

    def test_rejects_empty_retrieved_chunks(self):
        with self.assertRaisesRegex(ValueError, "retrieved_chunks"):
            build_grounded_answer_prompt("Question?", [])


if __name__ == "__main__":
    unittest.main()
