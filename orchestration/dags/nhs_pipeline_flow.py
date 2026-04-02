"""
NHS Data Pipeline - Prefect Orchestration Flow
================================================
Complete end-to-end pipeline orchestration using Prefect.

This flow orchestrates:
1. Synthetic data generation
2. Data loading into DuckDB
3. dbt transformations (staging → intermediate → marts → OMOP)
4. Clinical NLP pipeline
5. NLP mart model generation
6. Data quality testing

Usage:
    # Run full pipeline
    poetry run python orchestration/dags/nhs_pipeline_flow.py

    # Or deploy as scheduled flow
    poetry run python orchestration/dags/nhs_pipeline_flow.py --deploy
"""

import sys
from datetime import timedelta
from pathlib import Path

from prefect import flow
from prefect.logging import get_run_logger

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.tasks.data_tasks import (
    dbt_deps,
    dbt_run,
    dbt_run_nlp_marts,
    dbt_seed,
    dbt_test,
    generate_synthetic_data,
    load_to_duckdb,
    run_nlp_pipeline,
)


@flow(
    name="NHS Full Data Pipeline",
    description="""
    End-to-end NHS data pipeline:
    - Generates synthetic NHS patient data
    - Loads into DuckDB warehouse
    - Runs dbt transformations (staging → intermediate → OMOP CDM)
    - Executes clinical NLP on unstructured notes
    - Runs data quality tests
    
    Designed for NHS London health data infrastructure.
    """,
    version="1.0.0",
    retries=0,
    timeout_seconds=3600,
)
def nhs_full_pipeline(
    generate_data: bool = True,
    run_nlp: bool = True,
):
    """
    Full NHS data pipeline flow.

    Args:
        generate_data: Whether to regenerate synthetic data
        run_nlp: Whether to run the NLP pipeline
    """
    logger = get_run_logger()
    logger.info("🏥 Starting NHS Full Data Pipeline")
    logger.info(f"   Generate data: {generate_data}")
    logger.info(f"   Run NLP: {run_nlp}")

    # ---- Phase 1: Data Ingestion ----
    logger.info("\n📥 PHASE 1: Data Ingestion")

    if generate_data:
        data_result = generate_synthetic_data()
        load_result = load_to_duckdb(wait_for=[data_result])
    else:
        load_result = load_to_duckdb()

    # ---- Phase 2: dbt Setup ----
    logger.info("\n⚙️ PHASE 2: dbt Setup")

    deps_result = dbt_deps(wait_for=[load_result])
    seed_result = dbt_seed(wait_for=[deps_result])

    # ---- Phase 3: dbt Transformations ----
    logger.info("\n🔄 PHASE 3: dbt Transformations")

    # Run staging models first
    staging_result = dbt_run(
        select="staging",
        wait_for=[seed_result],
    )

    # Then intermediate models
    intermediate_result = dbt_run(
        select="intermediate",
        wait_for=[staging_result],
    )

    # Then OMOP mart models
    omop_result = dbt_run(
        select="tag:omop",
        wait_for=[intermediate_result],
    )

    # Then cohort models
    cohort_result = dbt_run(
        select="tag:cohorts",
        wait_for=[omop_result],
    )

    # ---- Phase 4: Data Quality ----
    logger.info("\n🧪 PHASE 4: Data Quality Tests (Pre-NLP)")

    test_result = dbt_test(
        select="staging intermediate",
        wait_for=[intermediate_result],
    )

    # ---- Phase 5: NLP Pipeline ----
    if run_nlp:
        logger.info("\n🧠 PHASE 5: Clinical NLP Pipeline")

        nlp_result = run_nlp_pipeline(wait_for=[test_result])
        nlp_marts_result = dbt_run_nlp_marts(wait_for=[nlp_result])

    # ---- Phase 6: Final Tests ----
    logger.info("\n🧪 PHASE 6: Final Data Quality Tests")

    final_test_result = dbt_test(wait_for=[cohort_result])

    logger.info("\n✅ NHS Full Data Pipeline COMPLETE")
    return "pipeline_complete"


@flow(
    name="NHS dbt Refresh",
    description="Quick dbt refresh — runs models and tests without data regeneration",
    version="1.0.0",
)
def nhs_dbt_refresh():
    """Quick dbt-only refresh flow."""
    logger = get_run_logger()
    logger.info("🔄 Starting dbt refresh...")

    deps = dbt_deps()
    seed = dbt_seed(wait_for=[deps])
    run = dbt_run(wait_for=[seed])
    test = dbt_test(wait_for=[run])

    logger.info("✅ dbt refresh complete")
    return "dbt_refresh_complete"


@flow(
    name="NHS NLP Only",
    description="Run NLP pipeline only — assumes data is already loaded",
    version="1.0.0",
)
def nhs_nlp_only():
    """NLP-only flow."""
    logger = get_run_logger()
    logger.info("🧠 Starting NLP-only pipeline...")

    nlp = run_nlp_pipeline()
    marts = dbt_run_nlp_marts(wait_for=[nlp])
    test = dbt_test(select="tag:nlp", wait_for=[marts])

    logger.info("✅ NLP pipeline complete")
    return "nlp_complete"


# ============================================
# CLI Entry Point
# ============================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NHS Data Pipeline Orchestration")
    parser.add_argument(
        "--flow",
        choices=["full", "dbt", "nlp"],
        default="full",
        help="Which flow to run (default: full)",
    )
    parser.add_argument(
        "--no-generate",
        action="store_true",
        help="Skip data generation step",
    )
    parser.add_argument(
        "--no-nlp",
        action="store_true",
        help="Skip NLP pipeline step",
    )

    args = parser.parse_args()

    if args.flow == "full":
        nhs_full_pipeline(
            generate_data=not args.no_generate,
            run_nlp=not args.no_nlp,
        )
    elif args.flow == "dbt":
        nhs_dbt_refresh()
    elif args.flow == "nlp":
        nhs_nlp_only()