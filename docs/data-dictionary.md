# Data Dictionary

This page documents every dbt model in the pipeline, including column definitions,
data types, and lineage. Models are organised by layer.

---

## Staging layer

Staging models sit directly on top of the raw source data. Their job is narrow:
rename columns to a consistent convention, cast types correctly, and handle nulls.
No business logic lives here.

### stg_patients

Source: `raw.patients` (synthetic NHS patient register)

| Column | Type | Description |
|---|---|---|
| patient_id | VARCHAR | Surrogate key, generated at ingestion |
| nhs_number | VARCHAR | NHS number in XXX-XXX-XXXX format |
| date_of_birth | DATE | Patient date of birth |
| sex | VARCHAR | M, F, or U (unknown) |
| ethnicity_code | VARCHAR | ONS 2-digit ethnicity classification code |
| postcode | VARCHAR | Partial postcode (district only, for privacy) |
| gp_practice_code | VARCHAR | ODS code of registered GP practice |
| registered_date | DATE | Date registered with current GP |
| _loaded_at | TIMESTAMP | When this record entered the pipeline |

### stg_inpatient_episodes

Source: `raw.inpatient_episodes` (synthetic SUS/HES Admitted Patient Care)

| Column | Type | Description |
|---|---|---|
| episode_id | VARCHAR | Unique episode identifier |
| patient_id | VARCHAR | Foreign key to stg_patients |
| spell_id | VARCHAR | Hospital spell (groups episodes for same admission) |
| admission_date | DATE | Date of admission |
| discharge_date | DATE | Date of discharge (NULL if still admitted) |
| length_of_stay_days | INTEGER | Derived: discharge_date - admission_date |
| primary_diagnosis_icd10 | VARCHAR | ICD-10 code for primary diagnosis |
| admission_method_code | VARCHAR | HES admission method (e.g. 21 = emergency) |
| discharge_destination_code | VARCHAR | HES discharge destination code |
| provider_code | VARCHAR | ODS code of treating NHS Trust |
| _loaded_at | TIMESTAMP | When this record entered the pipeline |

### stg_clinical_notes

Source: `raw.clinical_notes` (synthetic discharge summaries and clinical letters)

| Column | Type | Description |
|---|---|---|
| note_id | VARCHAR | Unique note identifier |
| patient_id | VARCHAR | Foreign key to stg_patients |
| episode_id | VARCHAR | Foreign key to stg_inpatient_episodes |
| note_date | DATE | Date note was authored |
| note_type | VARCHAR | discharge_summary, outpatient, gp_referral, nursing |
| note_text | TEXT | Free-text clinical note content |
| clinician_id | VARCHAR | Anonymised clinician identifier |
| _loaded_at | TIMESTAMP | When this record entered the pipeline |

---

## Intermediate layer

Intermediate models apply business logic. Joins, aggregations, and clinical
derivations live here. They are not intended for direct consumption by end users.

### int_patient_demographics

Enriches patient records with derived age bands and deprivation proxies.

| Column | Type | Description |
|---|---|---|
| patient_id | VARCHAR | Primary key |
| nhs_number | VARCHAR | NHS number |
| date_of_birth | DATE | Date of birth |
| age_at_reference | INTEGER | Age in years at pipeline run date |
| age_band | VARCHAR | 0-17, 18-39, 40-64, 65-79, 80+ |
| sex | VARCHAR | M, F, U |
| ethnicity_code | VARCHAR | ONS ethnicity code |
| postcode_district | VARCHAR | Postcode district (e.g. SW1) |
| gp_practice_code | VARCHAR | GP practice ODS code |

### int_inpatient_spells

Groups episodes into complete hospital spells and calculates spell-level metrics.

| Column | Type | Description |
|---|---|---|
| spell_id | VARCHAR | Primary key |
| patient_id | VARCHAR | Foreign key |
| admission_date | DATE | First episode admission date |
| discharge_date | DATE | Last episode discharge date |
| total_length_of_stay | INTEGER | Total days across all episodes in spell |
| episode_count | INTEGER | Number of episodes within the spell |
| primary_diagnosis_icd10 | VARCHAR | Primary diagnosis from first episode |
| icd10_chapter | VARCHAR | Derived ICD-10 chapter (e.g. Diseases of the circulatory system) |
| admission_method_code | VARCHAR | Admission method |
| provider_code | VARCHAR | NHS Trust ODS code |
| is_emergency | BOOLEAN | True if admission_method in (21, 22, 23, 24, 25) |

### int_nlp_entities

NLP-extracted clinical entities joined back to their source notes.

| Column | Type | Description |
|---|---|---|
| entity_id | VARCHAR | Surrogate key |
| note_id | VARCHAR | Foreign key to stg_clinical_notes |
| patient_id | VARCHAR | Foreign key to stg_patients |
| entity_text | VARCHAR | Raw text of the extracted entity |
| entity_label | VARCHAR | spaCy label (DISEASE, DRUG, PROCEDURE, etc.) |
| start_char | INTEGER | Character offset start in note_text |
| end_char | INTEGER | Character offset end in note_text |
| confidence | FLOAT | Model confidence score (0-1) |
| note_date | DATE | Date of source note |

---

## Marts layer (OMOP CDM)

The marts layer produces the final OMOP CDM tables. These are the tables
consumed by the FHIR API, the cohort builder, and any downstream research tools.

### PERSON

| Column | Type | OMOP definition |
|---|---|---|
| person_id | INTEGER | OMOP surrogate key |
| gender_concept_id | INTEGER | OMOP standard concept for gender |
| year_of_birth | INTEGER | Year extracted from date_of_birth |
| month_of_birth | INTEGER | Month extracted from date_of_birth |
| race_concept_id | INTEGER | Mapped from ONS ethnicity code |
| ethnicity_concept_id | INTEGER | Hispanic / Not Hispanic (OMOP standard) |
| person_source_value | VARCHAR | Original patient_id |
| gender_source_value | VARCHAR | Original sex code |

### VISIT_OCCURRENCE

| Column | Type | OMOP definition |
|---|---|---|
| visit_occurrence_id | INTEGER | OMOP surrogate key |
| person_id | INTEGER | Foreign key to PERSON |
| visit_concept_id | INTEGER | 9201 (Inpatient), 9202 (Outpatient) |
| visit_start_date | DATE | Admission date |
| visit_end_date | DATE | Discharge date |
| visit_type_concept_id | INTEGER | 44818518 (EHR encounter) |
| visit_source_value | VARCHAR | Original spell_id |

### CONDITION_OCCURRENCE

| Column | Type | OMOP definition |
|---|---|---|
| condition_occurrence_id | INTEGER | OMOP surrogate key |
| person_id | INTEGER | Foreign key to PERSON |
| condition_concept_id | INTEGER | SNOMED CT concept mapped from ICD-10 |
| condition_start_date | DATE | Diagnosis date |
| condition_type_concept_id | INTEGER | 32817 (EHR) |
| condition_source_value | VARCHAR | Original ICD-10 code |
| visit_occurrence_id | INTEGER | Foreign key to VISIT_OCCURRENCE |

---

## dbt tests in place

Every model above has the following schema tests applied in `schema.yml`:

- `not_null` on all primary and foreign keys
- `unique` on all primary keys
- `accepted_values` on coded fields (sex, note_type, admission_method)
- `relationships` tests between fact and dimension tables
