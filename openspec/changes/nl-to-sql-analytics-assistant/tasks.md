## 1. Project Scaffold & Configuration

- [x] 1.1 Initialize repository structure: `app/`, `data/`, `chroma/`, `docker/`, `tests/` directories
- [x] 1.2 Create `app/config/`, `app/providers/`, `app/retrieval/`, `app/sql/`, `app/database/`, `app/ui/` submodules
- [x] 1.3 Create `.env.example` with `MODEL_PROVIDER`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `OLLAMA_BASE_URL`, `SQLITE_DB_PATH`
- [x] 1.4 Create `requirements.txt` with pinned versions: `streamlit`, `langchain`, `langchain-google-genai`, `langchain-openai`, `langchain-ollama`, `chromadb`, `sentence-transformers`, `sqlite3` (stdlib)
- [x] 1.5 Create `app/config/settings.py` to load and validate all environment variables at import time

## 2. Database Layer

- [x] 2.1 Create the SQLite inventory database at `data/inventory.db` with the retail inventory schema (products table with name, category, colour, size, stock, price, discount columns)
- [x] 2.2 Create `app/database/repository.py` with `execute_query(sql: str) -> list[tuple]` function
- [x] 2.3 Implement read-only enforcement in `execute_query`: parse first keyword, reject DELETE/UPDATE/INSERT/DROP/ALTER with a clear exception
- [x] 2.4 Add startup validation in `repository.py` to check `SQLITE_DB_PATH` exists and raise a clear error if not

## 3. LLM Provider Abstraction

- [x] 3.1 Create `app/providers/base.py` with abstract `LLMProvider` class defining `generate(prompt: str, temperature: float = 0) -> str`
- [x] 3.2 Create `app/providers/gemma.py` implementing `GemmaProvider` using `langchain-ollama` pointed at `OLLAMA_BASE_URL` with `gemma3` model
- [x] 3.3 Create `app/providers/gemini.py` implementing `GeminiProvider` using `langchain-google-genai` with `GOOGLE_API_KEY`
- [x] 3.4 Create `app/providers/openai.py` implementing `OpenAIProvider` using `langchain-openai` with `OPENAI_API_KEY`
- [x] 3.5 Create `app/providers/factory.py` with `get_provider(name: str) -> LLMProvider` factory that reads `MODEL_PROVIDER` and returns the correct instance; raise a clear error for unknown values

## 4. Provider Health Validation

- [x] 4.1 Create `app/providers/health.py` with `validate_provider(name: str)` function
- [x] 4.2 Implement API key presence check for `gemini` (requires `GOOGLE_API_KEY`) and `openai` (requires `OPENAI_API_KEY`)
- [x] 4.3 Implement Ollama reachability check for `gemma`: attempt HTTP GET to `OLLAMA_BASE_URL` with a short timeout; raise descriptive error if unreachable
- [x] 4.4 Call `validate_provider` during application startup before serving any queries
- [x] 4.5 When `MODEL_PROVIDER` is not `gemma` and Ollama is unavailable, log a warning but continue startup

## 5. Vector Store & Few-Shot Retrieval

- [x] 5.1 Create `data/examples/examples.json` with at least 10 (question, SQL, notes) example pairs covering the inventory schema
- [x] 5.2 Create `app/retrieval/store.py` with `initialize_store() -> Chroma` that opens or creates the ChromaDB collection at `chroma/` using HuggingFace `all-MiniLM-L6-v2` embeddings
- [x] 5.3 Create `app/retrieval/seeder.py` with `seed_if_empty(store: Chroma)` that loads `data/examples/examples.json` and populates the collection if it is empty
- [x] 5.4 Create `app/retrieval/retriever.py` with `retrieve_examples(question: str, store: Chroma, k: int = 3) -> list[dict]` that embeds the question and returns top-k similar (question, SQL) pairs
- [x] 5.5 Call `seed_if_empty` during application startup after the store is initialized

## 6. SQL Generation Layer

- [x] 6.1 Create `app/sql/prompt.py` with `build_prompt(question: str, examples: list[dict], schema: str) -> str` that constructs the few-shot SQL generation prompt
- [x] 6.2 Define the inventory schema string (table name, columns, types) in `app/sql/schema.py`
- [x] 6.3 Create `app/sql/generator.py` with `generate_sql(question: str, provider: LLMProvider, store: Chroma) -> str` that orchestrates retrieval → prompt building → LLM call → SQL extraction
- [x] 6.4 Implement SQL extraction/cleaning in `generator.py` to strip markdown code fences and whitespace from LLM output
- [x] 6.5 After generation, pass the extracted SQL through the read-only validator before returning it

## 7. Streamlit UI

- [x] 7.1 Create `app/ui/app.py` as the main Streamlit entry point
- [x] 7.2 Add provider selection dropdown (Gemma, Gemini, ChatGPT) using `st.selectbox`; disable Gemma option if Ollama is unavailable
- [x] 7.3 Add natural language question text input (`st.text_input`) and a "Run Query" submit button
- [x] 7.4 On submit: call `generate_sql`, display generated SQL in an expandable `st.expander`, call `execute_query`, display results as `st.dataframe`
- [x] 7.5 Handle empty input: show `st.warning` if user submits without entering a question
- [x] 7.6 Handle pipeline errors: catch all exceptions and display with `st.error` (user-readable message, no traceback)
- [x] 7.7 Handle empty result set: display `st.info("No results found for your query.")` when query returns zero rows

## 8. Docker & Deployment

- [x] 8.1 Create `docker/Dockerfile` for the `app` service: Python base image, install `requirements.txt`, copy app source, expose port 8501, entrypoint `streamlit run app/ui/app.py`
- [x] 8.2 Create `docker-compose.yml` with `app` service (mounts `data/`, `chroma/`, `.env`) and optional `ollama` service (official `ollama/ollama` image, mounts model volume)
- [x] 8.3 Set `OLLAMA_BASE_URL=http://ollama:11434` as the default in `.env.example` for Docker networking
- [x] 8.4 Verify cross-platform startup: test `docker compose up` on Windows with cloud provider only

## 9. Tests

- [x] 9.1 Write unit test for `execute_query` read-only enforcement (assert DELETE/UPDATE/INSERT/DROP/ALTER raise exceptions)
- [x] 9.2 Write unit test for `get_provider` factory (assert correct class returned for each valid `MODEL_PROVIDER` value; assert error for invalid value)
- [x] 9.3 Write unit test for `build_prompt` (assert few-shot examples are included in the output)
- [x] 9.4 Write unit test for `retrieve_examples` with a pre-seeded in-memory ChromaDB (assert top-k returns correct examples)
- [x] 9.5 Write integration test: seed store → retrieve → build prompt → assert prompt contains relevant SQL example

## 10. Documentation

- [x] 10.1 Create `README.md` with project overview, prerequisites (Docker, API keys), quickstart (`docker compose up`), and provider configuration guide
- [x] 10.2 Document expected HuggingFace model download on first run in README
- [x] 10.3 Add inline docstrings to all public functions across `providers/`, `retrieval/`, `sql/`, `database/`
