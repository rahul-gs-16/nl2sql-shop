## ADDED Requirements

### Requirement: Query Across Products and Orders
The system SHALL support natural language queries that span both the `products` and `orders` tables.

#### Scenario: Cross-table query
- **WHEN** the user asks "Show me all orders for blue iPhones"
- **THEN** the generated SQL includes a JOIN between the `orders` and `products` tables.

## MODIFIED Requirements

### Requirement: Prompt Generation
The system SHALL generate a prompt containing the updated schema and relevant few-shot examples.

#### Scenario: Updated Schema Injection
- **WHEN** the SQL generator builds the prompt
- **THEN** the injected schema string describes both the new `products` table (model, variant, color, storage) and the new `orders` table, and explicitly disallows destructive operations.
