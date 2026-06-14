# Project Title

Natural Language to SQL Analytics Assistant using Antigravity, LangChain, SQLite, Streamlit, and Multi-Provider LLM Support

---

# 1. Overview

## Purpose

Build a demo-grade Generative AI application that allows business users to query a retail inventory database using natural language.

The application shall translate user questions into SQL queries, execute those queries against a SQLite database, and return human-readable results through a Streamlit interface.

The project is based on the Codebasics Natural Language to SQL tutorial but replaces Google PaLM with a modular multi-provider LLM architecture supporting:

* Local Gemma via Ollama
* Gemini via Google API
* ChatGPT via OpenAI API

The implementation shall use Antigravity during development but shall not depend on Antigravity at runtime.

---

# 2. Goals

## Primary Goals

* Query SQLite databases using natural language
* Support multiple LLM providers through a common abstraction layer
* Allow runtime model selection
* Support local-first execution
* Provide a simple Streamlit interface
* Use vector-based few-shot retrieval for improved SQL generation accuracy
* Keep deployment simple and portable across developer machines

## Non-Goals

* Multi-tenant deployments
* Production-grade authentication
* Distributed execution
* High-availability infrastructure
* Kubernetes deployment
* Agentic workflows beyond SQL generation

---

# 3. High-Level Architecture

```text
User
 │
 ▼
Streamlit UI
 │
 ▼
Application Layer
 │
 ├── LLM Provider Layer
 │
 ├── Few-Shot Retrieval Layer
 │
 ├── SQL Generation Layer
 │
 └── Database Access Layer
 │
 ▼
SQLite Database

Few-Shot Examples
 │
 ▼
ChromaDB Vector Store

Optional Local LLM
 │
 ▼
Ollama + Gemma
```

---

# 4. Functional Requirements

## FR-001 Natural Language Query Input

Users shall be able to enter natural language questions through Streamlit.

Example:

* How many white t-shirts are available?
* What is the total revenue from Nike products?
* Which products have discounts greater than 20%?

---

## FR-002 SQL Generation

The system shall generate valid SQLite-compatible SQL statements from user prompts.

Generated SQL must:

* Use only known tables
* Use only known columns
* Avoid destructive operations

Allowed:

* SELECT
* Aggregation
* Filtering
* Sorting

Disallowed:

* DELETE
* UPDATE
* INSERT
* DROP
* ALTER

---

## FR-003 SQL Execution

The generated SQL shall be executed against SQLite.

Results shall be returned to the application layer.

---

## FR-004 Result Presentation

Results shall be displayed in Streamlit as:

* Tables
* Numeric summaries
* Human-readable responses

---

## FR-005 Few-Shot Learning Support

The system shall improve SQL generation using retrieved examples.

Examples shall contain:

* Natural language question
* Correct SQL query

Examples shall be stored in ChromaDB.

---

## FR-006 Semantic Retrieval

The application shall retrieve relevant examples before SQL generation.

Process:

1. User question received
2. Embedding generated
3. Similar examples retrieved
4. Examples injected into prompt
5. SQL generated

---

## FR-007 Runtime LLM Selection

At startup, users shall select one of:

* Gemma
* Gemini
* ChatGPT

Example:

```bash
MODEL_PROVIDER=gemma
```

```bash
MODEL_PROVIDER=gemini
```

```bash
MODEL_PROVIDER=openai
```

---

## FR-008 Local Model Optionality

The system shall not require Ollama.

If Ollama is unavailable:

* Gemma provider shall be disabled
* Gemini and OpenAI providers shall remain functional

Application startup must not fail.

---

## FR-009 Provider Health Validation

Application startup shall validate:

* API keys
* Ollama availability
* Model availability

Failures shall produce clear messages.

---

# 5. LLM Provider Abstraction

## Objective

The application shall isolate all LLM-specific logic behind a common interface.

---

## Interface

```python
class LLMProvider:

    def generate(
        self,
        prompt: str,
        temperature: float = 0
    ) -> str:
        pass
```

---

## Supported Implementations

### GemmaProvider

Backend:

* Ollama

Supported Models:

* gemma3
* future local models

---

### GeminiProvider

Backend:

* Google Generative AI API

Supported Models:

* Gemini family

---

### OpenAIProvider

Backend:

* OpenAI API

Supported Models:

* GPT family

---

## Switching Requirement

No business logic changes shall be required when switching providers.

Only configuration changes shall be necessary.

---

# 6. Database Requirements

## Database Type

SQLite

---

## Database Storage

Database shall be stored as:

```text
/data/inventory.db
```

---

## Database Access

Database access shall be isolated behind a repository layer.

Example:

```python
execute_query(sql: str)
```

---

## Database Security

Only read-only SQL execution shall be allowed.

---

# 7. Embedding and Vector Store

## Embedding Provider

Initial implementation:

* HuggingFace embeddings

Future providers may be added.

---

## Vector Database

ChromaDB

---

## Stored Metadata

Each example shall contain:

```text
Question
SQL Query
Optional Notes
```

---

# 8. Streamlit Requirements

## Features

### Query Input

Text box for questions.

### Provider Selection

Dropdown:

* Gemma
* Gemini
* ChatGPT

### Query Execution

Submit button.

### SQL Display

Optional expandable section showing generated SQL.

### Results Display

Results table.

### Error Display

Readable error messages.

---

# 9. Container Architecture

## Design Principles

* Minimal
* Portable
* Easy onboarding
* Local development focused

---

## Container 1

### app

Contains:

* Streamlit
* Antigravity-generated application code
* LangChain
* ChromaDB
* SQLite file access
* Provider implementations

---

## Container 2

### ollama

Contains:

* Ollama runtime
* Gemma model

Optional container.

May be disabled.

---

## Docker Compose

```text
services:

  app

  ollama
```

No additional infrastructure containers shall be required.

---

# 10. Configuration Management

## Environment Variables

```env
MODEL_PROVIDER=gemma

OPENAI_API_KEY=

GOOGLE_API_KEY=

OLLAMA_BASE_URL=http://ollama:11434

SQLITE_DB_PATH=/data/inventory.db
```

---

# 11. Non-Functional Requirements

## NFR-001 Simplicity

Architecture shall prioritize simplicity over extensibility.

---

## NFR-002 Portability

Application shall run on:

* Windows
* macOS
* Linux

through Docker Compose.

---

## NFR-003 Startup Time

Application startup shall complete within acceptable local development limits.

---

## NFR-004 Maintainability

Provider-specific code shall remain isolated.

---

## NFR-005 Extensibility

Adding a new provider shall require:

* New provider implementation
* Registration entry

No application workflow changes.

---

# 12. Repository Structure

```text
repo/

├── app/
│   ├── ui/
│   ├── providers/
│   ├── retrieval/
│   ├── sql/
│   ├── database/
│   └── config/
│
├── data/
│   ├── inventory.db
│   └── examples/
│
├── chroma/
│
├── docker/
│
├── tests/
│
├── docker-compose.yml
│
├── .env.example
│
├── requirements.md
│
└── README.md
```

---

# 13. Acceptance Criteria

## AC-001

User submits a natural language question.

System generates valid SQL.

System returns results.

---

## AC-002

User can switch between:

* Gemma
* Gemini
* ChatGPT

without code changes.

---

## AC-003

Application runs successfully with:

* App container only

when cloud providers are used.

---

## AC-004

Application runs successfully with:

* App container
* Ollama container

when Gemma is selected.

---

## AC-005

Few-shot retrieval improves SQL generation through ChromaDB example retrieval.

---

## AC-006

Project can be cloned and started using:

```bash
docker compose up
```

with no additional infrastructure requirements.
