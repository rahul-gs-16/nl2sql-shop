## Why

Business users need to query a retail inventory database without writing SQL. This project builds a demo-grade Generative AI application that translates natural language questions into SQL queries and returns readable results — replacing a single-provider Google PaLM implementation with a modular, multi-provider LLM architecture that supports local-first execution.

## What Changes

- Introduce a **natural language to SQL** query pipeline backed by LangChain and SQLite
- Implement a **multi-provider LLM abstraction layer** supporting Gemma (via Ollama), Gemini (via Google API), and ChatGPT (via OpenAI API)
- Add **runtime LLM provider selection** via environment variable and Streamlit dropdown
- Integrate **ChromaDB vector store** with HuggingFace embeddings for few-shot SQL example retrieval
- Build a **Streamlit UI** with query input, provider selection, SQL display, results table, and error display
- Package the application using **Docker Compose** with an optional Ollama container for local model execution
- Enforce **read-only SQL execution** — no destructive operations (DELETE, UPDATE, INSERT, DROP, ALTER)
- Provide **provider health validation** at startup (API keys, Ollama availability, model availability)

## Capabilities

### New Capabilities

- `nl-query-input`: Accepts natural language questions from users via a Streamlit text input
- `sql-generation`: Translates natural language questions into valid, read-only SQLite SQL using an LLM and injected few-shot examples
- `sql-execution`: Executes generated SQL against the SQLite inventory database and returns results
- `result-presentation`: Displays query results as tables, numeric summaries, and human-readable responses in Streamlit
- `few-shot-retrieval`: Embeds the user question, retrieves semantically similar SQL examples from ChromaDB, and injects them into the SQL generation prompt
- `llm-provider-abstraction`: Common `LLMProvider` interface with implementations for Gemma (Ollama), Gemini (Google API), and OpenAI (GPT family)
- `runtime-provider-selection`: Allows switching the active LLM provider at startup via `MODEL_PROVIDER` environment variable and Streamlit dropdown, without code changes
- `provider-health-validation`: Validates API keys, Ollama availability, and model availability at startup with clear error messages
- `database-access`: Isolated read-only repository layer for SQLite query execution
- `vector-store`: ChromaDB-backed store for few-shot SQL examples with HuggingFace embeddings
- `container-deployment`: Docker Compose setup with an `app` container and optional `ollama` container for portable local deployment

### Modified Capabilities

<!-- No existing capabilities are being modified — this is a new project. -->

## Impact

- **New dependencies**: LangChain, ChromaDB, HuggingFace Transformers (embeddings), Streamlit, SQLite3, `langchain-google-genai`, `langchain-openai`, `langchain-ollama`
- **New infrastructure**: Docker Compose with two services (`app`, `ollama`); ChromaDB persisted locally under `chroma/`
- **Configuration**: `.env` file with `MODEL_PROVIDER`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `OLLAMA_BASE_URL`, `SQLITE_DB_PATH`
- **No Antigravity runtime dependency**: Antigravity is used only during development; the deployed application has no dependency on it
- **Platform**: Cross-platform via Docker Compose (Windows, macOS, Linux)
