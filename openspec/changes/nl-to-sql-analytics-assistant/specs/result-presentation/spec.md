## ADDED Requirements

### Requirement: Display query results in the Streamlit UI
The system SHALL present query results to the user in a clear, readable format including a data table, numeric summaries where applicable, and human-readable interpretation.

#### Scenario: Results displayed as a table
- **WHEN** the query returns one or more rows
- **THEN** the system SHALL display the results in a Streamlit data table with column headers

#### Scenario: Expandable SQL display
- **WHEN** query results are shown
- **THEN** the system SHALL provide an optional expandable section that reveals the generated SQL query used to produce the results

#### Scenario: Error displayed clearly
- **WHEN** any stage of the pipeline (SQL generation, validation, execution) fails
- **THEN** the system SHALL display a human-readable error message in the UI and SHALL NOT show a Python traceback to the user

#### Scenario: Empty results communicated to user
- **WHEN** the query executes successfully but returns zero rows
- **THEN** the system SHALL display a message such as "No results found for your query" instead of an empty table
