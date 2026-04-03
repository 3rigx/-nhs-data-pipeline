"""
Generate minimal synthetic seed data for dbt CI runs.
Writes CSV seeds to nhs_dbt/seeds/ so dbt can run staging models
against DuckDB in-memory without needing the full data generator.
"""
import csv
import os
import random
from datetime import date, timedelta
from pathlib import Path

SEEDS_DIR = Path("nhs_dbt/seeds")
SEEDS_DIR.mkdir(parents=True, exist_ok=True)

ROWS = 50
random.seed(42)

def random_date(start_year=2020, end_year=2024):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

# ── patients ─────────────────────────────────────────────────────────────────
with open(SEEDS_DIR / "ci_patients.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["patient_id","nhs_number","date_of_birth","sex","ethnicity","postcode","gp_practice_code","registered_date"])
    w.writeheader()
    sexes = ["M", "F", "U"]
    ethnicities = ["A", "B", "C", "D", "E", "F", "Z"]
    for i in range(1, ROWS + 1):
        w.writerow({
            "patient_id": f"P{i:05d}",
            "nhs_number": f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            "date_of_birth": random_date(1940, 2000),
            "sex": random.choice(sexes),
            "ethnicity": random.choice(ethnicities),
            "postcode": f"SW{random.randint(1,20)} {random.randint(1,9)}AA",
            "gp_practice_code": f"G{random.randint(10000,99999)}",
            "registered_date": random_date(2010, 2022),
        })

# ── inpatient episodes ────────────────────────────────────────────────────────
with open(SEEDS_DIR / "ci_inpatient_episodes.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["episode_id","patient_id","admission_date","discharge_date","primary_diagnosis_icd10","admission_method","discharge_destination","spell_id","provider_code"])
    w.writeheader()
    diagnoses = ["I21.0","J18.1","K80.0","N39.0","F32.1","C34.1","E11.9","I63.9","M54.5","Z51.1"]
    for i in range(1, ROWS + 1):
        adm = random_date()
        dis = adm + timedelta(days=random.randint(1, 14))
        w.writerow({
            "episode_id": f"EP{i:06d}",
            "patient_id": f"P{random.randint(1,ROWS):05d}",
            "admission_date": adm,
            "discharge_date": dis,
            "primary_diagnosis_icd10": random.choice(diagnoses),
            "admission_method": random.choice(["11","21","22","31"]),
            "discharge_destination": random.choice(["19","51","52","54"]),
            "spell_id": f"SP{i:06d}",
            "provider_code": f"RJ{random.randint(100,999)}",
        })

# ── clinical notes ────────────────────────────────────────────────────────────
templates = [
    "Patient presented with chest pain. ECG showed ST elevation. Started on aspirin and clopidogrel.",
    "Admitted with shortness of breath. SpO2 88%. CXR confirms consolidation. Started IV antibiotics.",
    "Type 2 diabetes poorly controlled. HbA1c 85mmol/mol. Medication reviewed and metformin increased.",
    "Elective cholecystectomy performed. Procedure uneventful. Patient discharged day 2 post-op.",
    "Mental health review. Patient reports low mood and anhedonia for 3 months. PHQ-9 score 18.",
]
with open(SEEDS_DIR / "ci_clinical_notes.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["note_id","patient_id","episode_id","note_date","note_type","note_text","clinician_id"])
    w.writeheader()
    for i in range(1, ROWS + 1):
        w.writerow({
            "note_id": f"N{i:06d}",
            "patient_id": f"P{random.randint(1,ROWS):05d}",
            "episode_id": f"EP{random.randint(1,ROWS):06d}",
            "note_date": random_date(),
            "note_type": random.choice(["discharge_summary","outpatient","gp_referral","nursing"]),
            "note_text": random.choice(templates),
            "clinician_id": f"DR{random.randint(1000,9999)}",
        })

print(f"✅ CI seed data written to {SEEDS_DIR}/")
print(f"   - ci_patients.csv ({ROWS} rows)")
print(f"   - ci_inpatient_episodes.csv ({ROWS} rows)")
print(f"   - ci_clinical_notes.csv ({ROWS} rows)")
