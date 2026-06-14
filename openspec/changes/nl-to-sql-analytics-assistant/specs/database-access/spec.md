## ADDED Requirements

### Requirement: Isolated read-only database access layer
The system SHALL expose database access through a repository layer with a single `execute_query(sql: str)` function. Direct database access from the UI or SQL generation layers is NOT permitted. The layer MUST enforce read-only execution by rejecting any SQL that is not a SELECT statement before execution.

#### Scenario: Read-only SELECT query executed successfully
- **WHEN** `execute_query` is called with a valid SELECT statement
- **THEN** the function SHALL execute the query against the SQLite database and return the result rows

#### Scenario: Destructive SQL rejected before execution
- **WHEN** `execute_query` is called with a DELETE, UPDATE, INSERT, DROP, or ALTER statement
- **THEN** the function SHALL raise an exception with a message indicating only read operations are permitted and SHALL NOT execute the statement against the database

#### Scenario: Database file not found
- **WHEN** the SQLite database file does not exist at `SQLITE_DB_PATH`
- **THEN** the system SHALL display a clear startup error indicating the database path is invalid
