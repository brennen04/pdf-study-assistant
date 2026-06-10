import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from src.gemini_client import generate_answer


class GenerateAnswerTests(unittest.TestCase):
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
        fake_genai_module.Client = FakeClient
        fake_genai_module.types = fake_types_module
        fake_google_module.genai = fake_genai_module

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
