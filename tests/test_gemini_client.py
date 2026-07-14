import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from src.answer.result import WebCitation
from src.providers.gemini_client import _extract_web_citations, generate_answer


class GenerateAnswerTests(unittest.TestCase):
    def test_extracts_absolute_grounding_sources_and_rejects_relative_redirects(self):
        response = SimpleNamespace(
            candidates=[
                SimpleNamespace(
                    grounding_metadata=SimpleNamespace(
                        grounding_chunks=[
                            SimpleNamespace(
                                web=SimpleNamespace(
                                    title="Example article",
                                    uri="https://example.com/article",
                                )
                            ),
                            SimpleNamespace(
                                web=SimpleNamespace(
                                    title="Broken redirect",
                                    uri="/grounding-api-redirect/token",
                                )
                            ),
                            SimpleNamespace(
                                web=SimpleNamespace(
                                    title="Duplicate",
                                    uri="https://example.com/article",
                                )
                            ),
                        ]
                    )
                )
            ]
        )

        self.assertEqual(
            _extract_web_citations(response),
            [WebCitation("Example article", "https://example.com/article")],
        )

    def test_rejects_empty_model_response(self):
        class FakeModels:
            def generate_content(self, **_kwargs):
                return SimpleNamespace(text="")

        class FakeClient:
            def __init__(self, api_key):
                self.api_key = api_key
                self.models = FakeModels()

        fake_google_module = ModuleType("google")
        fake_genai_module = ModuleType("google.genai")
        fake_types_module = ModuleType("google.genai.types")
        setattr(fake_genai_module, "Client", FakeClient)
        setattr(fake_genai_module, "types", fake_types_module)
        setattr(fake_google_module, "genai", fake_genai_module)

        with patch.dict(
            "sys.modules",
            {
                "google": fake_google_module,
                "google.genai": fake_genai_module,
                "google.genai.types": fake_types_module,
            },
        ):
            with self.assertRaisesRegex(ValueError, "empty response"):
                generate_answer("Explain the PDF.", api_key="test-key")


if __name__ == "__main__":
    unittest.main()
