"""
app/sql/schema.py

Defines the inventory database schema as a plain string that is injected into
SQL generation prompts. Keep this in sync with scripts/create_db.py.
"""

INVENTORY_SCHEMA = """
Table: products
Columns:
  id        INTEGER  - Primary key (auto-increment)
  name      TEXT     - Product name (e.g. 'Nike Air T-Shirt', 'Levi\\'s 501 Jeans')
  category  TEXT     - Product category (T-Shirt, Jeans, Hoodie, Pants, Jacket)
  colour    TEXT     - Product colour (e.g. White, Black, Blue, Grey, Red, Navy, Beige, Olive)
  size      TEXT     - Size code (S, M, L, XL)
  stock     INTEGER  - Units currently in stock
  price     REAL     - Unit price in USD (e.g. 24.99)
  discount  REAL     - Discount percentage (0 = no discount, 20 = 20% off)

Notes:
  - All SQL must target only the 'products' table
  - Only SELECT statements are permitted
  - discount is stored as a percentage (e.g. 20 means 20%, not 0.20)
""".strip()
