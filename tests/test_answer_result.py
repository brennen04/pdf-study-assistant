import unittest

from src.answer.result import build_retrieved_sources


class AnswerResultTests(unittest.TestCase):
    def test_build_retrieved_sources_numbers_sources(self):
        sources = build_retrieved_sources(
            [
                ("First chunk", 0.91),
                ("Second chunk", 0.82),
            ]
        )

        self.assertEqual(sources[0].source_number, 1)
        self.assertEqual(sources[0].text, "First chunk")
        self.assertEqual(sources[0].similarity, 0.91)
        self.assertEqual(sources[1].source_number, 2)


if __name__ == "__main__":
    unittest.main()
