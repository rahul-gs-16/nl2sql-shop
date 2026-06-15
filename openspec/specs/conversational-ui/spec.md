## ADDED Requirements

### Requirement: Chat Interface
The system SHALL provide a conversational chat interface using Streamlit (`st.chat_message` and `st.chat_input`).

#### Scenario: User sends a message
- **WHEN** the user types a query or command into the chat input
- **THEN** the message appears as a user message bubble in the UI.

### Requirement: Chat Memory
The system SHALL maintain a history of the current conversation session.

#### Scenario: Contextual follow-up
- **WHEN** the user asks a follow-up question that depends on previous context
- **THEN** the system uses the conversation history to generate a correct response.

### Requirement: Intent Routing
The system SHALL determine whether a user's message is a query for information or an intent to place an order.

#### Scenario: Analytics query
- **WHEN** the user asks "How many blue iPhones do we have?"
- **THEN** the system routes the request to the NL2SQL generation pipeline.

#### Scenario: Order placement
- **WHEN** the user says "I want to buy 1 black iPhone 15 Pro 256GB"
- **THEN** the system routes the request to the order management Python function.
