# 🏥 NHS Data Pipeline

> End-to-end data engineering platform for NHS health data: ELT pipelines,
> OMOP Common Data Model, Clinical NLP, and Research Cohort Generation.

[![CI/CD Pipeline](https://github.com/3rigx/nhs-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/nhs-data-pipeline/actions)
[![dbt](https://img.shields.io/badge/dbt-1.7+-orange.svg)](https://www.getdbt.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Overview

This project demonstrates a **production-grade NHS data engineering platform**
that mirrors real-world health data infrastructure used across London NHS Trusts.

### What It Does

1. **Ingests** synthetic NHS hospital data (SUS/HES, primary care, clinical notes)
2. **Transforms** raw data through staging → intermediate → marts layers using dbt
3. **Standardises** data into the OMOP Common Data Model for research
4. **Extracts** clinical entities from unstructured notes using NLP (MedCAT/spaCy)
5. **Generates** research cohorts for analysis and machine learning
6. **Exposes** data via a FHIR-compatible REST API
7. **Orchestrates** the full pipeline with Airflow/Prefect

### Architecture

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Synthetic    │     │   dbt ELT    │     │    Research       │
│  NHS Data     │────▶│  Pipeline    │────▶│    Cohorts        │
│  Generator    │     │  (Snowflake/ │     │    (OMOP CDM)     │
└──────────────┘     │   DuckDB)    │     └──────────────────┘
                      └──────┬───────┘
┌──────────────┐            │            ┌──────────────────┐
│  Clinical     │            │            │   FHIR-Ready     │
│  Notes (NLP) │────────────┘            │   REST API       │
│  MedCAT       │                         │   (FastAPI)      │
└──────────────┘                         └──────────────────┘