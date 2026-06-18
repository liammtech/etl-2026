"""Database connection helpers for production and development environments.

Connection settings are loaded from a project-level `.env` file located in
the repository root directory.
"""

import os
from pathlib import Path

import pyodbc
from dotenv import load_dotenv


load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def _need(name: str) -> str:
    """Retrieve a required environment variable.

    Args:
        name: The name of the environment variable.

    Returns:
        The environment variable value.

    Raises:
        RuntimeError: If the environment variable is missing or empty.
    """
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")

    return value


def get_prod_cursor() -> pyodbc.Cursor:
    """Create a cursor for the production SQL Server database.

    Required environment variables:

    - DRIVER
    - SERVER
    - DATABASE

    Optional environment variables:

    - TRUSTED_CONNECTION (defaults to "yes")
    - ENCRYPT (defaults to "yes")
    - TRUST_SERVER_CERTIFICATE (defaults to "no")

    Returns:
        A cursor connected to the production database.

    Raises:
        RuntimeError: If a required environment variable is missing.
        pyodbc.Error: If the database connection cannot be established.
    """
    conn = pyodbc.connect(
        f"DRIVER={_need('DRIVER')};"
        f"SERVER={_need('SERVER')};"
        f"DATABASE={_need('DATABASE')};"
        f"Trusted_Connection={os.getenv('TRUSTED_CONNECTION', 'yes')};"
        f"Encrypt={os.getenv('ENCRYPT', 'yes')};"
        f"TrustServerCertificate={os.getenv('TRUST_SERVER_CERTIFICATE', 'no')};"
    )

    return conn.cursor()


def get_dev_cursor() -> pyodbc.Cursor:
    """Create a cursor for the development database.

    The development environment uses a file-based ODBC connection.

    Required environment variables:

    - DRIVER_DEV
    - DBQ_DEV

    Returns:
        A cursor connected to the development database.

    Raises:
        RuntimeError: If a required environment variable is missing.
        pyodbc.Error: If the database connection cannot be established.
    """
    conn = pyodbc.connect(
        f"DRIVER={_need('DRIVER_DEV')};"
        f"DBQ={_need('DBQ_DEV')};"
    )

    return conn.cursor()


def get_cursor() -> pyodbc.Cursor:
    """Create a cursor for the configured database environment.

    The target environment is selected using the ``SQL_MODE`` environment
    variable.

    Supported values are:

    - "Prod" for the production SQL Server database.
    - "Dev" for the development database.

    Returns:
        A cursor connected to the configured database.

    Raises:
        RuntimeError: If ``SQL_MODE`` or another required environment
            variable is missing.
        ValueError: If ``SQL_MODE`` is not set to a supported value.
        pyodbc.Error: If the database connection cannot be established.
    """
    sql_mode = _need("SQL_MODE")

    if sql_mode == "Prod":
        return get_prod_cursor()

    if sql_mode == "Dev":
        return get_dev_cursor()

    raise ValueError(
        f"Invalid SQL_MODE: {sql_mode!r}. "
        "Expected one of: 'Prod', 'Dev'."
    )
```
