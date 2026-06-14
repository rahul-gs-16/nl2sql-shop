"""
app/sql/generator.py

Orchestrates the full NL-to-SQL pipeline:
  1. Retrieve few-shot examples from ChromaDB
  2. Build a prompt with schema + examples + question
  3. Call the active LLM provider
  4. Extract and clean the SQL from the response
  5. Validate that the SQL is read-only
"""

import re
import logging

from langchain_community.vectorstores import Chroma

from app.providers.base import LLMProvider
from app.retrieval.retriever import retrieve_examples
from app.sql.prompt import build_prompt
from app.sql.schema import INVENTORY_SCHEMA
from app.database.repository import _assert_read_only

logger = logging.getLogger(__name__)


def generate_sql(
    question: str,
    provider: LLMProvider,
    store: Chroma,
) -> str:
    """
    Generate a read-only SQL query from a natural language question.

    Parameters
    ----------
    question : str
        The user's natural language question.
    provider : LLMProvider
        The active LLM provider (Gemma, Gemini, or OpenAI).
    store : Chroma
        The ChromaDB vector store containing few-shot examples.

    Returns
    -------
    str
        A clean, validated SQL SELECT statement.

    Raises
    ------
    ValueError
        If the generated SQL is not a read-only SELECT statement.
    RuntimeError
        If the LLM returns an empty or unparseable response.
    """
    # Step 1 — retrieve semantically similar examples
    examples = retrieve_examples(question, store)
    logger.debug("Retrieved %d few-shot examples for question: %s", len(examples), question)

    # Step 2 — build the prompt
    prompt = build_prompt(question, examples, INVENTORY_SCHEMA)
    logger.debug("Built prompt (%d chars)", len(prompt))

    # Step 3 — call the LLM
    raw_response = provider.generate(prompt, temperature=0.0)
    logger.debug("Raw LLM response: %s", raw_response)

    # Step 4 — extract and clean the SQL
    sql = _extract_sql(raw_response)

    if not sql:
        raise RuntimeError(
            "The model returned an empty or unparseable response. "
            "Please try rephrasing your question."
        )

    # Step 5 — validate read-only (raises ValueError on destructive SQL)
    _assert_read_only(sql)

    return sql


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_sql(raw: str) -> str:
    """
    Strip markdown code fences, whitespace, and extraneous text from *raw*.

    Handles patterns like:
      ```sql\\nSELECT ...\\n```
      ```\\nSELECT ...\\n```
      SELECT ... (plain text)

    Parameters
    ----------
    raw : str
        Raw string response from the LLM.

    Returns
    -------
    str
        Cleaned SQL string, or empty string if nothing extractable was found.
    """
    # Remove code fences
    cleaned = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE)
    cleaned = cleaned.strip().strip("`").strip()

    # If LLM prefixed with "SQL:" take everything after
    if cleaned.upper().startswith("SQL:"):
        cleaned = cleaned[4:].strip()

    # Take only the first statement (up to first semicolon or end of string)
    match = re.search(r"(SELECT\b.*?)(?:;|$)", cleaned, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()

    return cleaned
