"""
app/config/settings.py

Loads and exposes all environment variables used by the application.
Values are read from the process environment (populated by Docker Compose / .env).
"""

import os
from dotenv import load_dotenv

# Load .env from project root when running outside Docker
load_dotenv()

# ---------------------------------------------------------------------------
# LLM provider
# ---------------------------------------------------------------------------

MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "gemma").strip().lower()
"""Active LLM provider. One of: gemma | gemini | openai."""

# ---------------------------------------------------------------------------
# API keys
# ---------------------------------------------------------------------------

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
"""OpenAI API key. Required when MODEL_PROVIDER=openai."""

GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
"""Google Generative AI API key. Required when MODEL_PROVIDER=gemini."""

# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
"""Base URL of the Ollama HTTP API. Used by GemmaProvider."""

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "/data/inventory.db")
"""Absolute path to the SQLite inventory database file."""

# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------

CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "/chroma")
"""Directory where ChromaDB persists its vector store."""

CHROMA_COLLECTION_NAME: str = "sql_examples"
"""Name of the ChromaDB collection that holds few-shot examples."""

# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", "3"))
"""Number of few-shot examples to retrieve per query."""

EXAMPLES_PATH: str = os.getenv("EXAMPLES_PATH", "/data/examples/examples.json")
"""Path to the JSON file containing seed few-shot examples."""

VALID_PROVIDERS = {"gemma", "gemini", "openai"}
"""Set of valid MODEL_PROVIDER values."""
