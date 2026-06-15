"""
scripts/create_db.py

Creates the SQLite inventory database at data/inventory.db and seeds it
with sample mobile inventory data. Run this once before starting the app.

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

    # Drop existing tables if they exist to ensure a clean slate
    cur.execute("DROP TABLE IF EXISTS orders")
    cur.execute("DROP TABLE IF EXISTS products")

    cur.execute("""
        CREATE TABLE products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            model       TEXT    NOT NULL,
            variant     TEXT    NOT NULL,
            color       TEXT    NOT NULL,
            storage     TEXT    NOT NULL,
            stock       INTEGER NOT NULL DEFAULT 0,
            price       REAL    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE orders (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name   TEXT    NOT NULL,
            contact_number  TEXT    NOT NULL,
            address         TEXT    NOT NULL,
            product_id      INTEGER NOT NULL,
            quantity        INTEGER NOT NULL,
            total_amount    REAL    NOT NULL,
            order_date      TEXT    NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

    # Standard models: 128GB, 256GB, 512GB
    # Pro/Pro Max models: 256GB, 512GB, 1TB
    # Colors: Black, White, Blue, Pink
    rows = [
        # model, variant, color, storage, stock, price
        ("iPhone 15", "Standard", "Black", "128GB", 50, 799.00),
        ("iPhone 15", "Standard", "White", "128GB", 40, 799.00),
        ("iPhone 15", "Standard", "Blue", "256GB", 30, 899.00),
        ("iPhone 15", "Standard", "Pink", "512GB", 20, 1099.00),
        
        ("iPhone 15", "Pro", "Black", "256GB", 45, 1099.00),
        ("iPhone 15", "Pro", "White", "512GB", 35, 1299.00),
        ("iPhone 15", "Pro", "Blue", "1TB", 15, 1499.00),

        ("iPhone 15", "Pro Max", "Black", "256GB", 55, 1199.00),
        ("iPhone 15", "Pro Max", "White", "512GB", 25, 1399.00),
        ("iPhone 15", "Pro Max", "Blue", "1TB", 10, 1599.00),

        ("iPhone 16", "Standard", "Black", "128GB", 100, 799.00),
        ("iPhone 16", "Standard", "White", "256GB", 80, 899.00),
        ("iPhone 16", "Standard", "Blue", "512GB", 60, 1099.00),
        ("iPhone 16", "Standard", "Pink", "128GB", 90, 799.00),

        ("iPhone 16", "Pro", "Black", "256GB", 70, 1099.00),
        ("iPhone 16", "Pro", "White", "512GB", 50, 1299.00),
        ("iPhone 16", "Pro", "Blue", "1TB", 30, 1499.00),

        ("iPhone 16", "Pro Max", "Black", "256GB", 80, 1199.00),
        ("iPhone 16", "Pro Max", "White", "512GB", 40, 1399.00),
        ("iPhone 16", "Pro Max", "Pink", "1TB", 20, 1599.00),

        ("iPhone 17", "Standard", "Black", "128GB", 150, 849.00),
        ("iPhone 17", "Standard", "White", "256GB", 120, 949.00),
        ("iPhone 17", "Standard", "Blue", "512GB", 90, 1149.00),
        ("iPhone 17", "Standard", "Pink", "256GB", 110, 949.00),

        ("iPhone 17", "Pro", "Black", "256GB", 100, 1149.00),
        ("iPhone 17", "Pro", "White", "512GB", 80, 1349.00),
        ("iPhone 17", "Pro", "Pink", "1TB", 50, 1549.00),

        ("iPhone 17", "Pro Max", "Black", "256GB", 120, 1249.00),
        ("iPhone 17", "Pro Max", "White", "512GB", 90, 1449.00),
        ("iPhone 17", "Pro Max", "Blue", "1TB", 60, 1649.00),
    ]

    cur.executemany(
        "INSERT INTO products (model, variant, color, storage, stock, price) VALUES (?,?,?,?,?,?)",
        rows
    )

    conn.commit()
    conn.close()
    print(f"[OK] Database created at {os.path.abspath(DB_PATH)} with {len(rows)} products.")


if __name__ == "__main__":
    create_and_seed()
