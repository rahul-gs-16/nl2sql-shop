"""
tests/test_repository.py

Unit tests for app.database.repository — read-only enforcement.
"""

import os
import sqlite3
import tempfile
import pytest

# Point the settings at a temporary test DB before importing repository
_TMP_DIR = tempfile.mkdtemp()
_TEST_DB = os.path.join(_TMP_DIR, "test_inventory.db")

os.environ["SQLITE_DB_PATH"] = _TEST_DB
os.environ["MODEL_PROVIDER"] = "gemini"   # Avoid Ollama check
os.environ["GOOGLE_API_KEY"] = "test-key"


def _create_test_db():
    conn = sqlite3.connect(_TEST_DB)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            colour TEXT,
            size TEXT,
            stock INTEGER,
            price REAL,
            discount REAL
        )"""
    )
    conn.execute(
        "INSERT INTO products VALUES (1, 'Test Shirt', 'T-Shirt', 'Blue', 'M', 10, 19.99, 0)"
    )
    conn.commit()
    conn.close()


_create_test_db()

# Import after env vars are set
from app.database.repository import execute_query, _assert_read_only  # noqa: E402


class TestReadOnlyEnforcement:
    """_assert_read_only rejects destructive SQL keywords."""

    @pytest.mark.parametrize("sql", [
        "DELETE FROM products WHERE id = 1",
        "UPDATE products SET stock = 0",
        "INSERT INTO products VALUES (2, 'X', 'Y', 'Z', 'S', 5, 9.99, 0)",
        "DROP TABLE products",
        "ALTER TABLE products ADD COLUMN foo TEXT",
        "TRUNCATE products",
    ])
    def test_destructive_sql_raises(self, sql):
        with pytest.raises(ValueError, match="not permitted"):
            _assert_read_only(sql)

    def test_select_passes(self):
        """SELECT statement must not raise."""
        _assert_read_only("SELECT * FROM products")  # should not raise

    def test_empty_sql_raises(self):
        with pytest.raises(ValueError):
            _assert_read_only("   ")


class TestExecuteQuery:
    """execute_query runs SELECT and returns rows."""

    def test_returns_rows(self):
        rows = execute_query("SELECT name FROM products")
        assert len(rows) == 1
        assert rows[0][0] == "Test Shirt"

    def test_execute_destructive_raises(self):
        with pytest.raises(ValueError):
            execute_query("DELETE FROM products")
