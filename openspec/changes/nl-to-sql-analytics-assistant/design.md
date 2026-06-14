## Context

This project introduces a new demo-grade Generative AI application for querying a retail inventory database using natural language. The application is built from scratch — it replaces the original Codebasics single-provider Google PaLM implementation with a modular, multi-provider LLM architecture. Antigravity is used during development only; the runtime has no Antigravity dependency.

The system sits on top of:
- **SQLite** for structured retail inventory data
- **LangChain** for prompt chaining and LLM abstraction
- **ChromaDB + HuggingFace embeddings** for few-shot SQL example retrieval
- **Streamlit** for the user interface
- **Docker Compose** for portable local deployment

## Goals / Non-Goals

**Goals:**
- Provide a clean LLM provider abstraction that isolates Gemma, Gemini, and OpenAI behind a single interface
- Enable runtime provider switching via `MODEL_PROVIDER` environment variable without any code changes
- Integrate few-shot retrieval using ChromaDB so that semantically similar SQL examples are injected into the prompt before SQL generation
- Enforce read-only SQL execution at the database layer
- Package the full stack in Docker Compose for one-command startup
- Validate provider health at startup with actionable error messages

**Non-Goals:**
- Production-grade authentication or multi-tenancy
- Distributed execution or high-availability infrastructure
- Kubernetes deployment
- Agentic workflows beyond SQL generation
- Streaming LLM responses
- Fine-tuning or training models

## Decisions

### Decision 1: LLM Provider Abstraction via a Python Abstract Base Class

**Choice**: Define a `LLMProvider` abstract base class with a single `generate(prompt, temperature) -> str` method. Each provider (Gemma, Gemini, OpenAI) implements this interface. A factory function reads `MODEL_PROVIDER` and returns the correct concrete instance.

**Rationale**: Keeps business logic (SQL generation, prompt construction) completely decoupled from provider-specific SDK calls. Adding a new provider requires only a new subclass and a factory registration — no workflow changes.

**Alternative considered**: Using LangChain's built-in `BaseChatModel` directly throughout the codebase. Rejected because it couples the core pipeline to LangChain's interface and makes provider-specific error handling harder to isolate.

---

### Decision 2: Few-Shot Retrieval with ChromaDB + HuggingFace Embeddings

**Choice**: Store natural-language-to-SQL example pairs in a ChromaDB collection. At query time, embed the user question using a HuggingFace sentence-transformer model and retrieve the top-k most similar examples. Inject retrieved examples into the SQL generation prompt.

**Rationale**: Vector-based semantic retrieval improves SQL generation accuracy versus static few-shot prompts, especially for diverse phrasings of similar questions. HuggingFace embeddings run locally with no API cost or latency for the embedding step.

**Alternative considered**: Using OpenAI embeddings. Rejected to preserve local-first execution (Gemma path must work without any external API calls).

---

### Decision 3: SQLite as the Only Database Backend

**Choice**: Use SQLite with a file at `/data/inventory.db`. All database access is mediated through a thin repository layer exposing only `execute_query(sql: str)`.

**Rationale**: SQLite is zero-infrastructure, portable, and sufficient for demo-scale retail inventory data. The repository layer enforces read-only access by intercepting or rejecting non-SELECT statements.

**Alternative considered**: PostgreSQL. Rejected — adds infrastructure complexity without benefit at demo scale.

---

### Decision 4: Docker Compose with Two Services

**Choice**: `app` service contains Streamlit, LangChain, ChromaDB client, and all provider implementations. `ollama` service is optional and can be disabled. No additional infrastructure containers.

**Rationale**: Minimizes onboarding friction — a developer can run the cloud providers with just `docker compose up app` and opt into Gemma by also starting `ollama`.

**Alternative considered**: Single monolithic container with Ollama embedded. Rejected because it forces a multi-GB image on all users, even those who only use cloud providers.

---

### Decision 5: Read-Only SQL Enforcement at the Application Layer

**Choice**: Before executing any generated SQL, validate it at the application layer by parsing the first token. Reject any statement that is not `SELECT`. Return a user-visible error message.

**Rationale**: SQLite does not natively enforce read-only connections in all drivers. Application-layer validation is explicit, testable, and provider-agnostic.

**Alternative considered**: Opening SQLite in `SQLITE_OPEN_READONLY` mode. This is a valid secondary defense but does not produce user-friendly error messages on its own.

## Risks / Trade-offs

- **LLM-generated SQL may be incorrect** → Mitigation: Few-shot retrieval reduces error rate; the UI displays generated SQL so users can inspect it; only `SELECT` is permitted so incorrect queries cannot cause data loss.
- **Ollama cold-start is slow** → Mitigation: Documented in README; the Ollama container can be pre-warmed; cloud providers are unaffected.
- **ChromaDB persistence across container restarts** → Mitigation: Mount `chroma/` as a Docker volume so embeddings persist; provide a seed script to repopulate from examples on first run.
- **HuggingFace model download on first run** → Mitigation: Document expected download; consider caching the model inside the Docker image in a future iteration.
- **Provider API key management** → Mitigation: Use `.env` file (never committed); provide `.env.example` with all required keys documented.
- **Single SQLite file as shared state** → Mitigation: Read-only access prevents corruption; file is mounted as a Docker volume.

## Migration Plan

This is a new project with no existing production deployment. Steps to bootstrap:

1. Clone repository
2. Copy `.env.example` to `.env`, fill in API keys for desired provider(s)
3. Run `docker compose up` (adds `ollama` service if Gemma is selected)
4. The `app` container runs a seed script on startup to populate ChromaDB with few-shot examples if not already present
5. Streamlit UI is accessible at `http://localhost:8501`

Rollback: Not applicable for a new project. Subsequent iterations can use feature flags on the `MODEL_PROVIDER` variable.
