"""
NHS Data Pipeline - Configuration Management
Loads environment variables and provides project-wide settings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SEEDS_DIR = DATA_DIR / "seeds"
DUCKDB_DIR = DATA_DIR / "duckdb"
DBT_PROJECT_DIR = PROJECT_ROOT / "nhs_dbt"


class SnowflakeConfig:
    """Snowflake connection configuration."""

    ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "")
    USER = os.getenv("SNOWFLAKE_USER", "")
    PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "")
    WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "NHS_PIPELINE_WH")
    DATABASE = os.getenv("SNOWFLAKE_DATABASE", "NHS_DATA_PLATFORM")
    ROLE = os.getenv("SNOWFLAKE_ROLE", "DBT_ROLE")


class DuckDBConfig:
    """DuckDB connection configuration."""

    PATH = os.getenv("DUCKDB_PATH", str(DUCKDB_DIR / "nhs_pipeline.duckdb"))


class APIConfig:
    """API configuration."""

    HOST = os.getenv("API_HOST", "0.0.0.0")
    PORT = int(os.getenv("API_PORT", "8000"))