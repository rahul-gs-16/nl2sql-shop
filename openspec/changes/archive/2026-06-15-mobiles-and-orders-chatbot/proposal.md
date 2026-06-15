## Why

The current demo application is limited to querying a read-only inventory database containing T-shirts and jeans. To demonstrate a more realistic and interactive e-commerce scenario, the system needs to be updated to handle a mobile phone store (specifically Apple iPhones), and provide a conversational chatbot interface that allows users to not only query stock but also place orders.

## What Changes

- Update the database schema and seed data to support iPhone models, variants, colours, storage capacities, and stock.
- Remove the unused `discount` logic from the database and prompts.
- Implement a conversational chat interface in Streamlit to replace the basic form submission.
- Add an `orders` table to track customer purchases.
- Add application logic (Python functions) to handle order placement, including writing to the `orders` table and updating stock in the `products` table transactionally.
- Update the SQL generation layer (prompts, few-shot examples) to support both the `products` and `orders` tables.

## Capabilities

### New Capabilities

- `mobile-inventory`: Handling iPhone specific inventory data (model, variant, color, storage).
- `conversational-ui`: A chat-based Streamlit interface supporting multi-turn interactions.
- `order-management`: Functionality to place orders and manage transactional updates to inventory and order records.

### Modified Capabilities

- `nl2sql-generation`: Updated to handle queries across both the new `products` schema and the new `orders` table.

## Impact

- `scripts/create_db.py`: Complete rewrite of the schema and seed data generation.
- `app/ui/main.py`: Major UI overhaul to implement `st.chat_message` and `st.chat_input` based conversational interface.
- `app/database/repository.py`: Addition of transactional write functions for order processing, relaxing the strict read-only nature of the repository *for application code only* (LLM SQL generation remains read-only).
- `app/sql/schema.py`: Schema string update for the LLM prompt.
- `data/examples/examples.json`: Rewrite of all few-shot examples to match the new schema and use cases.
