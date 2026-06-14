"""
tests/test_prompt.py

Unit tests for app.sql.prompt — build_prompt includes few-shot examples.
"""

import os

os.environ.setdefault("MODEL_PROVIDER", "gemini")
os.environ.setdefault("SQLITE_DB_PATH", "/tmp/test.db")

from app.sql.prompt import build_prompt  # noqa: E402
from app.sql.schema import INVENTORY_SCHEMA  # noqa: E402


class TestBuildPrompt:
    """build_prompt constructs a valid prompt string."""

    def test_contains_question(self):
        prompt = build_prompt("How many products?", [], INVENTORY_SCHEMA)
        assert "How many products?" in prompt

    def test_contains_schema(self):
        prompt = build_prompt("test question", [], INVENTORY_SCHEMA)
        assert "products" in prompt
        assert "stock" in prompt

    def test_contains_few_shot_examples(self):
        examples = [
            {"question": "How many blue items?", "sql": "SELECT COUNT(*) FROM products WHERE colour='Blue'"},
            {"question": "Cheapest jacket?", "sql": "SELECT * FROM products WHERE category='Jacket' ORDER BY price LIMIT 1"},
        ]
        prompt = build_prompt("How many red items?", examples, INVENTORY_SCHEMA)
        assert "How many blue items?" in prompt
        assert "SELECT COUNT(*) FROM products WHERE colour='Blue'" in prompt
        assert "Cheapest jacket?" in prompt

    def test_no_examples_still_valid(self):
        prompt = build_prompt("Any question", [], INVENTORY_SCHEMA)
        assert "FEW-SHOT EXAMPLES" not in prompt
        assert "DATABASE SCHEMA" in prompt
