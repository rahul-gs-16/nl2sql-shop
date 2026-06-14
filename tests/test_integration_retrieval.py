"""
tests/test_integration_retrieval.py

Integration test: seed store → retrieve → build prompt → assert relevant
SQL example is present in the generated prompt.
"""

import os
import json
import tempfile
import pytest

os.environ.setdefault("MODEL_PROVIDER", "gemini")
os.environ.setdefault("SQLITE_DB_PATH", "/tmp/test.db")
os.environ.setdefault("RETRIEVAL_K", "3")

# Point EXAMPLES_PATH to a small inline fixture
_TMP = tempfile.mkdtemp()
_EXAMPLES_FILE = os.path.join(_TMP, "examples.json")
_FIXTURE_EXAMPLES = [
    {
        "question": "How many white t-shirts are in stock?",
        "sql": "SELECT SUM(stock) FROM products WHERE colour='White' AND category='T-Shirt'",
        "notes": "aggregation example",
    },
    {
        "question": "What is the average price of hoodies?",
        "sql": "SELECT AVG(price) FROM products WHERE category='Hoodie'",
        "notes": "avg price",
    },
]

with open(_EXAMPLES_FILE, "w") as f:
    json.dump(_FIXTURE_EXAMPLES, f)

os.environ["EXAMPLES_PATH"] = _EXAMPLES_FILE

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from app.retrieval.retriever import retrieve_examples  # noqa: E402
from app.sql.prompt import build_prompt  # noqa: E402
from app.sql.schema import INVENTORY_SCHEMA  # noqa: E402


@pytest.fixture(scope="module")
def integration_store():
    """Seed an in-memory store with the fixture examples."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    store = Chroma(
        collection_name="integration_test",
        embedding_function=embeddings,
    )
    docs = [
        Document(
            page_content=ex["question"],
            metadata={"sql": ex["sql"], "notes": ex.get("notes", "")},
        )
        for ex in _FIXTURE_EXAMPLES
    ]
    store.add_documents(docs)
    yield store
    store.delete_collection()


class TestIntegrationRetrievalToPrompt:
    """End-to-end: retrieve → prompt → relevant SQL appears in prompt."""

    def test_relevant_sql_in_prompt(self, integration_store):
        question = "How many white t-shirts do we have?"
        examples = retrieve_examples(question, integration_store, k=2)
        assert len(examples) > 0, "Retrieval returned no examples"

        prompt = build_prompt(question, examples, INVENTORY_SCHEMA)

        # The SQL from the most relevant example should appear in the prompt
        assert "SELECT SUM(stock) FROM products" in prompt or \
               "colour='White'" in prompt or \
               "category='T-Shirt'" in prompt, \
               "Expected relevant SQL example not found in prompt"
