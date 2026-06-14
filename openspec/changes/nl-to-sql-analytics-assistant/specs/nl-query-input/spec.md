## ADDED Requirements

### Requirement: User enters a natural language question
The system SHALL provide a text input field in the Streamlit UI where users can type any natural language question about the retail inventory database.

#### Scenario: User submits a valid natural language question
- **WHEN** a user types a natural language question into the text input and clicks the submit button
- **THEN** the system SHALL accept the input and pass it to the SQL generation pipeline

#### Scenario: User submits an empty question
- **WHEN** a user clicks the submit button with an empty text input
- **THEN** the system SHALL display a validation message prompting the user to enter a question and SHALL NOT invoke the SQL generation pipeline
