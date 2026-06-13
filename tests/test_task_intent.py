import unittest

from src.rag.task_intent import TaskIntent, classify_task_intent


class TaskIntentTests(unittest.TestCase):
    def test_classifies_summary_as_study_transformation(self):
        self.assertEqual(
            classify_task_intent("Can you summarise this PDF?"),
            TaskIntent.STUDY_TRANSFORMATION,
        )

    def test_classifies_notes_as_study_transformation(self):
        self.assertEqual(
            classify_task_intent("Make study notes from this document."),
            TaskIntent.STUDY_TRANSFORMATION,
        )

    def test_classifies_document_overview_as_study_transformation(self):
        self.assertEqual(
            classify_task_intent("What is this about?"),
            TaskIntent.STUDY_TRANSFORMATION,
        )

    def test_classifies_lookup_as_factual_lookup(self):
        self.assertEqual(
            classify_task_intent("What does the PDF say about retrieval?"),
            TaskIntent.FACTUAL_LOOKUP,
        )


if __name__ == "__main__":
    unittest.main()
