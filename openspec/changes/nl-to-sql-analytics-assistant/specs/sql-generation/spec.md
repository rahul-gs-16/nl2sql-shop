## ADDED Requirements

### Requirement: Generate valid read-only SQL from a natural language question
The system SHALL translate a natural language question into a valid SQLite-compatible SELECT statement using an LLM and few-shot examples injected into the prompt. The generated SQL MUST use only known tables and columns from the inventory schema and MUST NOT contain any destructive operations.

#### Scenario: Successful SQL generation for a valid question
- **WHEN** the SQL generation layer receives a natural language question with retrieved few-shot examples
- **THEN** the system SHALL produce a valid SQLite SELECT statement that correctly targets the appropriate tables and columns

#### Scenario: Generated SQL contains only SELECT operations
- **WHEN** the SQL generation layer produces output
- **THEN** the system SHALL validate that the first statement keyword is SELECT and SHALL reject any output containing DELETE, UPDATE, INSERT, DROP, or ALTER

#### Scenario: Generated SQL references unknown table or column
- **WHEN** the LLM produces SQL referencing a table or column not in the known schema
- **THEN** the system SHALL surface an error to the user indicating the query could not be executed safely and SHALL NOT execute the malformed SQL
