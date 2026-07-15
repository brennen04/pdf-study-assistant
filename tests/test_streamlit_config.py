import os
import unittest
from unittest.mock import patch

from src.streamlit_app.config import is_internet_context_enabled


class InternetContextConfigTests(unittest.TestCase):
    def test_defaults_to_disabled(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(is_internet_context_enabled())

    def test_accepts_common_enabled_values(self):
        for value in ("1", "true", "TRUE", " yes ", "on"):
            with self.subTest(value=value), patch.dict(
                os.environ,
                {"ENABLE_INTERNET_CONTEXT": value},
                clear=True,
            ):
                self.assertTrue(is_internet_context_enabled())

    def test_other_values_remain_disabled(self):
        for value in ("0", "false", "no", "off", "unexpected"):
            with self.subTest(value=value), patch.dict(
                os.environ,
                {"ENABLE_INTERNET_CONTEXT": value},
                clear=True,
            ):
                self.assertFalse(is_internet_context_enabled())
