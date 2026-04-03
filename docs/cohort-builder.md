# Cohort Builder

The research cohort builder generates reproducible patient populations
from the OMOP CDM marts. Each cohort is defined by a set of clinical inclusion
and exclusion criteria, following the phenotyping approach recommended by
the OHDSI community (Hripcsak et al., 2016)[^1].

---

## Why cohort-based research?

Most clinical research questions are not about all patients, but about a
specific sub-population. The coronary heart disease cohort, for example,
only includes patients who have had a relevant diagnosis within a defined
observation window, and excludes patients who died before the study period.
Defining these rules explicitly, and testing them against known data, is
essential for producing reproducible research (Garza et al., 2016)[^2].

---

## The five pre-defined cohorts

### 1. Coronary Heart Disease (CHD_COHORT)

**Clinical question:** Patients with a confirmed diagnosis of ischaemic heart disease.

**Inclusion criteria:**
- At least one CONDITION_OCCURRENCE with an ICD-10 code in the range I20-I25
- At least one inpatient visit in the observation period
- Age 18 or over at index date

**Exclusion criteria:**
- No valid NHS number
- Date of death before index date

**Index date:** Date of first qualifying condition occurrence.

---

### 2. Type 2 Diabetes (T2D_COHORT)

**Clinical question:** Patients with a confirmed diagnosis of type 2 diabetes mellitus.

**Inclusion criteria:**
- At least one CONDITION_OCCURRENCE with ICD-10 code E11.x
- Minimum 365 days of observation prior to index date

**Exclusion criteria:**
- Any prior diagnosis of type 1 diabetes (E10.x)
- Age under 18 at index date

**Index date:** Date of first qualifying condition occurrence.

---

### 3. Stroke and TIA (STROKE_COHORT)

**Clinical question:** Patients presenting with acute stroke or transient ischaemic attack.

**Inclusion criteria:**
- At least one emergency inpatient admission (admission method 21-25)
- Primary diagnosis ICD-10 code in I60-I64 (stroke) or G45 (TIA)

**Exclusion criteria:**
- Subarachnoid haemorrhage as primary cause (I60) can be separated into a sub-cohort

**Index date:** Date of qualifying emergency admission.

---

### 4. Respiratory Disease (RESP_COHORT)

**Clinical question:** Patients with chronic respiratory conditions requiring hospital care.

**Inclusion criteria:**
- At least one CONDITION_OCCURRENCE with ICD-10 code in J40-J47 (COPD, asthma, bronchiectasis)
- At least one inpatient or outpatient visit

**Exclusion criteria:**
- Diagnoses coded purely as acute upper respiratory tract infection (J00-J06) without chronic code

**Index date:** Date of first qualifying condition occurrence.

---

### 5. Elderly Frailty (FRAILTY_COHORT)

**Clinical question:** Patients aged 65 and over with markers of clinical frailty.

**Inclusion criteria:**
- Age 65 or over at index date
- At least two emergency admissions in any 12-month window
- At least one of: falls diagnosis (W00-W19), dementia (F00-F03), pressure injury (L89)

**Exclusion criteria:**
- Patients in palliative care pathway (Z51.5) at index date

**Index date:** Date of second qualifying emergency admission.

---

## Building a custom cohort

Custom cohorts can be defined by extending the base cohort class in `src/cohorts/`.
Each cohort requires three components:

**1. Inclusion SQL** — a DuckDB query returning qualifying `person_id` values:

```python
INCLUSION_QUERY = """
    SELECT DISTINCT person_id
    FROM condition_occurrence
    WHERE condition_source_value LIKE 'N18%'  -- Chronic kidney disease
    AND condition_start_date >= '2020-01-01'
"""
```

**2. Exclusion SQL** — a query returning `person_id` values to remove:

```python
EXCLUSION_QUERY = """
    SELECT DISTINCT person_id
    FROM condition_occurrence
    WHERE condition_source_value LIKE 'Z99.2%'  -- Dependence on renal dialysis
"""
```

**3. Cohort registration:**

```python
from src.cohorts.base import BaseCohort

class CKDCohort(BaseCohort):
    cohort_id = "CKD_COHORT"
    name = "Chronic Kidney Disease"
    inclusion_query = INCLUSION_QUERY
    exclusion_query = EXCLUSION_QUERY
```

---

## Running cohort generation

```bash
# Generate all cohorts
poetry run python src/cohorts/run_cohorts.py

# Or inside Docker
docker compose exec pipeline python src/cohorts/run_cohorts.py
```

Results are written to the `cohort_member` OMOP CDM table.

---

[^1]: Hripcsak, G. et al. (2016) 'Characterizing treatment pathways at scale using the OMOP common data model', *Proceedings of the National Academy of Sciences*, 113(27), pp. 7329-7336.
[^2]: Garza, M. et al. (2016) 'Evaluating common data models for use with a longitudinal community registry', *Journal of Biomedical Informatics*, 64, pp. 333-341.
