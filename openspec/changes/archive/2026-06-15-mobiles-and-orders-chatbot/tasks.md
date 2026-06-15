## 1. Database and Schema Refactoring

- [x] 1.1 Update `scripts/create_db.py` to create the new `products` table schema (model, variant, color, storage, stock, price).
- [x] 1.2 Update `scripts/create_db.py` to seed the database with Apple iPhone products matching the spec (specific colors, storages, and approximate prices).
- [x] 1.3 Update `scripts/create_db.py` to create the new `orders` table (id, customer_name, address, product_id, quantity, total_amount, order_date).
- [x] 1.4 Update `app/sql/schema.py` to reflect the new `products` and `orders` schemas and provide context for the LLM.

## 2. Data Access Layer Updates

- [x] 2.1 Add a new Python function in `app/database/repository.py` for placing an order (`place_order(customer_name, address, product_id, quantity)`).
- [x] 2.2 Implement transactional logic in `place_order` to check stock, insert the order record, and decrement product stock, rolling back on failure.
- [x] 2.3 Ensure `execute_query` remains strictly read-only by verifying no destructive keywords exist.

## 3. Retrieval and Prompts

- [x] 3.1 Rewrite `data/examples/examples.json` with new few-shot examples that query the updated `products` table and the new `orders` table (including cross-table JOINs).
- [x] 3.2 Ensure the vector store initialization (`app/retrieval/seeder.py`) uses the updated examples correctly.

## 4. UI and Conversational Logic

- [x] 4.1 Refactor `app/ui/main.py` to replace the simple form with `st.chat_message` and `st.chat_input`.
- [x] 4.2 Initialize and maintain chat history in `st.session_state`.
- [x] 4.3 Integrate a routing mechanism (using an LLM call with Langchain tools or a specialized prompt) to determine if the user wants to query data or place an order.
- [x] 4.4 If intent is query: append history, generate SQL, execute query, and display results in the chat.
- [x] 4.5 If intent is order: extract necessary parameters (name, address, product, quantity), call the `place_order` python function, and return success/failure to the chat.
