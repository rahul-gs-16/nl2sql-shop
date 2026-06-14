"""
tests/test_retriever.py

Unit tests for app.retrieval.retriever — retrieve_examples returns top-k
similar documents from a pre-seeded in-memory ChromaDB.
"""

import os
import pytest

os.environ.setdefault("MODEL_PROVIDER", "gemini")
os.environ.setdefault("SQLITE_DB_PATH", "/tmp/test.db")
os.environ.setdefault("RETRIEVAL_K", "2")

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from app.retrieval.retriever import retrieve_examples  # noqa: E402


@pytest.fixture(scope="module")
def seeded_store():
    """Create an in-memory ChromaDB with a few example documents."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    store = Chroma(
        collection_name="test_collection",
        embedding_function=embeddings,
    )
    docs = [
        Document(
            page_content="How many white t-shirts are in stock?",
            metadata={"sql": "SELECT SUM(stock) FROM products WHERE colour='White' AND category='T-Shirt'"},
        ),
        Document(
            page_content="What is the average price of hoodies?",
            metadata={"sql": "SELECT AVG(price) FROM products WHERE category='Hoodie'"},
        ),
        Document(
            page_content="List all products with a discount greater than 20 percent",
            metadata={"sql": "SELECT * FROM products WHERE discount > 20"},
        ),
    ]
    store.add_documents(docs)
    yield store
    store.delete_collection()


class TestRetrieveExamples:
    """retrieve_examples returns correctly structured dicts."""

    def test_returns_list(self, seeded_store):
        results = retrieve_examples("Show me t-shirts in white colour", seeded_store, k=2)
        assert isinstance(results, list)

    def test_returns_correct_keys(self, seeded_store):
        results = retrieve_examples("white shirts", seeded_store, k=1)
        assert len(results) >= 1
        assert "question" in results[0]
        assert "sql" in results[0]

    def test_top_result_is_relevant(self, seeded_store):
        """Top result for a t-shirt question should be the t-shirt example."""
        results = retrieve_examples("How many white t-shirts do we have?", seeded_store, k=1)
        assert len(results) == 1
        assert "t-shirt" in results[0]["question"].lower() or "white" in results[0]["question"].lower()

    def test_respects_k_limit(self, seeded_store):
        results = retrieve_examples("products", seeded_store, k=2)
        assert len(results) <= 2
