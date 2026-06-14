## ADDED Requirements

### Requirement: Execute generated SQL against the SQLite inventory database
The system SHALL execute a validated SELECT statement against the SQLite database at the path specified by `SQLITE_DB_PATH` and return the result rows to the application layer.

#### Scenario: Successful query execution
- **WHEN** a valid SELECT SQL statement is passed to the database access layer
- **THEN** the system SHALL execute the query and return all matching rows

#### Scenario: SQL execution error
- **WHEN** the database encounters an error executing the SQL (e.g., syntax error, missing column)
- **THEN** the system SHALL catch the exception and return a user-readable error message without exposing raw database error traces

#### Scenario: Query returns no results
- **WHEN** a valid SELECT query matches zero rows
- **THEN** the system SHALL return an empty result set and the UI SHALL display a message indicating no results were found
