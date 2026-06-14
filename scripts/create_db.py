"""
scripts/create_db.py

Creates the SQLite inventory database at data/inventory.db and seeds it
with sample retail inventory data. Run this once before starting the app.

Usage (from repo root):
    python scripts/create_db.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "inventory.db")


def create_and_seed():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            colour      TEXT    NOT NULL,
            size        TEXT    NOT NULL,
            stock       INTEGER NOT NULL DEFAULT 0,
            price       REAL    NOT NULL,
            discount    REAL    NOT NULL DEFAULT 0.0
        )
    """)

    # Clear existing rows so the script is idempotent
    cur.execute("DELETE FROM products")

    rows = [
        # name,                category,   colour,   size,  stock, price,  discount
        ("Levi's 501 Jeans",    "Jeans",    "Blue",   "M",   45,    49.99,  10.0),
        ("Levi's 501 Jeans",    "Jeans",    "Black",  "L",   30,    49.99,  10.0),
        ("Nike Air T-Shirt",    "T-Shirt",  "White",  "S",   120,   24.99,  0.0),
        ("Nike Air T-Shirt",    "T-Shirt",  "White",  "M",   85,    24.99,  0.0),
        ("Nike Air T-Shirt",    "T-Shirt",  "Black",  "XL",  60,    24.99,  5.0),
        ("Adidas Hoodie",       "Hoodie",   "Grey",   "M",   40,    59.99,  15.0),
        ("Adidas Hoodie",       "Hoodie",   "Navy",   "L",   25,    59.99,  15.0),
        ("Puma Track Pants",    "Pants",    "Black",  "M",   70,    34.99,  0.0),
        ("Puma Track Pants",    "Pants",    "Grey",   "S",   55,    34.99,  0.0),
        ("Reebok Polo Shirt",   "T-Shirt",  "Red",    "L",   35,    29.99,  20.0),
        ("Under Armour Top",    "T-Shirt",  "Blue",   "M",   90,    27.99,  0.0),
        ("H&M Chinos",          "Pants",    "Beige",  "M",   80,    39.99,  25.0),
        ("H&M Chinos",          "Pants",    "Olive",  "L",   45,    39.99,  25.0),
        ("Zara Blazer",         "Jacket",   "Navy",   "M",   20,    89.99,  0.0),
        ("Zara Blazer",         "Jacket",   "Black",  "S",   15,    89.99,  0.0),
        ("Gap Sweatshirt",      "Hoodie",   "White",  "XL",  50,    44.99,  10.0),
        ("Tommy Hilfiger Polo", "T-Shirt",  "White",  "M",   65,    39.99,  0.0),
        ("Calvin Klein Jeans",  "Jeans",    "Blue",   "S",   38,    54.99,  5.0),
        ("Calvin Klein Jeans",  "Jeans",    "Grey",   "L",   22,    54.99,  5.0),
        ("New Balance Jacket",  "Jacket",   "Black",  "M",   18,    74.99,  30.0),
    ]

    cur.executemany(
        "INSERT INTO products (name, category, colour, size, stock, price, discount) VALUES (?,?,?,?,?,?,?)",
        rows
    )

    conn.commit()
    conn.close()
    print(f"[OK] Database created at {os.path.abspath(DB_PATH)} with {len(rows)} rows.")


if __name__ == "__main__":
    create_and_seed()
