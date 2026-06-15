"""
app/sql/prompt.py

Builds the few-shot SQL generation prompt sent to the active LLM provider.
"""


def build_prompt(
    question: str,
    examples: list[dict],
    schema: str,
) -> str:
    """
    Construct the full prompt for SQL generation.

    The prompt includes the database schema, retrieved few-shot examples,
    and the user's question. The LLM is instructed to return only the SQL
    statement with no surrounding explanation.

    Parameters
    ----------
    question : str
        The user's natural language question.
    examples : list[dict]
        Retrieved few-shot examples. Each dict must have ``"question"`` and
        ``"sql"`` keys.
    schema : str
        The database schema string (from ``app.sql.schema.INVENTORY_SCHEMA``).

    Returns
    -------
    str
        The complete prompt string ready to be sent to an LLM provider.
    """
    lines = [
        "You are an expert SQL assistant. Convert the user's natural language question",
        "into a valid SQLite SELECT statement using the schema below.",
        "Return ONLY the SQL query — no explanation, no markdown, no code fences.",
        "",
        "Rules:",
        "- Use ONLY the table and columns listed in the schema.",
        "- ONLY SELECT statements are allowed.",
        "- Do not use DELETE, UPDATE, INSERT, DROP, or ALTER.",
        "- If unsure, write the most reasonable SELECT query you can.",
        "",
        "=== DATABASE SCHEMA ===",
        schema,
        "",
    ]

    if examples:
        lines.append("=== FEW-SHOT EXAMPLES ===")
        for i, ex in enumerate(examples, 1):
            lines.append(f"Example {i}:")
            lines.append(f"  Question: {ex['question']}")
            lines.append(f"  SQL:      {ex['sql']}")
        lines.append("")

    lines += [
        "=== YOUR TASK ===",
        "You must generate a SQL query to answer the user's current question.",
        "If there is a 'Recent conversation context' provided, use it STRICTLY to understand what product models, colors, or variants the user is referring to in their current question.",
        "For example, if the context was discussing the 'iPhone 16 Black' and the current question is 'what storage capacities are available?', your SQL must filter for model='iPhone 16' and color='Black'.",
        "",
        f"Input Data:\n{question}",
        "",
        "SQL:",
    ]

    return "\n".join(lines)
