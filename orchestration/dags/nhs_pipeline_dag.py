"""
NHS Data Pipeline - Apache Airflow DAG
========================================
Production-grade pipeline orchestration using Airflow.

This DAG orchestrates the full NHS data pipeline:
1. Generate synthetic NHS data
2. Load into DuckDB/Snowflake
3. Run dbt transformations
4. Execute clinical NLP pipeline
5. Run data quality tests

Designed for deployment across London NHS Trusts.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule

# ============================================
# DAG Configuration
# ============================================

PROJECT_DIR = "/opt/airflow/project"
DBT_DIR = f"{PROJECT_DIR}/nhs_dbt"
DBT_ENV = {"DBT_PROFILES_DIR": DBT_DIR}

default_args = {
    "owner": "nhs_data_engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "email": ["data-engineering@nhs.net"],
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=1),
}

# ============================================
# Main Pipeline DAG
# ============================================

with DAG(
    dag_id="nhs_data_pipeline",
    default_args=default_args,
    description="End-to-end NHS data pipeline: ELT, OMOP CDM, Clinical NLP",
    schedule_interval="0 2 * * *",  # Daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["nhs", "data-engineering", "dbt", "nlp", "omop"],
    doc_md="""
    ## NHS Data Pipeline
    
    **Owner:** Data Engineering Team  
    **Schedule:** Daily at 02:00 UTC  
    **Platform:** DuckDB (dev) / Snowflake (prod)
    
    ### Pipeline Stages:
    1. **Ingestion** — Generate/load synthetic NHS data
    2. **Transformation** — dbt staging → intermediate → marts
    3. **OMOP CDM** — Map to OMOP Common Data Model
    4. **NLP** — Extract entities from clinical notes
    5. **Quality** — Run data quality tests
    
    ### Data Sources:
    - Patient demographics (SUS/HES format)
    - Hospital episodes
    - ICD-10 diagnoses
    - OPCS-4 procedures
    - Medications
    - Lab results
    - Unstructured clinical notes
    """,
) as dag:

    # ---- Start ----
    start = EmptyOperator(task_id="start")

    # ---- Phase 1: Data Ingestion ----
    generate_data = BashOperator(
        task_id="generate_synthetic_data",
        bash_command=f"cd {PROJECT_DIR} && python src/ingestion/generate_synthetic_data.py",
        doc_md="Generate synthetic NHS patient data",
    )

    load_duckdb = BashOperator(
        task_id="load_to_duckdb",
        bash_command=f"cd {PROJECT_DIR} && python src/ingestion/load_to_duckdb.py",
        doc_md="Load raw CSV data into DuckDB warehouse",
    )

    # ---- Phase 2: dbt Setup ----
    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"cd {DBT_DIR} && dbt deps",
        env=DBT_ENV,
        doc_md="Install dbt package dependencies",
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"cd {DBT_DIR} && dbt seed",
        env=DBT_ENV,
        doc_md="Load reference data (ICD-10, SNOMED, OMOP mappings)",
    )

    # ---- Phase 3: dbt Transformations ----
    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=f"cd {DBT_DIR} && dbt run --select staging",
        env=DBT_ENV,
        doc_md="Run staging models — clean and standardise raw data",
    )

    dbt_test_staging = BashOperator(
        task_id="dbt_test_staging",
        bash_command=f"cd {DBT_DIR} && dbt test --select staging",
        env=DBT_ENV,
        doc_md="Test staging models — validate data quality",
    )

    dbt_run_intermediate = BashOperator(
        task_id="dbt_run_intermediate",
        bash_command=f"cd {DBT_DIR} && dbt run --select intermediate",
        env=DBT_ENV,
        doc_md="Run intermediate models — enrich and join data",
    )

    dbt_test_intermediate = BashOperator(
        task_id="dbt_test_intermediate",
        bash_command=f"cd {DBT_DIR} && dbt test --select intermediate",
        env=DBT_ENV,
        doc_md="Test intermediate models",
    )

    # ---- Phase 4: OMOP CDM ----
    dbt_run_omop = BashOperator(
        task_id="dbt_run_omop",
        bash_command=f"cd {DBT_DIR} && dbt run --select tag:omop",
        env=DBT_ENV,
        doc_md="Run OMOP CDM models — map NHS data to international standard",
    )

    dbt_test_omop = BashOperator(
        task_id="dbt_test_omop",
        bash_command=f"cd {DBT_DIR} && dbt test --select tag:omop",
        env=DBT_ENV,
        doc_md="Test OMOP CDM models",
    )

    # ---- Phase 5: NLP Pipeline ----
    run_nlp = BashOperator(
        task_id="run_nlp_pipeline",
        bash_command=f"cd {PROJECT_DIR} && python src/nlp/run_pipeline.py",
        doc_md="Run clinical NLP — extract entities from unstructured notes",
        execution_timeout=timedelta(minutes=30),
    )

    dbt_run_nlp = BashOperator(
        task_id="dbt_run_nlp_marts",
        bash_command=f"cd {DBT_DIR} && dbt run --select tag:nlp",
        env=DBT_ENV,
        doc_md="Run NLP mart models — structure NLP outputs",
    )

    dbt_test_nlp = BashOperator(
        task_id="dbt_test_nlp",
        bash_command=f"cd {DBT_DIR} && dbt test --select tag:nlp",
        env=DBT_ENV,
        doc_md="Test NLP mart models",
    )

    # ---- Phase 6: Cohorts ----
    dbt_run_cohorts = BashOperator(
        task_id="dbt_run_cohorts",
        bash_command=f"cd {DBT_DIR} && dbt run --select tag:cohorts",
        env=DBT_ENV,
        doc_md="Run research cohort generation models",
    )

    # ---- Phase 7: Final Validation ----
    dbt_final_test = BashOperator(
        task_id="dbt_final_test",
        bash_command=f"cd {DBT_DIR} && dbt test",
        env=DBT_ENV,
        trigger_rule=TriggerRule.ALL_SUCCESS,
        doc_md="Run ALL data quality tests as final validation",
    )

    # ---- End ----
    end = EmptyOperator(
        task_id="end",
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    # ============================================
    # Task Dependencies (Pipeline Flow)
    # ============================================

    # Phase 1: Ingestion
    start >> generate_data >> load_duckdb

    # Phase 2: dbt Setup
    load_duckdb >> dbt_deps >> dbt_seed

    # Phase 3: Transformations
    dbt_seed >> dbt_run_staging >> dbt_test_staging
    dbt_test_staging >> dbt_run_intermediate >> dbt_test_intermediate

    # Phase 4: OMOP (depends on intermediate)
    dbt_test_intermediate >> dbt_run_omop >> dbt_test_omop

    # Phase 5: NLP (can run after staging tests pass)
    dbt_test_staging >> run_nlp >> dbt_run_nlp >> dbt_test_nlp

    # Phase 6: Cohorts (depends on OMOP and NLP)
    [dbt_test_omop, dbt_test_nlp] >> dbt_run_cohorts

    # Phase 7: Final validation
    dbt_run_cohorts >> dbt_final_test >> end


# ============================================
# dbt Refresh DAG (Quick rebuild)
# ============================================

with DAG(
    dag_id="nhs_dbt_refresh",
    default_args=default_args,
    description="Quick dbt model refresh without data regeneration",
    schedule_interval=None,  # Manual trigger only
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["nhs", "dbt", "refresh"],
) as dbt_refresh_dag:

    start = EmptyOperator(task_id="start")

    deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"cd {DBT_DIR} && dbt deps",
        env=DBT_ENV,
    )

    seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"cd {DBT_DIR} && dbt seed",
        env=DBT_ENV,
    )

    run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run",
        env=DBT_ENV,
    )

    test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test",
        env=DBT_ENV,
    )

    end = EmptyOperator(task_id="end")

    start >> deps >> seed >> run >> test >> end