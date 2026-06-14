"""
app/retrieval/retriever.py

Semantic retrieval of few-shot SQL examples from the ChromaDB vector store.
"""

import logging

from langchain_community.vectorstores import Chroma

from app.config import settings

logger = logging.getLogger(__name__)


def retrieve_examples(
    question: str,
    store: Chroma,
    k: int | None = None,
) -> list[dict]:
    """
    Retrieve the top-*k* most semantically similar few-shot examples for *question*.

    Parameters
    ----------
    question : str
        The user's natural language question to find similar examples for.
    store : Chroma
        The ChromaDB vector store containing the few-shot examples.
    k : int | None
        Number of examples to retrieve. Defaults to ``settings.RETRIEVAL_K``.

    Returns
    -------
    list[dict]
        A list of dicts with keys ``"question"`` and ``"sql"`` (and ``"notes"``),
        ordered by descending semantic similarity. Returns an empty list if the
        store contains no documents.
    """
    k = k or settings.RETRIEVAL_K

    try:
        docs = store.similarity_search(question, k=k)
    except Exception as exc:
        logger.warning("ChromaDB similarity search failed: %s. Falling back to zero-shot.", exc)
        return []

    results = []
    for doc in docs:
        results.append(
            {
                "question": doc.page_content,
                "sql": doc.metadata.get("sql", ""),
                "notes": doc.metadata.get("notes", ""),
            }
        )
    return results
