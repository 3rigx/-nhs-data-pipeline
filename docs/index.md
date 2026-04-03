# NHS Data Pipeline

[![CI/CD Pipeline](https://github.com/3rigx/-nhs-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/3rigx/-nhs-data-pipeline/actions)
[![dbt](https://img.shields.io/badge/dbt-1.11+-orange.svg)](https://www.getdbt.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![OMOP CDM](https://img.shields.io/badge/OMOP-CDM%20v5.4-green.svg)](https://ohdsi.github.io/CommonDataModel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://3rigx.github.io/-nhs-data-pipeline)

> Built by **Greendly Guosadia** as a production-grade demonstration of NHS health data engineering,
> covering the full journey from raw synthetic hospital records through to a FHIR-compatible REST API.

---

## What this project does

Modern NHS Trusts generate enormous volumes of structured and unstructured clinical data every day.
Getting that data into a reliable, research-ready format is a non-trivial engineering challenge.
This project builds the full pipeline end-to-end, using open-source tools that mirror real infrastructure
used across London NHS Trusts (NHS England, 2013)[^1].

The pipeline handles seven distinct concerns:

1. **Ingestion** of synthetic NHS hospital data modelled on SUS/HES datasets
2. **Transformation** through a layered dbt ELT pipeline (staging, intermediate, marts)
3. **Standardisation** into the OMOP Common Data Model v5.4 (Observational Health Data Sciences and Informatics, 2024)[^2]
4. **Entity extraction** from free-text clinical notes using spaCy NLP
5. **Cohort generation** for five clinical research populations
6. **API exposure** via a FHIR R4-compatible FastAPI endpoint
7. **Orchestration** of the full pipeline using Prefect and Airflow

---

## Architecture overview

```
Raw Synthetic Data
       |
       v
  DuckDB Loader  ──>  dbt Staging  ──>  dbt Intermediate  ──>  OMOP CDM Marts
       |                                                              |
       v                                                              v
  Clinical Notes NLP                                        Research Cohort Builder
  (spaCy / MedCAT)                                                    |
                                                                      v
                                                            FastAPI FHIR R4 Endpoint
                                                                      |
                                          Orchestration: Prefect + Airflow
```

For a full component breakdown with design rationale, see [Architecture](architecture.md).

---

## Quick start

### Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- Docker Desktop (for the containerised stack)

### Local setup

```bash
git clone https://github.com/3rigx/-nhs-data-pipeline.git
cd -nhs-data-pipeline

# Install dependencies and set up pre-commit hooks
poetry install
poetry run pre-commit install

# Copy the environment template
cp .env.example .env
```

### Generate synthetic data and run the pipeline

```bash
# Generate synthetic NHS patient data
poetry run python src/ingestion/generate_synthetic_data.py

# Run the full dbt ELT pipeline
cd nhs_dbt && poetry run dbt run

# Run dbt data quality tests
poetry run dbt test

# Start the FHIR API
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Run with Docker

```bash
# Full stack: API + Prefect UI + dbt docs
docker compose up --build -d
```

| Service | URL |
|---|---|
| FHIR API + interactive docs | http://localhost:8000/docs |
| Prefect orchestration UI | http://localhost:4200 |
| dbt model lineage docs | http://localhost:8081 |
| Airflow scheduler UI | http://localhost:8080 |

---

## Project structure

```
nhs-data-pipeline/
├── src/
│   ├── ingestion/        # Synthetic data generator
│   ├── nlp/              # spaCy clinical NLP pipeline
│   ├── cohorts/          # Research cohort builder
│   └── api/              # FastAPI FHIR endpoint
├── nhs_dbt/
│   ├── models/
│   │   ├── staging/      # Raw source cleaning
│   │   ├── intermediate/ # Business logic
│   │   └── marts/        # OMOP CDM tables
│   └── seeds/            # Reference data
├── orchestration/
│   ├── dags/             # Airflow DAGs
│   └── flows/            # Prefect flows
├── docker/               # Dockerfiles and entrypoint
├── tests/                # pytest test suite
└── docs/                 # This documentation
```

---

## Technology stack

| Layer | Tool | Purpose |
|---|---|---|
| Data storage | DuckDB 1.5+ | Embedded analytical database |
| Transformation | dbt-core 1.11+ | SQL-based ELT with testing |
| Data model | OMOP CDM v5.4 | Clinical research standardisation |
| NLP | spaCy 3.8+ | Clinical entity extraction |
| API | FastAPI 0.135+ | FHIR R4 REST endpoint |
| Orchestration | Prefect 3 + Airflow 2.9 | Pipeline scheduling |
| CI/CD | GitHub Actions | Automated testing and deployment |
| Containerisation | Docker + Compose | Reproducible environments |

---

## Running the tests

```bash
# Full test suite with coverage
poetry run pytest tests/ -v --cov=src

# SQL model linting
poetry run sqlfluff lint nhs_dbt/models/ --dialect duckdb
```

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](../CONTRIBUTING.md) before opening a pull request.
All commits should follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

---

## Licence

This project is released under the [MIT Licence](../LICENSE).
All patient data used in this project is fully synthetic and does not represent any real individual.

---

[^1]: NHS England (2013) *NHS Hospital Data and Datasets: A Consultation*. London: NHS England. Available at: https://www.england.nhs.uk/wp-content/uploads/2013/07/hosp-data-consult.pdf (Accessed: 3 April 2026).
[^2]: Observational Health Data Sciences and Informatics (2024) *OMOP Common Data Model v5.4*. Available at: https://ohdsi.github.io/CommonDataModel/ (Accessed: 3 April 2026).
