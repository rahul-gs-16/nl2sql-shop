## ADDED Requirements

### Requirement: Retrieve semantically similar few-shot SQL examples before generation
Before invoking the LLM for SQL generation, the system SHALL embed the user's natural language question and retrieve the top-k most semantically similar (question, SQL) example pairs from the ChromaDB vector store. The retrieved examples SHALL be injected into the SQL generation prompt.

#### Scenario: Examples retrieved for a known question pattern
- **WHEN** a user submits a question semantically similar to stored examples
- **THEN** the retrieval layer SHALL return at least one matching (question, SQL) pair to be included in the prompt

#### Scenario: No similar examples found
- **WHEN** the user's question is not semantically similar to any stored example
- **THEN** the system SHALL proceed with SQL generation using only the schema context (zero-shot) and SHALL NOT fail

#### Scenario: ChromaDB collection seeded on first run
- **WHEN** the application starts and the ChromaDB collection is empty
- **THEN** the system SHALL seed the collection with the predefined few-shot examples from the `data/examples/` directory before serving any user queries
