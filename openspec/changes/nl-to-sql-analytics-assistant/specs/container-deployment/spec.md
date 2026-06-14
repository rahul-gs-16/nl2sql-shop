## ADDED Requirements

### Requirement: Application packaged as Docker Compose with app and optional ollama services
The system SHALL be deployable using a single `docker compose up` command. The `app` service SHALL contain Streamlit, LangChain, ChromaDB client, HuggingFace embeddings, SQLite access, and all provider implementations. The `ollama` service SHALL be optional and may be omitted when using cloud providers.

#### Scenario: Full stack startup with Gemma (app + ollama)
- **WHEN** a developer runs `docker compose up` with `MODEL_PROVIDER=gemma`
- **THEN** both the `app` container and the `ollama` container SHALL start, and the Streamlit UI SHALL be accessible at `http://localhost:8501`

#### Scenario: Cloud-only startup (app only)
- **WHEN** a developer runs `docker compose up app` with `MODEL_PROVIDER=gemini` or `MODEL_PROVIDER=openai`
- **THEN** only the `app` container SHALL start and the application SHALL function fully without the `ollama` service

#### Scenario: One-command clone and start
- **WHEN** a developer clones the repository, copies `.env.example` to `.env`, fills in API keys, and runs `docker compose up`
- **THEN** the application SHALL start successfully with no additional infrastructure setup required

### Requirement: No additional infrastructure containers beyond app and ollama
The Docker Compose configuration SHALL define only `app` and `ollama` services. No databases, message brokers, or other infrastructure containers SHALL be required.

#### Scenario: Minimal Docker Compose services
- **WHEN** the `docker-compose.yml` is inspected
- **THEN** it SHALL contain exactly two service definitions: `app` and `ollama`
