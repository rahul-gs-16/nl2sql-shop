"""
tests/test_factory.py

Unit tests for app.providers.factory — get_provider returns the correct class
and raises ValueError for unknown provider names.
"""

import os
import pytest

os.environ.setdefault("MODEL_PROVIDER", "gemini")
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("SQLITE_DB_PATH", "/tmp/test.db")

from app.providers.factory import get_provider  # noqa: E402
from app.providers.gemini import GeminiProvider  # noqa: E402
from app.providers.openai_provider import OpenAIProvider  # noqa: E402


class TestGetProvider:
    """get_provider factory returns the correct concrete class."""

    def test_gemini_provider(self):
        provider = get_provider("gemini")
        assert isinstance(provider, GeminiProvider)

    def test_openai_provider(self):
        provider = get_provider("openai")
        assert isinstance(provider, OpenAIProvider)

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown MODEL_PROVIDER"):
            get_provider("unknown-llm")

    def test_case_insensitive(self):
        """Provider name lookup must be case-insensitive."""
        provider = get_provider("Gemini")
        assert isinstance(provider, GeminiProvider)
