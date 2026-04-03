# NLP Pipeline

The NLP pipeline extracts structured clinical information from free-text notes
using spaCy. This turns unstructured discharge summaries and clinical letters
into queryable entities that feed into the OMOP CDM and cohort builder.

---

## Why clinical NLP matters

A significant proportion of clinically relevant information in NHS systems
is locked inside free-text fields. Structured coded data (ICD-10, SNOMED CT)
captures diagnoses and procedures, but misses nuance: severity, laterality,
negation, and co-morbidity mentions that clinicians document in narrative form.
Clinical NLP bridges that gap (Spasic et al., 2020)[^1].

---

## Pipeline overview

```
Raw clinical note text
        |
        v
  Text preprocessing
  (lowercasing, whitespace normalisation, section splitting)
        |
        v
  spaCy en_core_web_sm
  (tokenisation, POS tagging, dependency parsing)
        |
        v
  Named Entity Recognition
  (DISEASE, DRUG, PROCEDURE, ANATOMY, FINDING)
        |
        v
  Negation detection
  (NegEx pattern matching)
        |
        v
  Entity linking (optional)
  (SNOMED CT via MedCAT when available)
        |
        v
  int_nlp_entities table in DuckDB
```

---

## Entity types extracted

| Label | Description | Example |
|---|---|---|
| DISEASE | Diagnosed conditions and symptoms | "myocardial infarction", "type 2 diabetes" |
| DRUG | Medications and substances | "aspirin", "metformin 500mg" |
| PROCEDURE | Clinical procedures | "coronary angiography", "CABG" |
| ANATOMY | Body parts and systems | "left ventricle", "renal cortex" |
| FINDING | Clinical findings and observations | "ST elevation", "SpO2 88%" |

---

## Negation handling

Not every entity mentioned in a note is a confirmed finding.
Clinicians routinely document what was ruled out:
"no evidence of pulmonary embolism" should not create a PE diagnosis record.

The pipeline uses a rule-based NegEx approach (Chapman et al., 2001)[^2]
to flag entities as negated, hypothetical, or historical before they
are written to the database.

```python
# Entities flagged with is_negated=True are excluded from OMOP mapping
# but retained in int_nlp_entities for audit purposes
```

---

## Running the pipeline

```bash
# Process all clinical notes in the database
poetry run python src/nlp/run_pipeline.py

# Or inside Docker
docker compose exec pipeline python src/nlp/run_pipeline.py
```

The pipeline processes notes in batches of 500 to keep memory usage stable.
Progress is logged to stdout and to the Prefect run log when orchestrated.

---

## Swapping in MedCAT for production use

The pipeline is designed so spaCy can be replaced with MedCAT
(Kraljevic et al., 2021)[^3] when real clinical data is used.
MedCAT provides SNOMED CT concept linking out of the box,
which maps extracted entities directly to OMOP concept IDs
without a separate vocabulary mapping step.

To enable MedCAT, set the following in your `.env`:

```bash
NLP_BACKEND=medcat
MEDCAT_MODEL_PATH=/path/to/your/medcat/model
```

The pipeline will automatically use MedCAT when this variable is present.

---

## Limitations

- The `en_core_web_sm` model is a general-purpose English model, not trained on clinical text. Entity recognition accuracy on clinical notes is lower than a purpose-built clinical model.
- Abbreviation expansion is not implemented in this version. Common NHS abbreviations (SOB, COPD, AF) are recognised by the base model but may be missed in unusual contexts.
- The pipeline processes English-language notes only.

---

[^1]: Spasic, I. et al. (2020) 'Clinical text mining of radiology reports', in *Artificial Intelligence in Healthcare*. London: Academic Press, pp. 155-182.
[^2]: Chapman, W.W. et al. (2001) 'A simple algorithm for identifying negated findings and diseases in discharge summaries', *Journal of Biomedical Informatics*, 34(5), pp. 301-310.
[^3]: Kraljevic, Z. et al. (2021) 'Multi-domain clinical natural language processing with MedCAT', *Artificial Intelligence in Medicine*, 117, p. 102083.
