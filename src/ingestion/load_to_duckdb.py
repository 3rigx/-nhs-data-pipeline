"""
NHS Data Pipeline - DuckDB Data Loader
=======================================
Loads raw CSV files into DuckDB database tables.
Creates the RAW schema and ingests all synthetic NHS data.
"""

import sys
import io
import duckdb
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DUCKDB_PATH = PROJECT_ROOT / "data" / "duckdb" / "nhs_pipeline.duckdb"

# Files to load and their target table names
RAW_FILES = {
    "patients.csv": "raw_patients",
    "episodes.csv": "raw_episodes",
    "diagnoses.csv": "raw_diagnoses",
    "procedures.csv": "raw_procedures",
    "medications.csv": "raw_medications",
    "observations.csv": "raw_observations",
    "clinical_notes.csv": "raw_clinical_notes",
}


def load_csv_to_duckdb():
    """Load all raw CSV files into DuckDB."""
    print("=" * 60)
    print("NHS Data Pipeline - DuckDB Loader")
    print("=" * 60)
    print()

    # Ensure DuckDB directory exists
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to DuckDB
    conn = duckdb.connect(str(DUCKDB_PATH))

    # Create raw schema
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
    print("[OK] Created schema: raw")

    # Load each CSV file
    for csv_file, table_name in RAW_FILES.items():
        csv_path = RAW_DATA_DIR / csv_file

        if not csv_path.exists():
            print(f"[WARN] File not found: {csv_file} -- skipping")
            continue

        # Drop table if exists and recreate from CSV
        conn.execute(f"DROP TABLE IF EXISTS raw.{table_name}")
        conn.execute(f"""
            CREATE TABLE raw.{table_name} AS
            SELECT * FROM read_csv_auto('{csv_path}', header=true)
        """)

        # Get row count
        result = conn.execute(f"SELECT COUNT(*) FROM raw.{table_name}").fetchone()
        print(f"[OK] Loaded {table_name}: {result[0]:,} rows")

    # Verify all tables
    print()
    print("-" * 60)
    print("VERIFICATION")
    print("-" * 60)

    tables = conn.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema = 'raw'
        ORDER BY table_name
    """).fetchall()

    print(f"\nTables in 'raw' schema: {len(tables)}")
    for schema, table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {schema}.{table}").fetchone()
        columns = conn.execute(f"""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{table}'
        """).fetchone()
        print(f"  {schema}.{table}: {count[0]:,} rows, {columns[0]} columns")

    # Sample data check
    print()
    print("-" * 60)
    print("SAMPLE DATA")
    print("-" * 60)

    print("\nSample Patient:")
    sample = conn.execute("SELECT * FROM raw.raw_patients LIMIT 1").fetchdf()
    for col in sample.columns:
        print(f"  {col}: {sample[col].values[0]}")

    print("\nSample Clinical Note (first 200 chars):")
    note = conn.execute("""
        SELECT note_text FROM raw.raw_clinical_notes LIMIT 1
    """).fetchone()
    print(f"  {note[0][:200]}...")

    conn.close()
    print()
    print("=" * 60)
    print("LOADING COMPLETE")
    print(f"Database: {DUCKDB_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    load_csv_to_duckdb()