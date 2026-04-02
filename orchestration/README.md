# 🔄 NHS Data Pipeline — Orchestration

## Pipeline Architecture

```text
                        NHS Data Pipeline DAG
                        =====================

[start]
   │
   ▼
[generate_synthetic_data] ──► [load_to_duckdb]
                                     │
                                     ▼
                              [dbt_deps] ──► [dbt_seed]
                                                  │
                              ┌───────────────────┤
                              │                   │
                              ▼                   ▼
                    [dbt_run_staging]    [dbt_run_staging]
                              │                   │
                              ▼                   ▼
                   [dbt_test_staging]   [dbt_test_staging]
                              │                   │
              ┌───────────────┤                   │
              │               │                   │
              ▼               ▼                   │
   [run_nlp_pipeline]  [dbt_run_intermediate]     │
              │               │                   │
              ▼               ▼                   │
   [dbt_run_nlp_marts] [dbt_test_intermediate]    │
              │               │                   │
              ▼               ▼                   │
   [dbt_test_nlp]      [dbt_run_omop]            │
              │               │                   │
              │               ▼                   │
              │        [dbt_test_omop]            │
              │               │                   │
              └───────┬───────┘                   │
                      │                           │
                      ▼                           │
              [dbt_run_cohorts]                   │
                      │                           │
                      ▼                           │
              [dbt_final_test]                    │
                      │                           │
                      ▼                           │
                    [end]