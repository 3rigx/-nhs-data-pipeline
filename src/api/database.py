"""
NHS Data Pipeline - API Database Connection
=============================================
Manages DuckDB connection for the FastAPI application.
"""

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).parent.parent.parent
DUCKDB_PATH = PROJECT_ROOT / "data" / "duckdb" / "nhs_pipeline.duckdb"


def get_db_connection():
    """Get a DuckDB connection."""
    return duckdb.connect(str(DUCKDB_PATH), read_only=True)


def query_to_dict(conn, sql: str, params: list = None) -> list[dict]:
    """Execute query and return list of dicts."""
    try:
        if params:
            result = conn.execute(sql, params)
        else:
            result = conn.execute(sql)

        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"Query error: {e}")
        return []


def query_single(conn, sql: str, params: list = None) -> dict:
    """Execute query and return single dict."""
    results = query_to_dict(conn, sql, params)
    return results[0] if results else {}