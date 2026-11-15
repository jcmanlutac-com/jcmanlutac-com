"""
This helper tool provides a reusable PostgreSQL database connector for Python applications.
Provides functions to connect to and interact with a PostgreSQL database using the psycopg library.

Usage:
    python pytools/postgresql_db_connector.py
    This will test the database connection and display environment information.
"""

import os
import sys
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine, make_url

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_database_url(database_url: str | None = None) -> str:
    """Return an explicit or environment-configured PostgreSQL URL."""
    if database_url:
        return database_url

    load_dotenv(PROJECT_ROOT / ".env")
    """Alternatively, NEON_DB_URL can be used as the database URL if set. The environment variable is used to configure the database connection."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL or NEON_DB_URL not found in the environment or project .env file."
        )
    return database_url


def _get_postgresql_url(database_url: str, drivername: str) -> URL:
    url = make_url(database_url)
    if url.drivername not in {
        "postgres",
        "postgresql",
        "postgresql+psycopg",
        "postgresql+psycopg2",
    }:
        raise ValueError("DATABASE_URL must use a PostgreSQL URL scheme.")
    return url.set(drivername=drivername)


def get_connection(
    database_url: str | None = None, **connect_options: Any
) -> psycopg.Connection[Any]:
    """Open a psycopg connection for scraper and SQL scripts."""
    url = _get_postgresql_url(get_database_url(database_url), "postgresql")
    dsn = url.render_as_string(hide_password=False)
    return psycopg.connect(dsn, **connect_options)


def create_sqlalchemy_engine(
    database_url: str | None = None, **engine_options: Any
) -> Engine:
    """Create a SQLAlchemy engine backed by psycopg 3."""
    url = _get_postgresql_url(get_database_url(database_url), "postgresql+psycopg")
    return create_engine(url, **engine_options)


def main() -> int:
    """Test database connection and display environment."""
    try:
        database_url = get_database_url()
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        with get_connection(database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print("\n✓ Connection successful!")
                if version:
                    print(f"PostgreSQL Version: {version[0]}")
                else:
                    print("PostgreSQL Version: Unable to retrieve")

                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                    """
                )
                tables = cursor.fetchall()
                print("\nExisting tables in 'public' schema:")
                if tables:
                    for table in tables:
                        print(f"  - {table[0]}")
                else:
                    print("  (none)")

    except psycopg.Error as exc:
        print(f"✗ Database operation failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
