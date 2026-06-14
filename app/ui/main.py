"""
app/ui/app.py

Streamlit entry point for the NL-to-SQL Analytics Assistant.

Run with:
    streamlit run app/ui/app.py
"""

import logging
import pandas as pd
import streamlit as st

from app.config import settings
from app.providers.factory import get_provider
from app.providers.health import validate_provider, is_ollama_available
from app.database.repository import validate_db_path, execute_query, get_column_names
from app.retrieval.store import initialize_store
from app.retrieval.seeder import seed_if_empty
from app.sql.generator import generate_sql

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="NL → SQL Analytics Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Startup validation (runs once per session via st.cache_resource)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Initialising vector store...")
def _get_store():
    """Initialise ChromaDB store and seed with examples (once per session)."""
    store = initialize_store()
    seed_if_empty(store)
    return store


@st.cache_resource(show_spinner=False)
def _check_db():
    """Validate the database path at startup."""
    validate_db_path()
    return True


@st.cache_resource(show_spinner=False)
def _ollama_available():
    """Check once whether Ollama is reachable."""
    return is_ollama_available()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")

    ollama_ok = _ollama_available()

    provider_options = ["Gemini", "ChatGPT"]
    provider_map = {"Gemini": "gemini", "ChatGPT": "openai"}

    if ollama_ok:
        provider_options = ["Gemma (Local)", "Gemini", "ChatGPT"]
        provider_map["Gemma (Local)"] = "gemma"
    else:
        st.warning("Ollama is not available. Gemma (local) option is disabled.")

    # Default to the configured provider if it maps to an available option
    default_label = next(
        (k for k, v in provider_map.items() if v == settings.MODEL_PROVIDER),
        provider_options[0],
    )
    default_index = provider_options.index(default_label)

    selected_label = st.selectbox(
        "LLM Provider",
        options=provider_options,
        index=default_index,
        help="Select which language model to use for SQL generation.",
    )
    selected_provider_name = provider_map[selected_label]

    st.markdown("---")
    st.caption("NL → SQL Analytics Assistant · demo build")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.title("🔍 Natural Language → SQL Analytics")
st.markdown(
    "Ask a question about the retail inventory database in plain English. "
    "The assistant will generate and execute the SQL query for you."
)

# DB startup validation (display error once if DB is missing)
try:
    _check_db()
except RuntimeError as db_err:
    st.error(f"**Database error:** {db_err}")
    st.stop()

# Initialise vector store
try:
    store = _get_store()
except Exception as store_err:
    st.error(f"**Vector store error:** {store_err}")
    st.stop()

# Validate the selected provider before the user submits a query
try:
    validate_provider(selected_provider_name)
    provider_valid = True
    provider_error = None
except (RuntimeError, ValueError) as prov_err:
    provider_valid = False
    provider_error = str(prov_err)

if not provider_valid:
    st.error(f"**Provider configuration error:** {provider_error}")

# ---------------------------------------------------------------------------
# Query input form
# ---------------------------------------------------------------------------

with st.form(key="query_form", clear_on_submit=False):
    question = st.text_input(
        "Your question",
        placeholder="e.g. How many white t-shirts are in stock?",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button(
        "Run Query",
        type="primary",
        disabled=not provider_valid,
    )

# ---------------------------------------------------------------------------
# Query execution
# ---------------------------------------------------------------------------

if submitted:
    # Task 7.5 — empty input guard
    if not question or not question.strip():
        st.warning("Please enter a question before running the query.")
        st.stop()

    try:
        # Instantiate provider on each run so switching the dropdown takes effect
        provider = get_provider(selected_provider_name)

        with st.spinner(f"Generating SQL with **{selected_label}**..."):
            sql = generate_sql(question, provider, store)

        # Task 7.4 — show generated SQL in expander
        with st.expander("Generated SQL", expanded=False):
            st.code(sql, language="sql")

        with st.spinner("Executing query..."):
            rows = execute_query(sql)
            columns = get_column_names(sql)

        # Task 7.7 — empty results
        if not rows:
            st.info("No results found for your query.")
        else:
            df = pd.DataFrame(rows, columns=columns)
            st.success(f"Query returned **{len(rows)}** row(s).")
            st.dataframe(df, use_container_width=True)

    except ValueError as ve:
        # Task 7.6 — user-readable error (e.g. read-only violation)
        st.error(f"**Query validation error:** {ve}")

    except Exception as exc:
        # Task 7.6 — catch-all: no traceback shown to user
        logger.exception("Unhandled error during query execution")
        st.error(
            f"**An error occurred:** {exc}\n\n"
            "Please try rephrasing your question or check the provider configuration."
        )
