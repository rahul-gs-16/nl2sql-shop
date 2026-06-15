"""
app/sql/schema.py

Defines the inventory database schema as a plain string that is injected into
SQL generation prompts. Keep this in sync with scripts/create_db.py.
"""

INVENTORY_SCHEMA = """
Table: products
Columns:
  id        INTEGER  - Primary key (auto-increment)
  model     TEXT     - Product model (e.g. 'iPhone 15', 'iPhone 16')
  variant   TEXT     - Product variant ('Standard', 'Pro', 'Pro Max')
  color     TEXT     - Product color ('Black', 'White', 'Blue', 'Pink')
  storage   TEXT     - Storage capacity ('128GB', '256GB', '512GB', '1TB')
  stock     INTEGER  - Units currently in stock
  price     REAL     - Unit price in USD (e.g. 799.00)

Table: orders
Columns:
  id              INTEGER - Primary key (auto-increment)
  customer_name   TEXT    - Name of the customer
  contact_number  TEXT    - Phone number of the customer
  address         TEXT    - Delivery address
  product_id      INTEGER - Foreign key referencing products.id
  quantity        INTEGER - Number of units ordered
  total_amount    REAL    - Total cost (quantity * price)
  order_date      TEXT    - ISO timestamp of the order (e.g., '2026-06-15T17:12:31.391573')

Notes:
  - All SQL must target only the 'products' or 'orders' tables
  - Only SELECT statements are permitted
  - Do not generate INSERT, UPDATE, DELETE statements
  - Use SQLite date functions (e.g., `date(order_date) = date('now')`) for date comparisons.
""".strip()
