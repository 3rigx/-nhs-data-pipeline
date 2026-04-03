# Changelog

All notable changes to the NHS Data Pipeline will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- CI/CD pipeline with GitHub Actions (Task 10)
  - Multi-job CI workflow: lint, SQL lint, pytest (Python 3.11 & 3.12), dbt compile/test, FastAPI smoke test, Docker build
  - PR checks: Conventional Commits title enforcement, Bandit security scan, pip-audit dependency audit
  - Release workflow: Docker image publish to GHCR on semver tag
  - Dependabot for pip, GitHub Actions, and Docker dependency updates
  - PR template and CHANGELOG

---

## [0.9.0] - 2026-04-03

### Added
- Task 1: Project architecture and scaffolding
- Task 2: Synthetic NHS data generation (Faker-based)
- Task 3: DuckDB loader and dbt staging models
- Task 4: dbt intermediate models
- Task 5: OMOP CDM transformation layer
- Task 6: NLP pipeline for clinical notes (spaCy/MedCAT)
- Task 7: Orchestration with Prefect and Airflow
- Task 8: Research cohort builder (5 clinical cohorts)
- Task 9: FastAPI REST API with FHIR R4 endpoints
