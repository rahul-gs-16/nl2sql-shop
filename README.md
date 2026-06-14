# NL → SQL Analytics Assistant

A demo-grade Generative AI application that lets business users query a **retail inventory SQLite database using natural language**. The application translates plain-English questions into SQL queries, executes them, and displays the results — all through a Streamlit interface.

Supports three LLM backends switchable at runtime with no code changes:
| Provider | Backend | Requires |
|---|---|---|
| **Gemma (local)** | Ollama (gemma3) | Ollama running locally or via Docker |
| **Gemini** | Google Generative AI API | `GOOGLE_API_KEY` |
| **ChatGPT** | OpenAI API | `OPENAI_API_KEY` |

Few-shot SQL examples are stored in ChromaDB with HuggingFace embeddings and retrieved semantically before each query to improve accuracy.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Docker & Docker Compose | v2+ recommended |
| (Optional) Ollama | Only needed for Gemma local execution |
| Google API key | Only needed for `MODEL_PROVIDER=gemini` |
| OpenAI API key | Only needed for `MODEL_PROVIDER=openai` |

---

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd nl-sql-analytics-assistant

# 2. Create your .env from the template
cp .env.example .env
# Edit .env — set MODEL_PROVIDER and the relevant API key

# 3. Start the application
docker compose up

# 4. Open in browser
# http://localhost:8501
```

---

## Provider Configuration

### Gemini (Google)

```env
MODEL_PROVIDER=gemini
GOOGLE_API_KEY=<your-google-generative-ai-key>
```

Start with:
```bash
docker compose up app
```

### ChatGPT (OpenAI)

```env
MODEL_PROVIDER=openai
OPENAI_API_KEY=<your-openai-api-key>
```

Start with:
```bash
docker compose up app
```

### Gemma (Local / Ollama)

```env
MODEL_PROVIDER=gemma
OLLAMA_BASE_URL=http://ollama:11434
```

Start with (includes the Ollama container):
```bash
docker compose --profile ollama up
```

Then pull the model (first run only):
```bash
docker exec -it <ollama-container-id> ollama pull gemma3
```

> **Note:** The first run will download the `gemma3` model (~5 GB). Subsequent starts reuse the cached model from the `ollama_models` Docker volume.

---

## HuggingFace Model Download

On first startup, the application downloads the `all-MiniLM-L6-v2` sentence-transformer model (~90 MB) used for embedding few-shot examples into ChromaDB. This is a one-time download; the model is cached inside the container layer. Subsequent starts use the cached model immediately.

---

## Repository Structure

```
.
├── app/
│   ├── config/          # Environment variable loading (settings.py)
│   ├── database/        # Read-only SQLite repository
│   ├── providers/       # LLM provider abstraction (base, gemma, gemini, openai, factory, health)
│   ├── retrieval/       # ChromaDB store, seeder, retriever
│   ├── sql/             # Schema string, prompt builder, SQL generator
│   └── ui/              # Streamlit entry point (app.py)
├── data/
│   ├── inventory.db     # SQLite retail inventory database
│   └── examples/        # Few-shot examples JSON
├── chroma/              # ChromaDB persistence directory (Docker volume)
├── docker/
│   └── Dockerfile
├── scripts/
│   └── create_db.py     # Creates and seeds inventory.db
├── tests/               # Unit and integration tests
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

> Tests for `test_retriever.py` and `test_integration_retrieval.py` require `sentence-transformers` and will download `all-MiniLM-L6-v2` on the first run.

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `MODEL_PROVIDER` | `gemma` | Active LLM provider: `gemma`, `gemini`, or `openai` |
| `GOOGLE_API_KEY` | _(empty)_ | Google Generative AI API key (Gemini provider) |
| `OPENAI_API_KEY` | _(empty)_ | OpenAI API key (ChatGPT provider) |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama API base URL (Gemma provider) |
| `SQLITE_DB_PATH` | `/data/inventory.db` | Path to the SQLite database file |
| `CHROMA_PERSIST_DIR` | `/chroma` | Directory for ChromaDB persistence |
| `EXAMPLES_PATH` | `/data/examples/examples.json` | Path to few-shot examples JSON |
| `RETRIEVAL_K` | `3` | Number of few-shot examples retrieved per query |

---

## Architecture

```
User
 │
 ▼
Streamlit UI (app/ui/app.py)
 │
 ├── LLM Provider Layer (app/providers/)
 │    ├── GemmaProvider  → Ollama API
 │    ├── GeminiProvider → Google Generative AI
 │    └── OpenAIProvider → OpenAI Chat API
 │
 ├── Few-Shot Retrieval Layer (app/retrieval/)
 │    ├── ChromaDB vector store
 │    └── HuggingFace sentence-transformers (all-MiniLM-L6-v2)
 │
 ├── SQL Generation Layer (app/sql/)
 │    ├── Prompt builder (schema + examples + question)
 │    └── SQL extractor & read-only validator
 │
 └── Database Access Layer (app/database/)
      └── Read-only SQLite repository (SELECT only)
```
