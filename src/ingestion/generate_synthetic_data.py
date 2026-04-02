"""
NHS Synthetic Data Generator
=============================
Generates realistic synthetic NHS data for the pipeline project.
Mirrors SUS/HES, primary care, and clinical notes formats.

DISCLAIMER: All data is synthetic. No real patient data is used.
"""


import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


import csv
import os
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

# Initialize Faker with UK locale
fake = Faker("en_GB")
Faker.seed(42)
random.seed(42)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
SEEDS_DIR = PROJECT_ROOT / "nhs_dbt" / "seeds"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# CONSTANTS — Real NHS Reference Data
# ============================================

LONDON_TRUSTS = [
    ("RJ1", "Guy's and St Thomas' NHS Foundation Trust"),
    ("RJZ", "King's College Hospital NHS Foundation Trust"),
    ("RAL", "Royal Free London NHS Foundation Trust"),
    ("RQM", "Chelsea and Westminster Hospital NHS Foundation Trust"),
    ("RYJ", "Imperial College Healthcare NHS Trust"),
    ("RNJ", "Barts Health NHS Trust"),
    ("R1H", "St George's University Hospitals NHS Foundation Trust"),
    ("RKE", "Whittington Health NHS Trust"),
    ("RAX", "Kingston Hospital NHS Foundation Trust"),
    ("RJ6", "Croydon Health Services NHS Trust"),
]

GP_PRACTICES = [
    ("Y00001", "The Bermondsey Practice"),
    ("Y00002", "Lambeth Walk Group Practice"),
    ("Y00003", "Camberwell Green Surgery"),
    ("Y00004", "Brixton Hill Group Practice"),
    ("Y00005", "Greenwich Medical Centre"),
    ("Y00006", "Lewisham Medical Centre"),
    ("Y00007", "Hackney Road Surgery"),
    ("Y00008", "Islington Central Medical Centre"),
    ("Y00009", "Camden Town Group Practice"),
    ("Y00010", "Westminster Health Centre"),
    ("Y00011", "Tower Hamlets Practice"),
    ("Y00012", "Southwark Bridge Road Surgery"),
    ("Y00013", "Wandsworth Common Surgery"),
    ("Y00014", "Kensington Park Medical Centre"),
    ("Y00015", "Croydon Family Practice"),
]

ETHNICITY_CODES = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "R", "S"]

# ICD-10 codes with weights (more common conditions appear more often)
ICD10_CODES_WEIGHTED = [
    ("I10", 15),    # Hypertension
    ("E11.9", 12),  # Type 2 diabetes
    ("I50.0", 8),   # Heart failure
    ("J44.1", 8),   # COPD
    ("J45.9", 7),   # Asthma
    ("I21.9", 5),   # MI
    ("I48.9", 6),   # AF
    ("I63.9", 4),   # Stroke
    ("J18.1", 6),   # Pneumonia
    ("N39.0", 7),   # UTI
    ("C50.9", 3),   # Breast cancer
    ("C34.9", 2),   # Lung cancer
    ("F32.1", 5),   # Depression
    ("M54.5", 6),   # Back pain
    ("K80.2", 3),   # Gallstones
    ("R07.9", 5),   # Chest pain
    ("S72.0", 3),   # Hip fracture
    ("N18.3", 4),   # CKD stage 3
    ("D64.9", 4),   # Anaemia
    ("E78.0", 5),   # Hypercholesterolaemia
    ("I25.1", 4),   # IHD
    ("J96.0", 2),   # Respiratory failure
    ("L03.1", 3),   # Cellulitis
    ("K21.0", 4),   # GORD
    ("G30.9", 2),   # Alzheimers
]

OPCS4_CODES = [
    "W37.1", "W38.1", "W40.1", "K22.2", "G45.1",
    "H22.9", "K63.1", "K49.1", "E85.1", "T46.2",
    "Y53.1", "X29.2", "B27.5",
]

ADMISSION_METHODS = [
    ("11", "Elective - Waiting List"),
    ("12", "Elective - Booked"),
    ("13", "Elective - Planned"),
    ("21", "Emergency - A&E"),
    ("22", "Emergency - GP"),
    ("23", "Emergency - Bed Bureau"),
    ("28", "Emergency - Other"),
    ("31", "Maternity - Ante-partum"),
    ("32", "Maternity - Post-partum"),
]

DISCHARGE_METHODS = [
    ("1", "Discharged on clinical advice"),
    ("2", "Self-discharged"),
    ("3", "Discharged by mental health tribunal"),
    ("4", "Died"),
    ("8", "Not applicable - still inpatient"),
    ("9", "Not known"),
]

DISCHARGE_DESTINATIONS = [
    ("19", "Usual place of residence"),
    ("29", "Temporary place of residence"),
    ("30", "Repatriation from high security psychiatric hospital"),
    ("37", "Penal establishment"),
    ("48", "High security psychiatric hospital"),
    ("49", "NHS other hospital - ward for general patients"),
    ("50", "NHS other hospital - ward for maternity patients"),
    ("51", "NHS other hospital - ward for mental health patients"),
    ("52", "Care home with nursing"),
    ("53", "Care home without nursing"),
    ("79", "Not applicable - patient died or stillbirth"),
    ("84", "Non-NHS hospital"),
    ("85", "Hospice"),
]

WARD_TYPES = [
    "Medical Assessment Unit",
    "Surgical Assessment Unit",
    "Cardiology Ward",
    "Respiratory Ward",
    "Orthopaedic Ward",
    "Oncology Ward",
    "General Medical Ward",
    "General Surgical Ward",
    "Intensive Care Unit",
    "Emergency Department",
    "Maternity Ward",
    "Stroke Unit",
    "Elderly Care Ward",
    "Gastroenterology Ward",
    "Neurology Ward",
]

SPECIALTIES = [
    ("100", "General Surgery"),
    ("101", "Urology"),
    ("110", "Trauma & Orthopaedics"),
    ("120", "ENT"),
    ("130", "Ophthalmology"),
    ("140", "Oral Surgery"),
    ("150", "Neurosurgery"),
    ("160", "Plastic Surgery"),
    ("170", "Cardiothoracic Surgery"),
    ("300", "General Medicine"),
    ("301", "Gastroenterology"),
    ("302", "Endocrinology"),
    ("303", "Clinical Haematology"),
    ("320", "Cardiology"),
    ("330", "Dermatology"),
    ("340", "Respiratory Medicine"),
    ("350", "Infectious Diseases"),
    ("360", "Genito-Urinary Medicine"),
    ("370", "Medical Oncology"),
    ("400", "Neurology"),
    ("410", "Rheumatology"),
    ("420", "Paediatrics"),
    ("430", "Geriatric Medicine"),
    ("500", "Obstetrics"),
    ("501", "Obstetrics"),
    ("502", "Gynaecology"),
    ("560", "Midwifery"),
]

# Medication data
MEDICATIONS = [
    ("Metformin", "500mg", "tablet", "oral", "twice daily", "Diabetes"),
    ("Amlodipine", "5mg", "tablet", "oral", "once daily", "Hypertension"),
    ("Ramipril", "5mg", "capsule", "oral", "once daily", "Hypertension"),
    ("Bisoprolol", "2.5mg", "tablet", "oral", "once daily", "Heart Failure"),
    ("Atorvastatin", "20mg", "tablet", "oral", "once daily", "Hyperlipidaemia"),
    ("Salbutamol", "100mcg", "inhaler", "inhaled", "as required", "Asthma"),
    ("Omeprazole", "20mg", "capsule", "oral", "once daily", "GORD"),
    ("Levothyroxine", "50mcg", "tablet", "oral", "once daily", "Hypothyroidism"),
    ("Warfarin", "3mg", "tablet", "oral", "once daily", "AF/VTE"),
    ("Paracetamol", "500mg", "tablet", "oral", "four times daily", "Pain"),
    ("Co-codamol", "30/500mg", "tablet", "oral", "four times daily", "Pain"),
    ("Amoxicillin", "500mg", "capsule", "oral", "three times daily", "Infection"),
    ("Doxycycline", "100mg", "capsule", "oral", "once daily", "Infection"),
    ("Furosemide", "40mg", "tablet", "oral", "once daily", "Heart Failure"),
    ("Sertraline", "50mg", "tablet", "oral", "once daily", "Depression"),
    ("Apixaban", "5mg", "tablet", "oral", "twice daily", "AF/VTE"),
    ("Insulin Lantus", "10 units", "injection", "subcutaneous", "once daily", "Diabetes"),
    ("Prednisolone", "5mg", "tablet", "oral", "once daily", "Inflammation"),
    ("Codeine", "30mg", "tablet", "oral", "four times daily", "Pain"),
    ("Clopidogrel", "75mg", "tablet", "oral", "once daily", "Cardiovascular"),
]

# Lab test types
LAB_TESTS = [
    ("FBC-HB", "Haemoglobin", "g/L", 120, 160, 80, 200),
    ("FBC-WCC", "White Cell Count", "x10^9/L", 4.0, 11.0, 1.0, 30.0),
    ("FBC-PLT", "Platelet Count", "x10^9/L", 150, 400, 50, 800),
    ("UREA", "Urea", "mmol/L", 2.5, 6.7, 1.0, 40.0),
    ("CREAT", "Creatinine", "umol/L", 62, 106, 30, 800),
    ("EGFR", "eGFR", "mL/min/1.73m2", 60, 120, 5, 120),
    ("NA", "Sodium", "mmol/L", 136, 145, 120, 160),
    ("K", "Potassium", "mmol/L", 3.5, 5.1, 2.5, 7.0),
    ("ALT", "Alanine Aminotransferase", "U/L", 7, 56, 3, 500),
    ("ALP", "Alkaline Phosphatase", "U/L", 44, 147, 20, 800),
    ("BILI", "Bilirubin", "umol/L", 0, 21, 0, 200),
    ("CRP", "C-Reactive Protein", "mg/L", 0, 5, 0, 400),
    ("HBA1C", "HbA1c", "mmol/mol", 20, 42, 20, 120),
    ("TROP", "Troponin I", "ng/L", 0, 14, 0, 5000),
    ("TSH", "Thyroid Stimulating Hormone", "mU/L", 0.27, 4.2, 0.01, 50),
    ("CHOL", "Total Cholesterol", "mmol/L", 0, 5.0, 2.0, 12.0),
    ("BNP", "B-type Natriuretic Peptide", "pg/mL", 0, 100, 0, 5000),
    ("GLU", "Random Glucose", "mmol/L", 3.9, 5.6, 2.0, 30.0),
    ("INR", "International Normalised Ratio", "", 0.8, 1.2, 0.5, 8.0),
    ("DDIMER", "D-Dimer", "ng/mL", 0, 500, 0, 10000),
]

# Clinical note templates for NLP
CLINICAL_NOTE_TEMPLATES = [
    # Cardiology
    "Patient is a {age} year old {gender} presenting with {symptom}. "
    "Past medical history includes {pmh1} and {pmh2}. "
    "On examination, blood pressure was {bp}, heart rate {hr} bpm. "
    "ECG showed {ecg_finding}. Troponin was {trop_result}. "
    "Plan: {plan}. Started on {medication1} and {medication2}.",

    # Respiratory
    "This {age} year old {gender} was admitted with a {duration} day history of "
    "worsening {symptom}. Known history of {pmh1}. "
    "On arrival, oxygen saturations were {sats}% on room air. "
    "Chest X-ray showed {cxr_finding}. "
    "Started on {medication1}. Referred to respiratory team for review.",

    # General Medicine
    "{age} year old {gender} admitted via A&E with {symptom}. "
    "Background of {pmh1}, {pmh2}, and {pmh3}. "
    "Currently on {medication1}, {medication2}, and {medication3}. "
    "Observations: BP {bp}, HR {hr}, Temp {temp}C, SpO2 {sats}%. "
    "Blood results showed {lab_finding}. "
    "Working diagnosis: {diagnosis}. Plan: {plan}.",

    # Emergency
    "Emergency department attendance. {age} year old {gender}. "
    "Presenting complaint: {symptom} for {duration} days. "
    "Triage category: {triage}. "
    "No known drug allergies. PMH: {pmh1}. "
    "Assessment: {diagnosis}. {plan}. "
    "Discharge with GP follow-up in {followup} days.",

    # Oncology
    "Oncology clinic review. {age} year old {gender} with known {cancer_type}. "
    "Diagnosed {months_ago} months ago, currently on cycle {cycle} of {chemo_regime}. "
    "Tolerating treatment {tolerance}. "
    "Latest CT scan shows {scan_result}. "
    "Bloods: Hb {hb} g/L, WCC {wcc}, Plt {plt}. "
    "Plan: continue current regime. Next review in {followup} weeks.",

    # Elderly Care
    "Geriatric assessment for {age} year old {gender} following {event}. "
    "Lives {living_situation}. {mobility}. "
    "PMH: {pmh1}, {pmh2}, {pmh3}. "
    "AMTS score: {amts}/10. Barthel index: {barthel}/20. "
    "Referred to {referral} for ongoing support. "
    "Discharge planning initiated with social services.",

    # Diabetes
    "Diabetes clinic review. {age} year old {gender} with {diabetes_type}. "
    "Current HbA1c: {hba1c} mmol/mol (previous: {prev_hba1c} mmol/mol). "
    "Currently on {medication1} and {medication2}. "
    "Reports {hypo_frequency} hypoglycaemic episodes in last month. "
    "Foot examination: {foot_exam}. Retinal screening: {retinal}. "
    "Plan: {plan}.",
]

# NLP-relevant terms
SYMPTOMS = [
    "chest pain", "shortness of breath", "palpitations", "dizziness",
    "severe headache", "abdominal pain", "nausea and vomiting",
    "productive cough", "haemoptysis", "fever and rigors",
    "confusion", "falls", "leg swelling", "urinary symptoms",
    "weight loss", "fatigue", "back pain", "joint pain",
]

ECG_FINDINGS = [
    "sinus rhythm", "atrial fibrillation", "ST elevation in leads V1-V4",
    "ST depression in lateral leads", "left bundle branch block",
    "right bundle branch block", "first degree heart block",
    "normal sinus rhythm with no acute changes",
    "sinus tachycardia", "ventricular ectopics",
]

CXR_FINDINGS = [
    "bilateral consolidation", "right lower lobe pneumonia",
    "left pleural effusion", "clear lung fields",
    "cardiomegaly", "hyperinflated lungs consistent with COPD",
    "no acute abnormality", "patchy atelectasis at the bases",
]

PLANS = [
    "Admit for monitoring and serial troponins",
    "Commence IV antibiotics and fluids",
    "Refer to cardiology for urgent review",
    "CT pulmonary angiogram to exclude PE",
    "Start on LMWH and arrange echocardiogram",
    "Discharge with GP follow-up in 7 days",
    "Refer to respiratory team for bronchoscopy",
    "MRI brain to exclude acute pathology",
    "Titrate up medications as tolerated",
    "Surgical review for possible intervention",
    "Palliative care team referral for symptom management",
    "Physiotherapy assessment and rehabilitation",
]


# ============================================
# GENERATOR FUNCTIONS
# ============================================

def generate_nhs_number() -> str:
    """Generate a realistic NHS number (10 digits)."""
    return "".join([str(random.randint(0, 9)) for _ in range(10)])


def generate_patients(n: int = 2000) -> list[dict]:
    """Generate synthetic patient demographics."""
    patients = []
    used_nhs_numbers = set()

    for _ in range(n):
        # Ensure unique NHS numbers
        nhs_number = generate_nhs_number()
        while nhs_number in used_nhs_numbers:
            nhs_number = generate_nhs_number()
        used_nhs_numbers.add(nhs_number)

        # Generate demographics
        gender = random.choice(["Male", "Female"])
        dob = fake.date_of_birth(minimum_age=18, maximum_age=95)
        date_of_death = None

        # ~5% of patients are deceased
        if random.random() < 0.05:
            death_offset = random.randint(1, 365 * 3)
            potential_death = datetime.now().date() - timedelta(days=random.randint(1, death_offset))
            if potential_death > dob:
                date_of_death = potential_death.isoformat()

        gp_practice = random.choice(GP_PRACTICES)

        patients.append({
            "nhs_number": nhs_number,
            "patient_id": str(uuid.uuid4()),
            "gender": gender,
            "date_of_birth": dob.isoformat(),
            "date_of_death": date_of_death,
            "ethnicity_code": random.choice(ETHNICITY_CODES),
            "postcode": fake.postcode(),
            "lsoa_code": f"E0100{random.randint(1000, 9999)}",
            "gp_practice_code": gp_practice[0],
            "gp_practice_name": gp_practice[1],
            "registered_date": fake.date_between(
                start_date="-10y", end_date="-1y"
            ).isoformat(),
            "is_active": "Y" if date_of_death is None else "N",
            "created_at": datetime.now().isoformat(),
        })

    return patients


def generate_episodes(patients: list[dict], avg_per_patient: float = 2.5) -> list[dict]:
    """Generate synthetic hospital episodes (SUS/HES format)."""
    episodes = []
    episode_id = 100000

    for patient in patients:
        # Skip deceased patients for new episodes sometimes
        if patient["date_of_death"] and random.random() < 0.5:
            continue

        n_episodes = max(1, int(random.gauss(avg_per_patient, 1.5)))

        for _ in range(n_episodes):
            episode_id += 1
            trust = random.choice(LONDON_TRUSTS)
            specialty = random.choice(SPECIALTIES)
            admission_method = random.choices(
                ADMISSION_METHODS,
                weights=[5, 3, 2, 30, 15, 3, 2, 1, 1],
                k=1,
            )[0]

            # Generate dates
            admission_date = fake.date_between(
                start_date="-3y", end_date="today"
            )

            # Length of stay based on admission type
            if admission_method[0].startswith("2"):  # Emergency
                los = max(0, int(random.gauss(5, 4)))
            elif admission_method[0].startswith("1"):  # Elective
                los = max(0, int(random.gauss(3, 2)))
            else:
                los = max(0, int(random.gauss(4, 3)))

            discharge_date = admission_date + timedelta(days=los)

            # Discharge method
            if random.random() < 0.02:  # 2% mortality
                discharge_method = ("4", "Died")
                discharge_destination = ("79", "Not applicable - patient died or stillbirth")
            else:
                discharge_method = random.choices(
                    DISCHARGE_METHODS[:2],
                    weights=[95, 5],
                    k=1,
                )[0]
                discharge_destination = random.choices(
                    [d for d in DISCHARGE_DESTINATIONS if d[0] not in ("79",)],
                    weights=[60, 5, 1, 1, 1, 3, 2, 1, 5, 3, 1, 2],
                    k=1,
                )[0]

            episodes.append({
                "episode_id": f"EP{episode_id}",
                "patient_id": patient["patient_id"],
                "nhs_number": patient["nhs_number"],
                "trust_code": trust[0],
                "trust_name": trust[1],
                "specialty_code": specialty[0],
                "specialty_name": specialty[1],
                "admission_date": admission_date.isoformat(),
                "discharge_date": discharge_date.isoformat(),
                "length_of_stay": los,
                "admission_method_code": admission_method[0],
                "admission_method": admission_method[1],
                "discharge_method_code": discharge_method[0],
                "discharge_method": discharge_method[1],
                "discharge_destination_code": discharge_destination[0],
                "discharge_destination": discharge_destination[1],
                "ward": random.choice(WARD_TYPES),
                "bed_days": los,
                "spell_id": f"SP{episode_id}",
                "created_at": datetime.now().isoformat(),
            })

    return episodes


def generate_diagnoses(episodes: list[dict]) -> list[dict]:
    """Generate ICD-10 diagnoses for episodes."""
    diagnoses = []
    codes = [c[0] for c in ICD10_CODES_WEIGHTED]
    weights = [c[1] for c in ICD10_CODES_WEIGHTED]

    for episode in episodes:
        # Primary diagnosis
        primary_code = random.choices(codes, weights=weights, k=1)[0]
        diagnoses.append({
            "diagnosis_id": str(uuid.uuid4()),
            "episode_id": episode["episode_id"],
            "patient_id": episode["patient_id"],
            "diagnosis_code": primary_code,
            "diagnosis_sequence": 1,
            "diagnosis_type": "primary",
            "coding_date": episode["admission_date"],
            "created_at": datetime.now().isoformat(),
        })

        # Secondary diagnoses (0-4)
        n_secondary = random.choices([0, 1, 2, 3, 4], weights=[20, 30, 25, 15, 10], k=1)[0]
        used_codes = {primary_code}

        for seq in range(2, 2 + n_secondary):
            secondary_code = random.choices(codes, weights=weights, k=1)[0]
            while secondary_code in used_codes:
                secondary_code = random.choices(codes, weights=weights, k=1)[0]
            used_codes.add(secondary_code)

            diagnoses.append({
                "diagnosis_id": str(uuid.uuid4()),
                "episode_id": episode["episode_id"],
                "patient_id": episode["patient_id"],
                "diagnosis_code": secondary_code,
                "diagnosis_sequence": seq,
                "diagnosis_type": "secondary",
                "coding_date": episode["admission_date"],
                "created_at": datetime.now().isoformat(),
            })

    return diagnoses


def generate_procedures(episodes: list[dict]) -> list[dict]:
    """Generate OPCS-4 procedures for episodes."""
    procedures = []

    for episode in episodes:
        # ~40% of episodes have a procedure
        if random.random() < 0.4:
            n_procedures = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0]

            for seq in range(1, n_procedures + 1):
                proc_date = datetime.fromisoformat(episode["admission_date"]) + timedelta(
                    days=random.randint(0, max(1, episode["length_of_stay"]))
                )

                procedures.append({
                    "procedure_id": str(uuid.uuid4()),
                    "episode_id": episode["episode_id"],
                    "patient_id": episode["patient_id"],
                    "procedure_code": random.choice(OPCS4_CODES),
                    "procedure_sequence": seq,
                    "procedure_date": proc_date.date().isoformat(),
                    "created_at": datetime.now().isoformat(),
                })

    return procedures


def generate_medications(patients: list[dict]) -> list[dict]:
    """Generate medication prescriptions."""
    medications_list = []

    for patient in patients:
        # Each patient has 0-8 medications
        n_meds = random.choices(
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            weights=[5, 10, 15, 20, 20, 15, 8, 5, 2],
            k=1,
        )[0]

        selected_meds = random.sample(MEDICATIONS, min(n_meds, len(MEDICATIONS)))

        for med in selected_meds:
            start_date = fake.date_between(start_date="-3y", end_date="today")

            # ~30% of medications have been stopped
            end_date = None
            status = "active"
            if random.random() < 0.3:
                end_date = (start_date + timedelta(days=random.randint(7, 365))).isoformat()
                status = "stopped"

            medications_list.append({
                "medication_id": str(uuid.uuid4()),
                "patient_id": patient["patient_id"],
                "nhs_number": patient["nhs_number"],
                "medication_name": med[0],
                "dose": med[1],
                "form": med[2],
                "route": med[3],
                "frequency": med[4],
                "indication": med[5],
                "prescribed_date": start_date.isoformat(),
                "end_date": end_date,
                "status": status,
                "prescriber_type": random.choice(["GP", "Hospital Doctor", "Nurse Prescriber"]),
                "created_at": datetime.now().isoformat(),
            })

    return medications_list


def generate_observations(episodes: list[dict]) -> list[dict]:
    """Generate lab results and observations."""
    observations = []

    for episode in episodes:
        # Each episode generates some lab results
        n_tests = random.randint(3, 12)
        selected_tests = random.sample(LAB_TESTS, min(n_tests, len(LAB_TESTS)))

        for test in selected_tests:
            test_code, test_name, unit, normal_low, normal_high, abs_low, abs_high = test

            # 70% normal, 30% abnormal
            if random.random() < 0.7:
                value = round(random.uniform(normal_low, normal_high), 1)
            else:
                value = round(random.uniform(abs_low, abs_high), 1)

            # Determine if abnormal
            is_abnormal = value < normal_low or value > normal_high

            test_date = datetime.fromisoformat(episode["admission_date"]) + timedelta(
                hours=random.randint(0, max(1, episode["length_of_stay"] * 24))
            )

            observations.append({
                "observation_id": str(uuid.uuid4()),
                "episode_id": episode["episode_id"],
                "patient_id": episode["patient_id"],
                "test_code": test_code,
                "test_name": test_name,
                "value": value,
                "unit": unit,
                "reference_range_low": normal_low,
                "reference_range_high": normal_high,
                "is_abnormal": is_abnormal,
                "observation_date": test_date.date().isoformat(),
                "observation_datetime": test_date.isoformat(),
                "created_at": datetime.now().isoformat(),
            })

    return observations


def generate_clinical_notes(episodes: list[dict], patients: list[dict]) -> list[dict]:
    """Generate unstructured clinical notes for NLP processing."""
    notes = []
    patient_lookup = {p["patient_id"]: p for p in patients}

    for episode in episodes:
        # ~60% of episodes have a clinical note
        if random.random() > 0.6:
            continue

        patient = patient_lookup.get(episode["patient_id"], {})
        dob = datetime.fromisoformat(patient.get("date_of_birth", "1970-01-01"))
        admission = datetime.fromisoformat(episode["admission_date"])
        age = (admission - dob).days // 365
        gender = patient.get("gender", "Male")

        # Pick a random template and fill it
        template = random.choice(CLINICAL_NOTE_TEMPLATES)

        # Common medications for filling templates
        med_names = [m[0] for m in MEDICATIONS]
        pmh_conditions = [
            "hypertension", "type 2 diabetes", "COPD", "asthma",
            "atrial fibrillation", "heart failure", "ischaemic heart disease",
            "chronic kidney disease", "osteoarthritis", "depression",
            "hypothyroidism", "hyperlipidaemia", "anxiety disorder",
            "previous stroke", "previous MI", "rheumatoid arthritis",
        ]

        # Build replacement values
        replacements = {
            "age": str(age),
            "gender": gender.lower(),
            "symptom": random.choice(SYMPTOMS),
            "pmh1": random.choice(pmh_conditions),
            "pmh2": random.choice(pmh_conditions),
            "pmh3": random.choice(pmh_conditions),
            "medication1": random.choice(med_names),
            "medication2": random.choice(med_names),
            "medication3": random.choice(med_names),
            "bp": f"{random.randint(100, 180)}/{random.randint(60, 100)}",
            "hr": str(random.randint(55, 120)),
            "temp": f"{round(random.uniform(36.0, 39.5), 1)}",
            "sats": str(random.randint(88, 100)),
            "duration": str(random.randint(1, 14)),
            "ecg_finding": random.choice(ECG_FINDINGS),
            "cxr_finding": random.choice(CXR_FINDINGS),
            "trop_result": f"{random.randint(1, 500)} ng/L",
            "plan": random.choice(PLANS),
            "diagnosis": random.choice(pmh_conditions),
            "triage": random.choice(["1 - Immediate", "2 - Very Urgent", "3 - Urgent", "4 - Standard"]),
            "followup": str(random.randint(2, 28)),
            "cancer_type": random.choice(["breast cancer", "lung cancer", "colorectal cancer", "prostate cancer"]),
            "months_ago": str(random.randint(1, 24)),
            "cycle": str(random.randint(1, 8)),
            "chemo_regime": random.choice(["FOLFOX", "CAPOX", "FEC-T", "carboplatin/pemetrexed", "docetaxel"]),
            "tolerance": random.choice(["well", "with mild nausea", "with significant fatigue", "poorly"]),
            "scan_result": random.choice([
                "stable disease", "partial response", "progressive disease",
                "complete response", "mixed response",
            ]),
            "hb": str(random.randint(80, 160)),
            "wcc": f"{round(random.uniform(2.0, 15.0), 1)}",
            "plt": str(random.randint(100, 400)),
            "lab_finding": random.choice([
                "elevated CRP at 85 mg/L",
                "raised troponin at 250 ng/L",
                "acute kidney injury with creatinine 180 umol/L",
                "low haemoglobin at 95 g/L",
                "deranged liver function tests",
                "HbA1c 68 mmol/mol indicating poor diabetic control",
                "raised white cell count at 15.2 x10^9/L suggesting infection",
                "normal blood results",
            ]),
            "event": random.choice(["a fall at home", "a collapse", "found on floor by carer", "a hip fracture"]),
            "living_situation": random.choice([
                "alone in a flat", "with spouse", "in a care home",
                "with family", "in sheltered accommodation",
            ]),
            "mobility": random.choice([
                "Normally independent with a walking stick",
                "Uses a zimmer frame",
                "Wheelchair dependent",
                "Fully mobile and independent",
                "Bedbound prior to admission",
            ]),
            "amts": str(random.randint(3, 10)),
            "barthel": str(random.randint(5, 20)),
            "referral": random.choice([
                "physiotherapy", "occupational therapy", "social services",
                "falls clinic", "memory clinic", "district nursing",
            ]),
            "diabetes_type": random.choice(["type 1 diabetes", "type 2 diabetes"]),
            "hba1c": str(random.randint(42, 100)),
            "prev_hba1c": str(random.randint(42, 100)),
            "hypo_frequency": random.choice(["no", "1-2", "3-4", "frequent"]),
            "foot_exam": random.choice([
                "normal sensation bilaterally",
                "reduced sensation in right foot",
                "monofilament testing abnormal bilaterally",
                "previous amputation left 5th toe",
            ]),
            "retinal": random.choice([
                "no retinopathy", "background retinopathy",
                "pre-proliferative retinopathy", "not yet screened this year",
            ]),
        }

        # Fill template with available replacements
        note_text = template
        for key, value in replacements.items():
            note_text = note_text.replace("{" + key + "}", value)

        note_date = admission + timedelta(hours=random.randint(1, 48))

        notes.append({
            "note_id": str(uuid.uuid4()),
            "episode_id": episode["episode_id"],
            "patient_id": episode["patient_id"],
            "note_type": random.choice([
                "Admission Note",
                "Discharge Summary",
                "Clinical Review",
                "Outpatient Letter",
                "A&E Attendance",
            ]),
            "note_date": note_date.date().isoformat(),
            "note_datetime": note_date.isoformat(),
            "note_text": note_text,
            "author_role": random.choice([
                "Consultant", "Registrar", "SHO",
                "FY1", "FY2", "Nurse Practitioner",
            ]),
            "specialty": episode["specialty_name"],
            "created_at": datetime.now().isoformat(),
        })

    return notes


def write_csv(data: list[dict], filepath: Path) -> None:
    """Write a list of dicts to CSV."""
    if not data:
        print(f"⚠️  No data to write for {filepath.name}")
        return

    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Generated {filepath.name}: {len(data):,} rows")


# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Generate all synthetic NHS data."""
    print("=" * 60)
    print("NHS Synthetic Data Generator")
    print("=" * 60)
    print()

    # Generate patients
    print("👤 Generating patients...")
    patients = generate_patients(n=2000)
    write_csv(patients, RAW_DATA_DIR / "patients.csv")

    # Generate episodes
    print("🏥 Generating hospital episodes...")
    episodes = generate_episodes(patients, avg_per_patient=2.5)
    write_csv(episodes, RAW_DATA_DIR / "episodes.csv")

    # Generate diagnoses
    print("🩺 Generating diagnoses...")
    diagnoses = generate_diagnoses(episodes)
    write_csv(diagnoses, RAW_DATA_DIR / "diagnoses.csv")

    # Generate procedures
    print("💊 Generating procedures...")
    procedures = generate_procedures(episodes)
    write_csv(procedures, RAW_DATA_DIR / "procedures.csv")

    # Generate medications
    print("💉 Generating medications...")
    medications = generate_medications(patients)
    write_csv(medications, RAW_DATA_DIR / "medications.csv")

    # Generate observations
    print("🔬 Generating lab results...")
    observations = generate_observations(episodes)
    write_csv(observations, RAW_DATA_DIR / "observations.csv")

    # Generate clinical notes
    print("📝 Generating clinical notes...")
    clinical_notes = generate_clinical_notes(episodes, patients)
    write_csv(clinical_notes, RAW_DATA_DIR / "clinical_notes.csv")

    # Summary
    print()
    print("=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"  Patients:       {len(patients):,}")
    print(f"  Episodes:       {len(episodes):,}")
    print(f"  Diagnoses:      {len(diagnoses):,}")
    print(f"  Procedures:     {len(procedures):,}")
    print(f"  Medications:    {len(medications):,}")
    print(f"  Observations:   {len(observations):,}")
    print(f"  Clinical Notes: {len(clinical_notes):,}")
    print(f"  Output dir:     {RAW_DATA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()