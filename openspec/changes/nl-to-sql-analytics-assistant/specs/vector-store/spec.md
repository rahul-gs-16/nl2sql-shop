## ADDED Requirements

### Requirement: Store and retrieve few-shot SQL examples using ChromaDB
The system SHALL maintain a ChromaDB collection of (question, SQL) example pairs embedded with HuggingFace sentence-transformer embeddings. The collection SHALL be persisted to disk under `chroma/` and SHALL be seeded automatically on first run from `data/examples/`.

#### Scenario: Collection seeded on first run
- **WHEN** the application starts and the ChromaDB collection is empty
- **THEN** the system SHALL load example pairs from `data/examples/` and add them to the collection with their embeddings

#### Scenario: Collection already populated on subsequent runs
- **WHEN** the application starts and the ChromaDB collection already contains examples
- **THEN** the system SHALL skip the seeding step and use the existing collection

#### Scenario: Semantic similarity search returns relevant examples
- **WHEN** a user question is embedded and a top-k similarity search is executed against the collection
- **THEN** the system SHALL return the k most semantically similar (question, SQL) pairs from the stored examples

### Requirement: Each stored example contains question, SQL query, and optional notes
Each document in the ChromaDB collection SHALL store the natural language question as the document text, the SQL query as metadata, and optionally a notes field as metadata.

#### Scenario: Example document structure is correct
- **WHEN** an example is retrieved from ChromaDB
- **THEN** the document SHALL have the question as the primary text and the SQL query accessible via metadata
