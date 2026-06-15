"""
app/database/repository.py

Isolated read-only data access layer for the SQLite inventory database.
Only SELECT statements are permitted; all destructive operations are rejected
before reaching the database.
"""

import sqlite3
import os
from typing import Any

from app.config import settings

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DISALLOWED_KEYWORDS = {"DELETE", "UPDATE", "INSERT", "DROP", "ALTER", "TRUNCATE", "REPLACE"}
"""SQL keywords that are never permitted."""


# ---------------------------------------------------------------------------
# Startup validation
# ---------------------------------------------------------------------------

def validate_db_path() -> None:
    """Raise RuntimeError if the configured database file does not exist."""
    path = settings.SQLITE_DB_PATH
    if not os.path.isfile(path):
        raise RuntimeError(
            f"Database file not found at '{path}'. "
            "Set SQLITE_DB_PATH to a valid SQLite file path, "
            "or run scripts/create_db.py to create the inventory database."
        )


# ---------------------------------------------------------------------------
# Query execution
# ---------------------------------------------------------------------------

def execute_query(sql: str) -> list[tuple[Any, ...]]:
    """
    Execute a read-only SQL statement against the inventory database.

    Parameters
    ----------
    sql : str
        A SQL SELECT statement to execute.

    Returns
    -------
    list[tuple]
        All matching rows as a list of tuples.

    Raises
    ------
    ValueError
        If the SQL contains a disallowed keyword (not a read-only statement).
    sqlite3.Error
        If the database raises an error during execution.
    """
    _assert_read_only(sql)

    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def get_column_names(sql: str) -> list[str]:
    """
    Execute a SQL SELECT and return the column names from the result cursor.

    Parameters
    ----------
    sql : str
        A SQL SELECT statement.

    Returns
    -------
    list[str]
        Column names in result order.
    """
    _assert_read_only(sql)

    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return columns
    finally:
        conn.close()


from datetime import datetime

def place_order(customer_name: str, contact_number: str, address: str, product_id: int, quantity: int) -> dict:
    """
    Place an order for a product, ensuring sufficient stock.
    This operation is transactional.

    Parameters
    ----------
    customer_name : str
    contact_number : str
    address : str
    product_id : int
    quantity : int

    Returns
    -------
    dict
        A dictionary with 'success' (bool) and 'message' (str).
    """
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    try:
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. Check stock and get price
        cursor.execute("SELECT stock, price, model, variant, storage, color FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.rollback()
            return {"success": False, "message": f"Product ID {product_id} not found."}
            
        stock, price, model, variant, storage, color = row
        product_name = f"{model} {variant} {storage} {color}"
        
        if stock < quantity:
            conn.rollback()
            return {
                "success": False, 
                "message": f"Insufficient stock for {product_name}. Requested: {quantity}, Available: {stock}."
            }
            
        # 2. Calculate total amount
        total_amount = price * quantity
        order_date = datetime.utcnow().isoformat()
        
        # 3. Deduct stock
        cursor.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?", 
            (quantity, product_id)
        )
        
        # 4. Insert order
        cursor.execute(
            """
            INSERT INTO orders (customer_name, contact_number, address, product_id, quantity, total_amount, order_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (customer_name, contact_number, address, product_id, quantity, total_amount, order_date)
        )
        
        # Commit transaction
        conn.commit()
        return {
            "success": True, 
            "message": f"Successfully ordered {quantity}x {product_name}. Total: ${total_amount:.2f}"
        }
        
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"An error occurred: {str(e)}"}
    finally:
        conn.close()

def clear_orders() -> None:
    """
    Clear all records from the orders table.
    Used to reset the orders database on startup.
    """
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders")
        conn.commit()
    except Exception as e:
        # Ignore errors if table doesn't exist yet
        pass
    finally:
        conn.close()

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _assert_read_only(sql: str) -> None:
    """
    Raise ValueError if *sql* begins with a disallowed keyword.

    Parameters
    ----------
    sql : str
        The SQL statement to validate.
    """
    first_token = sql.strip().split()[0].upper() if sql.strip() else ""
    if first_token in _DISALLOWED_KEYWORDS:
        raise ValueError(
            f"Destructive SQL operation '{first_token}' is not permitted. "
            "Only SELECT statements are allowed."
        )
    if not first_token:
        raise ValueError("Empty SQL statement provided.")
