"""
NHS Data Pipeline - Reusable Orchestration Tasks
==================================================
Individual pipeline tasks that can be composed into flows.
"""

import subprocess
import sys
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger

PROJECT_ROOT = Path(__file__).parent.parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "nhs_dbt"


@task(
    name="generate-synthetic-data",
    description="Generate synthetic NHS data (patients, episodes, diagnoses, etc.)",
    retries=2,
    retry_delay_seconds=30,
    tags=["ingestion", "data-generation"],
)
def generate_synthetic_data():
    """Generate synthetic NHS data."""
    logger = get_run_logger()
    logger.info("👤 Generating synthetic NHS data...")

    result = subprocess.run(
        [sys.executable, "src/ingestion/generate_synthetic_data.py"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(f"Data generation failed:\n{result.stderr}")
        raise Exception(f"Data generation failed: {result.stderr}")

    logger.info(f"✅ Data generation complete\n{result.stdout[-500:]}")
    return "synthetic_data_generated"


@task(
    name="load-to-duckdb",
    description="Load raw CSV files into DuckDB database",
    retries=2,
    retry_delay_seconds=30,
    tags=["ingestion", "duckdb"],
)
def load_to_duckdb():
    """Load raw data into DuckDB."""
    logger = get_run_logger()
    logger.info("📂 Loading data into DuckDB...")

    result = subprocess.run(
        [sys.executable, "src/ingestion/load_to_duckdb.py"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(f"DuckDB loading failed:\n{result.stderr}")
        raise Exception(f"DuckDB loading failed: {result.stderr}")

    logger.info(f"✅ DuckDB loading complete\n{result.stdout[-500:]}")
    return "data_loaded_to_duckdb"


@task(
    name="dbt-deps",
    description="Install dbt package dependencies",
    retries=2,
    retry_delay_seconds=15,
    tags=["dbt", "setup"],
)
def dbt_deps():
    """Install dbt dependencies."""
    logger = get_run_logger()
    logger.info("📦 Installing dbt dependencies...")

    result = subprocess.run(
        ["dbt", "deps"],
        cwd=str(DBT_PROJECT_DIR),
        capture_output=True,
        text=True,
        env={
            **dict(__import__("os").environ),
            "DBT_PROFILES_DIR": str(DBT_PROJECT_DIR),
        },
    )

    if result.returncode != 0:
        logger.error(f"dbt deps failed:\n{result.stderr}")
        raise Exception(f"dbt deps failed: {result.stderr}")

    logger.info("✅ dbt dependencies installed")
    return "dbt_deps_installed"


@task(
    name="dbt-seed",
    description="Load dbt seed files (reference data)",
    retries=2,
    retry_delay_seconds=15,
    tags=["dbt", "seed"],
)
def dbt_seed():
    """Run dbt seed to load reference data."""
    logger = get_run_logger()
    logger.info("🌱 Running dbt seed...")

    result = subprocess.run(
        ["dbt", "seed"],
        cwd=str(DBT_PROJECT_DIR),
        capture_output=True,
        text=True,
        env={
            **dict(__import__("os").environ),
            "DBT_PROFILES_DIR": str(DBT_PROJECT_DIR),
        },
    )

    if result.returncode != 0:
        logger.error(f"dbt seed failed:\n{result.stderr}")
        raise Exception(f"dbt seed failed: {result.stderr}")

    logger.info(f"✅ dbt seed complete\n{result.stdout[-500:]}")
    return "dbt_seed_complete"


@task(
    name="dbt-run",
    description="Run dbt models (staging, intermediate, marts)",
    retries=2,
    retry_delay_seconds=30,
    tags=["dbt", "transform"],
)
def dbt_run(select: str = None):
    """Run dbt models."""
    logger = get_run_logger()

    cmd = ["dbt", "run"]
    if select:
        cmd.extend(["--select", select])
        logger.info(f"🔄 Running dbt models: {select}")
    else:
        logger.info("🔄 Running all dbt models...")

    result = subprocess.run(
        cmd,
        cwd=str(DBT_PROJECT_DIR),
        capture_output=True,
        text=True,
        env={
            **dict(__import__("os").environ),
            "DBT_PROFILES_DIR": str(DBT_PROJECT_DIR),
        },
    )

    if result.returncode != 0:
        logger.error(f"dbt run failed:\n{result.stderr}")
        raise Exception(f"dbt run failed: {result.stderr}")

    logger.info(f"✅ dbt run complete\n{result.stdout[-500:]}")
    return "dbt_run_complete"


@task(
    name="dbt-test",
    description="Run dbt data quality tests",
    retries=1,
    tags=["dbt", "testing", "data-quality"],
)
def dbt_test(select: str = None):
    """Run dbt tests."""
    logger = get_run_logger()

    cmd = ["dbt", "test"]
    if select:
        cmd.extend(["--select", select])
        logger.info(f"🧪 Running dbt tests: {select}")
    else:
        logger.info("🧪 Running all dbt tests...")

    result = subprocess.run(
        cmd,
        cwd=str(DBT_PROJECT_DIR),
        capture_output=True,
        text=True,
        env={
            **dict(__import__("os").environ),
            "DBT_PROFILES_DIR": str(DBT_PROJECT_DIR),
        },
    )

    if result.returncode != 0:
        logger.error(f"dbt test failures:\n{result.stdout[-1000:]}")
        raise Exception(f"dbt tests failed: {result.stdout[-1000:]}")

    logger.info(f"✅ dbt tests passed\n{result.stdout[-500:]}")
    return "dbt_tests_passed"


@task(
    name="run-nlp-pipeline",
    description="Run clinical NLP pipeline on unstructured notes",
    retries=1,
    retry_delay_seconds=60,
    tags=["nlp", "language-ai"],
)
def run_nlp_pipeline():
    """Run the clinical NLP pipeline."""
    logger = get_run_logger()
    logger.info("🧠 Running clinical NLP pipeline...")

    result = subprocess.run(
        [sys.executable, "src/nlp/run_pipeline.py"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(f"NLP pipeline failed:\n{result.stderr}")
        raise Exception(f"NLP pipeline failed: {result.stderr}")

    logger.info(f"✅ NLP pipeline complete\n{result.stdout[-500:]}")
    return "nlp_pipeline_complete"


@task(
    name="dbt-run-nlp-marts",
    description="Run dbt NLP mart models after NLP extraction",
    retries=2,
    retry_delay_seconds=15,
    tags=["dbt", "nlp"],
)
def dbt_run_nlp_marts():
    """Run dbt models for NLP marts only."""
    logger = get_run_logger()
    logger.info("📊 Running dbt NLP mart models...")

    result = subprocess.run(
        ["dbt", "run", "--select", "tag:nlp"],
        cwd=str(DBT_PROJECT_DIR),
        capture_output=True,
        text=True,
        env={
            **dict(__import__("os").environ),
            "DBT_PROFILES_DIR": str(DBT_PROJECT_DIR),
        },
    )

    if result.returncode != 0:
        logger.error(f"dbt NLP marts failed:\n{result.stderr}")
        raise Exception(f"dbt NLP marts failed: {result.stderr}")

    logger.info(f"✅ dbt NLP marts complete\n{result.stdout[-500:]}")
    return "nlp_marts_complete"