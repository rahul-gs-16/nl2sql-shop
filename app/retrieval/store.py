"""
app/retrieval/store.py

Initialises (or opens) the persistent ChromaDB vector store used for
few-shot SQL example retrieval.
"""

import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Return the shared HuggingFace sentence-transformer embedding model.

    Uses ``all-MiniLM-L6-v2`` — a lightweight, CPU-friendly model that
    produces 384-dimensional embeddings suitable for semantic similarity search.

    Returns
    -------
    HuggingFaceEmbeddings
        Configured embedding function.
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def initialize_store() -> Chroma:
    """
    Open or create the ChromaDB collection for few-shot SQL examples.

    The collection is persisted to ``settings.CHROMA_PERSIST_DIR`` so that
    embeddings survive container restarts without re-seeding.

    Returns
    -------
    Chroma
        A LangChain ``Chroma`` vector store wrapping the collection.
    """
    embeddings = get_embeddings()

    store = Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )
    return store
