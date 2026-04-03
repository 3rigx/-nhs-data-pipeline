# Architecture

This page explains how the pipeline is structured, why each tool was chosen,
and how the components interact. It is intended for developers and technical reviewers.

---

## Design principles

The pipeline was designed around three priorities:

1. **Reproducibility** — every run produces the same output given the same inputs
2. **Testability** — every layer has automated quality checks before data moves forward
3. **Portability** — the full stack runs locally via Docker with no cloud dependencies

---

## Data flow

```
                      ┌─────────────────────────────┐
                      │   Synthetic Data Generator   │
                      │   (Faker + custom NHS logic) │
                      └────────────────┬────────────┘
                                       |
                              CSV / Parquet files
                                       |
                                       v
                      ┌─────────────────────────────┐
                      │       DuckDB Loader          │
                      │  src/ingestion/loader.py     │
                      └────────────────┬────────────┘
                                       |
                                       v
                      ┌─────────────────────────────┐
                      │     dbt Staging Layer        │
                      │  nhs_dbt/models/staging/     │
                      │  - Type casting              │
                      │  - Field renaming            │
                      │  - Null handling             │
                      └────────────────┬────────────┘
                                       |
                                       v
                      ┌─────────────────────────────┐
                      │   dbt Intermediate Layer     │
                      │  nhs_dbt/models/intermediate/│
                      │  - Business logic            │
                      │  - Joins and aggregations    │
                      │  - Derived clinical fields   │
                      └────────────────┬────────────┘
                                       |
                                       v
                      ┌─────────────────────────────┐
                      │    OMOP CDM Mart Layer       │
                      │  nhs_dbt/models/marts/       │
                      │  PERSON, VISIT_OCCURRENCE,   │
                      │  CONDITION_OCCURRENCE, etc.  │
                      └────────┬──────────┬──────────┘
                               |          |
               ┌───────────────┘          └──────────────────┐
               v                                              v
┌──────────────────────────┐              ┌──────────────────────────────┐
│   Research Cohort Builder│              │   Clinical NLP Pipeline      │
│   src/cohorts/           │              │   src/nlp/                   │
│   5 clinical cohorts     │              │   spaCy entity extraction    │
└──────────────────────────┘              └──────────────────────────────┘
               |                                              |
               └──────────────────┬───────────────────────────┘
                                  v
                  ┌───────────────────────────────┐
                  │   FastAPI FHIR R4 Endpoint    │
                  │   src/api/                    │
                  │   /Patient, /Condition,       │
                  │   /Observation, /Bundle       │
                  └───────────────────────────────┘
                                  |
                  ┌───────────────────────────────┐
                  │   Orchestration Layer         │
                  │   Prefect flows + Airflow DAGs│
                  └───────────────────────────────┘
```

---

## Component decisions

### DuckDB as the analytical store

DuckDB was chosen over PostgreSQL or SQLite for several reasons.
It is an embedded columnar database designed for analytical workloads,
meaning it executes complex aggregations significantly faster than row-oriented stores
for the kinds of queries health data research typically requires (Raasveldt and Muehleisen, 2019)[^1].
It also requires no server process, which keeps the local development experience simple
and makes it straightforward to run the full pipeline inside a single Docker container.

### dbt for transformation

dbt (data build tool) brings software engineering practices to SQL transformations.
Every model is version-controlled, testable, and documented in the same codebase.
The three-layer architecture (staging, intermediate, marts) follows the pattern
recommended by dbt Labs (2023)[^2] and mirrors how NHS Trusts typically structure
their analytical engineering work.

### OMOP CDM for standardisation

The Observational Medical Outcomes Partnership Common Data Model (OMOP CDM) is the
dominant standard for structuring clinical research data. By mapping raw NHS data
to OMOP v5.4, the pipeline produces data that can be queried using ATLAS and other
OHDSI tools without modification, and that is directly comparable to datasets from
other healthcare systems internationally (Observational Health Data Sciences and
Informatics, 2024)[^3].

### spaCy for NLP

spaCy was selected for its production maturity and its active NHS/clinical NLP ecosystem.
The en_core_web_sm model provides a baseline for entity recognition which can be
swapped out for MedCAT (Kraljevic et al., 2021)[^4], a dedicated clinical NLP library
trained on SNOMED CT, when real clinical data is used.

### FastAPI for the API layer

FastAPI generates OpenAPI documentation automatically, supports async request handling,
and integrates cleanly with Pydantic for FHIR R4 schema validation.
The endpoint design follows the HL7 FHIR R4 specification (HL7 International, 2023)[^5].

---

## Database schema (OMOP CDM tables implemented)

| Table | Description |
|---|---|
| PERSON | One row per patient, demographic information |
| VISIT_OCCURRENCE | Every hospital admission or outpatient encounter |
| CONDITION_OCCURRENCE | Diagnoses mapped from ICD-10 |
| DRUG_EXPOSURE | Medications and prescriptions |
| PROCEDURE_OCCURRENCE | Clinical procedures performed |
| MEASUREMENT | Lab results and vital signs |
| OBSERVATION | Clinical observations not covered by other tables |
| CARE_SITE | NHS Trust and ward reference data |
| PROVIDER | Clinician reference data |

---

[^1]: Raasveldt, M. and Muehleisen, H. (2019) 'DuckDB: an embeddable analytical database', *Proceedings of the 2019 ACM SIGMOD International Conference on Management of Data*, pp. 1981-1984.
[^2]: dbt Labs (2023) *dbt Best Practices: How we structure our dbt projects*. Available at: https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview (Accessed: 3 April 2026).
[^3]: Observational Health Data Sciences and Informatics (2024) *OMOP Common Data Model v5.4*. Available at: https://ohdsi.github.io/CommonDataModel/ (Accessed: 3 April 2026).
[^4]: Kraljevic, Z. et al. (2021) 'Multi-domain clinical natural language processing with MedCAT', *Artificial Intelligence in Medicine*, 117, p. 102083.
[^5]: HL7 International (2023) *FHIR R4: HL7 Fast Healthcare Interoperability Resources*. Available at: https://hl7.org/fhir/R4/ (Accessed: 3 April 2026).
