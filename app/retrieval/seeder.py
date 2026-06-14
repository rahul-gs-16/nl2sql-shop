"""
app/retrieval/seeder.py

Seeds the ChromaDB vector store with few-shot SQL examples on first run.
Subsequent runs are no-ops (idempotent check on collection size).
"""

import json
import os
import logging

from langchain_community.vectorstores import Chroma
from langchain.schema import Document

from app.config import settings

logger = logging.getLogger(__name__)


def seed_if_empty(store: Chroma) -> None:
    """
    Populate the ChromaDB collection with few-shot examples if it is empty.

    Reads example pairs from ``settings.EXAMPLES_PATH`` (a JSON file with a
    list of objects containing ``question``, ``sql``, and optional ``notes``).
    If the collection already contains documents this function is a no-op.

    Parameters
    ----------
    store : Chroma
        The vector store to seed.
    """
    # Check current count — skip seeding if already populated
    existing = store.get()
    if existing and existing.get("ids"):
        logger.info(
            "ChromaDB collection '%s' already contains %d documents — skipping seed.",
            settings.CHROMA_COLLECTION_NAME,
            len(existing["ids"]),
        )
        return

    examples_path = settings.EXAMPLES_PATH
    if not os.path.isfile(examples_path):
        logger.warning(
            "Examples file not found at '%s'. Skipping seed — few-shot retrieval will be zero-shot.",
            examples_path,
        )
        return

    with open(examples_path, "r", encoding="utf-8") as f:
        examples: list[dict] = json.load(f)

    documents = []
    for ex in examples:
        doc = Document(
            page_content=ex["question"],
            metadata={
                "sql": ex["sql"],
                "notes": ex.get("notes", ""),
            },
        )
        documents.append(doc)

    store.add_documents(documents)
    logger.info(
        "Seeded ChromaDB collection '%s' with %d examples.",
        settings.CHROMA_COLLECTION_NAME,
        len(documents),
    )
