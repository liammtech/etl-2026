"""Database connection helpers for production and development environments.

Connection settings are loaded from a project-level `.env` file located in
the repository root directory.
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pyodbc
from dotenv import load_dotenv


load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def _need(name: str) -> str:
    """Retrieve a required environment variable."""
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")

    return value


def get_prod_connection() -> pyodbc.Connection:
    """Create a connection to the production SQL Server database."""
    return pyodbc.connect(
        f"DRIVER={_need('DRIVER')};"
        f"SERVER={_need('SERVER')};"
        f"DATABASE={_need('DATABASE')};"
        f"Trusted_Connection={os.getenv('TRUSTED_CONNECTION', 'yes')};"
        f"Encrypt={os.getenv('ENCRYPT', 'yes')};"
        f"TrustServerCertificate={os.getenv('TRUST_SERVER_CERTIFICATE', 'no')};"
    )


def get_dev_connection() -> pyodbc.Connection:
    """Create a connection to the development database."""
    return pyodbc.connect(
        f"DRIVER={_need('DRIVER_DEV')};"
        f"DBQ={_need('DBQ_DEV')};"
    )


def get_connection() -> pyodbc.Connection:
    """Create a connection for the configured database environment."""
    sql_mode = _need("SQL_MODE")

    if sql_mode == "Prod":
        return get_prod_connection()

    if sql_mode == "Dev":
        return get_dev_connection()

    raise ValueError(
        f"Invalid SQL_MODE: {sql_mode!r}. "
        "Expected one of: 'Prod', 'Dev'."
    )


@contextmanager
def get_cursor() -> Iterator[pyodbc.Cursor]:
    """Create a managed cursor for the configured database environment.

    The database connection is automatically committed if the wrapped block
    completes successfully, rolled back if an exception is raised, and closed
    afterwards in all cases.
    """
    conn = get_connection()

    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_prod_cursor() -> pyodbc.Cursor:
    """Create a cursor for the production SQL Server database.

    Prefer using ``get_cursor()`` for managed connection handling.
    """
    return get_prod_connection().cursor()


def get_dev_cursor() -> pyodbc.Cursor:
    """Create a cursor for the development database.

    Prefer using ``get_cursor()`` for managed connection handling.
    """
    return get_dev_connection().cursor()