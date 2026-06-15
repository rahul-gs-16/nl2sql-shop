## Context

The current application is a read-only Streamlit app that uses LangChain and ChromaDB to translate natural language into SQL queries against an inventory database containing T-shirts and jeans.

The objective is to pivot this into an interactive, conversational chatbot for an Apple mobile device store. The chatbot will need to support conversational turns (memory) and be capable of placing orders, which requires write access to the database to insert order records and update inventory stock.

## Goals / Non-Goals

**Goals:**
- Pivot the database schema to reflect Apple iPhone models, variants, colors, and storage capacities.
- Transform the Streamlit UI from a single-shot query form to a conversational chat interface.
- Add an `orders` table to track customer purchases.
- Implement application-level transaction logic to place orders (insert into `orders`, decrement `stock` in `products`).
- Safely integrate LLM-based NL-to-SQL for query purposes while keeping destructive operations strictly in application code.

**Non-Goals:**
- Implementing actual payment gateways.
- Advanced user authentication/login.
- Multi-tenant architecture.
- Allowing the LLM to generate `INSERT` or `UPDATE` SQL statements directly.

## Decisions

### 1. Separation of Concerns: Read vs. Write Operations
- **Decision:** Keep the LLM-generated SQL strictly read-only (`SELECT` only). Order placement will be handled by explicit application-level Python functions.
- **Rationale:** Allowing an LLM to generate destructive SQL (`INSERT`, `UPDATE`) is extremely unsafe and prone to hallucination. By intercepting order intent and routing it to a structured Python function, we ensure transactional integrity and data safety. We will use Langchain's tool-calling capabilities (or a routing prompt) to determine if the user wants to *query* data (use NL2SQL) or *place an order* (use Python function).

### 2. Conversational UI Implementation
- **Decision:** Use Streamlit's built-in `st.chat_message` and `st.chat_input` widgets. Store conversation history in `st.session_state`.
- **Rationale:** This is the standard, supported way to build chatbots in Streamlit and provides a familiar chat interface natively.

### 3. Database Schema Updates
- **Decision:** 
  - `products`: Drop `discount` and `category`. Add `model` (e.g., iPhone 16), `variant` (Standard, Pro, Pro Max), `color` (Black, White, Blue, Pink), `storage` (128GB, 256GB, 512GB, 1TB), `stock`, `price`.
  - `orders`: Add table with `id`, `customer_name`, `address`, `product_id` (FK), `quantity`, `total_amount`, `order_date`.
- **Rationale:** Directly maps to the user's requirements for product offerings and order capture.

### 4. Handling LLM Memory
- **Decision:** Use LangChain's memory components (e.g., `ConversationBufferMemory`) to pass chat history to the LLM for context-aware responses (e.g., User: "How many black iPhone 15s are there?" -> Bot: "10" -> User: "Order 2 of them").

## Risks / Trade-offs

- **Risk:** Routing ambiguity (LLM gets confused whether to generate SQL or trigger an order).
  - **Mitigation:** Provide clear system prompts and strictly define the order-taking tool/function signature.
- **Risk:** Stock race conditions.
  - **Mitigation:** Use SQLite transactions. The Python function must check if `stock >= requested_quantity` within the same transaction block that performs the update.
- **Risk:** Few-shot examples become stale.
  - **Mitigation:** The design mandates a complete rewrite of `examples.json` to match the new mobile schema and including cross-table queries.
