"""
NHS Data Pipeline - Clinical Entity Definitions
=================================================
Defines clinical entities, patterns, and mappings for NLP extraction.
Based on NHS clinical terminology standards (SNOMED-CT, ICD-10).
"""

# ============================================
# CONDITION PATTERNS
# Maps clinical text mentions to SNOMED/ICD-10
# ============================================

CONDITION_PATTERNS = {
    # Cardiovascular
    "hypertension": {
        "patterns": [
            "hypertension", "high blood pressure", "elevated blood pressure",
            "htn", "hypertensive",
        ],
        "snomed_code": "38341003",
        "snomed_term": "Hypertensive disorder",
        "icd10_code": "I10",
        "category": "Cardiovascular",
    },
    "type 2 diabetes": {
        "patterns": [
            "type 2 diabetes", "type ii diabetes", "t2dm", "type 2 dm",
            "diabetes mellitus type 2", "non-insulin dependent diabetes",
            "diabetes", "diabetic",
        ],
        "snomed_code": "44054006",
        "snomed_term": "Type 2 diabetes mellitus",
        "icd10_code": "E11.9",
        "category": "Endocrine",
    },
    "type 1 diabetes": {
        "patterns": [
            "type 1 diabetes", "type i diabetes", "t1dm", "type 1 dm",
            "insulin dependent diabetes",
        ],
        "snomed_code": "46635009",
        "snomed_term": "Type 1 diabetes mellitus",
        "icd10_code": "E10.9",
        "category": "Endocrine",
    },
    "heart failure": {
        "patterns": [
            "heart failure", "cardiac failure", "congestive heart failure",
            "chf", "hf", "left ventricular failure", "lvf",
        ],
        "snomed_code": "84114007",
        "snomed_term": "Heart failure",
        "icd10_code": "I50.0",
        "category": "Cardiovascular",
    },
    "myocardial infarction": {
        "patterns": [
            "myocardial infarction", "heart attack", "mi", "stemi",
            "nstemi", "acute coronary syndrome", "acs",
            "previous mi", "previous myocardial infarction",
        ],
        "snomed_code": "22298006",
        "snomed_term": "Myocardial infarction",
        "icd10_code": "I21.9",
        "category": "Cardiovascular",
    },
    "atrial fibrillation": {
        "patterns": [
            "atrial fibrillation", "af", "a-fib", "afib",
            "paroxysmal af", "persistent af", "permanent af",
        ],
        "snomed_code": "49436004",
        "snomed_term": "Atrial fibrillation",
        "icd10_code": "I48.9",
        "category": "Cardiovascular",
    },
    "ischaemic heart disease": {
        "patterns": [
            "ischaemic heart disease", "ischemic heart disease",
            "ihd", "coronary artery disease", "cad",
            "angina", "coronary heart disease",
        ],
        "snomed_code": "414545008",
        "snomed_term": "Ischaemic heart disease",
        "icd10_code": "I25.1",
        "category": "Cardiovascular",
    },
    "stroke": {
        "patterns": [
            "stroke", "cerebrovascular accident", "cva",
            "cerebral infarction", "previous stroke",
        ],
        "snomed_code": "230690007",
        "snomed_term": "Cerebrovascular accident",
        "icd10_code": "I64",
        "category": "Cardiovascular",
    },

    # Respiratory
    "copd": {
        "patterns": [
            "copd", "chronic obstructive pulmonary disease",
            "chronic obstructive lung disease", "emphysema",
            "chronic bronchitis",
        ],
        "snomed_code": "13645005",
        "snomed_term": "Chronic obstructive lung disease",
        "icd10_code": "J44.1",
        "category": "Respiratory",
    },
    "asthma": {
        "patterns": [
            "asthma", "asthmatic", "bronchial asthma",
        ],
        "snomed_code": "195967001",
        "snomed_term": "Asthma",
        "icd10_code": "J45.9",
        "category": "Respiratory",
    },
    "pneumonia": {
        "patterns": [
            "pneumonia", "chest infection", "lower respiratory tract infection",
            "lrti", "community acquired pneumonia", "cap",
            "hospital acquired pneumonia", "hap",
        ],
        "snomed_code": "233604007",
        "snomed_term": "Pneumonia",
        "icd10_code": "J18.1",
        "category": "Respiratory",
    },

    # Mental Health
    "depression": {
        "patterns": [
            "depression", "depressive disorder", "depressive episode",
            "low mood", "depressed mood",
        ],
        "snomed_code": "35489007",
        "snomed_term": "Depressive disorder",
        "icd10_code": "F32.1",
        "category": "Mental Health",
    },
    "anxiety disorder": {
        "patterns": [
            "anxiety", "anxiety disorder", "generalised anxiety",
            "generalized anxiety", "gad", "anxious",
        ],
        "snomed_code": "197480006",
        "snomed_term": "Anxiety disorder",
        "icd10_code": "F41.1",
        "category": "Mental Health",
    },

    # Renal
    "chronic kidney disease": {
        "patterns": [
            "chronic kidney disease", "ckd", "renal impairment",
            "kidney disease", "renal failure",
        ],
        "snomed_code": "90708001",
        "snomed_term": "Kidney disease",
        "icd10_code": "N18.3",
        "category": "Renal",
    },
    "urinary tract infection": {
        "patterns": [
            "urinary tract infection", "uti", "urine infection",
            "urinary infection",
        ],
        "snomed_code": "68566005",
        "snomed_term": "Urinary tract infection",
        "icd10_code": "N39.0",
        "category": "Infectious",
    },

    # Other
    "hyperlipidaemia": {
        "patterns": [
            "hyperlipidaemia", "hyperlipidemia", "hypercholesterolaemia",
            "hypercholesterolemia", "high cholesterol", "raised cholesterol",
        ],
        "snomed_code": "55822004",
        "snomed_term": "Hyperlipidemia",
        "icd10_code": "E78.0",
        "category": "Endocrine",
    },
    "hypothyroidism": {
        "patterns": [
            "hypothyroidism", "hypothyroid", "underactive thyroid",
        ],
        "snomed_code": "40930008",
        "snomed_term": "Hypothyroidism",
        "icd10_code": "E03.9",
        "category": "Endocrine",
    },
    "osteoarthritis": {
        "patterns": [
            "osteoarthritis", "oa", "degenerative joint disease",
            "arthritis",
        ],
        "snomed_code": "396275006",
        "snomed_term": "Osteoarthritis",
        "icd10_code": "M17.1",
        "category": "Musculoskeletal",
    },
    "rheumatoid arthritis": {
        "patterns": [
            "rheumatoid arthritis", "ra", "rheumatoid",
        ],
        "snomed_code": "69896004",
        "snomed_term": "Rheumatoid arthritis",
        "icd10_code": "M06.9",
        "category": "Musculoskeletal",
    },
    "alzheimers": {
        "patterns": [
            "alzheimers", "alzheimer's", "alzheimer disease",
            "dementia",
        ],
        "snomed_code": "26929004",
        "snomed_term": "Alzheimer disease",
        "icd10_code": "G30.9",
        "category": "Neurological",
    },
}

# ============================================
# MEDICATION PATTERNS
# ============================================

MEDICATION_PATTERNS = {
    "metformin": {
        "patterns": ["metformin"],
        "rxnorm_code": "1503297",
        "category": "Diabetes",
    },
    "amlodipine": {
        "patterns": ["amlodipine"],
        "rxnorm_code": "1332418",
        "category": "Cardiovascular",
    },
    "ramipril": {
        "patterns": ["ramipril"],
        "rxnorm_code": "1334456",
        "category": "Cardiovascular",
    },
    "bisoprolol": {
        "patterns": ["bisoprolol"],
        "rxnorm_code": "1338005",
        "category": "Cardiovascular",
    },
    "atorvastatin": {
        "patterns": ["atorvastatin"],
        "rxnorm_code": "1545958",
        "category": "Cardiovascular",
    },
    "salbutamol": {
        "patterns": ["salbutamol", "ventolin"],
        "rxnorm_code": "1154070",
        "category": "Respiratory",
    },
    "omeprazole": {
        "patterns": ["omeprazole"],
        "rxnorm_code": "948078",
        "category": "Gastrointestinal",
    },
    "levothyroxine": {
        "patterns": ["levothyroxine"],
        "rxnorm_code": "1501700",
        "category": "Endocrine",
    },
    "warfarin": {
        "patterns": ["warfarin"],
        "rxnorm_code": "1310149",
        "category": "Anticoagulant",
    },
    "paracetamol": {
        "patterns": ["paracetamol", "acetaminophen"],
        "rxnorm_code": "1125315",
        "category": "Pain Relief",
    },
    "co-codamol": {
        "patterns": ["co-codamol", "cocodamol"],
        "rxnorm_code": "1201620",
        "category": "Pain Relief",
    },
    "amoxicillin": {
        "patterns": ["amoxicillin", "amoxycillin"],
        "rxnorm_code": "1713332",
        "category": "Anti-infective",
    },
    "doxycycline": {
        "patterns": ["doxycycline"],
        "rxnorm_code": "1738521",
        "category": "Anti-infective",
    },
    "furosemide": {
        "patterns": ["furosemide", "frusemide"],
        "rxnorm_code": "956874",
        "category": "Diuretic",
    },
    "sertraline": {
        "patterns": ["sertraline"],
        "rxnorm_code": "739138",
        "category": "Mental Health",
    },
    "apixaban": {
        "patterns": ["apixaban"],
        "rxnorm_code": "43013024",
        "category": "Anticoagulant",
    },
    "insulin": {
        "patterns": ["insulin", "insulin lantus", "insulin glargine"],
        "rxnorm_code": "46275076",
        "category": "Diabetes",
    },
    "prednisolone": {
        "patterns": ["prednisolone", "prednisone"],
        "rxnorm_code": "1551099",
        "category": "Anti-inflammatory",
    },
    "codeine": {
        "patterns": ["codeine"],
        "rxnorm_code": "1201620",
        "category": "Pain Relief",
    },
    "clopidogrel": {
        "patterns": ["clopidogrel"],
        "rxnorm_code": "1322184",
        "category": "Cardiovascular",
    },
    "lmwh": {
        "patterns": ["lmwh", "enoxaparin", "dalteparin", "tinzaparin"],
        "rxnorm_code": "0",
        "category": "Anticoagulant",
    },
}

# ============================================
# SYMPTOM PATTERNS
# ============================================

SYMPTOM_PATTERNS = {
    "chest pain": {
        "patterns": ["chest pain", "chest tightness", "central chest pain"],
        "snomed_code": "29857009",
        "snomed_term": "Chest pain",
    },
    "shortness of breath": {
        "patterns": [
            "shortness of breath", "breathlessness", "dyspnoea",
            "dyspnea", "sob", "difficulty breathing",
        ],
        "snomed_code": "267036007",
        "snomed_term": "Dyspnoea",
    },
    "palpitations": {
        "patterns": ["palpitations", "palpitation", "racing heart"],
        "snomed_code": "80313002",
        "snomed_term": "Palpitations",
    },
    "fever": {
        "patterns": ["fever", "pyrexia", "febrile", "temperature", "rigors"],
        "snomed_code": "386661006",
        "snomed_term": "Fever",
    },
    "cough": {
        "patterns": [
            "cough", "productive cough", "dry cough",
            "worsening cough", "chronic cough",
        ],
        "snomed_code": "49727002",
        "snomed_term": "Cough",
    },
    "abdominal pain": {
        "patterns": [
            "abdominal pain", "stomach pain", "epigastric pain",
            "right upper quadrant pain", "ruq pain",
        ],
        "snomed_code": "21522001",
        "snomed_term": "Abdominal pain",
    },
    "nausea": {
        "patterns": ["nausea", "nausea and vomiting", "vomiting", "emesis"],
        "snomed_code": "422587007",
        "snomed_term": "Nausea and vomiting",
    },
    "headache": {
        "patterns": ["headache", "head pain", "severe headache", "migraine"],
        "snomed_code": "25064002",
        "snomed_term": "Headache",
    },
    "dizziness": {
        "patterns": ["dizziness", "dizzy", "vertigo", "lightheaded"],
        "snomed_code": "404640003",
        "snomed_term": "Dizziness",
    },
    "confusion": {
        "patterns": ["confusion", "confused", "delirium", "altered mental state"],
        "snomed_code": "40917007",
        "snomed_term": "Confusion",
    },
    "fatigue": {
        "patterns": ["fatigue", "tiredness", "lethargy", "malaise"],
        "snomed_code": "84229001",
        "snomed_term": "Fatigue",
    },
    "falls": {
        "patterns": ["fall", "falls", "fallen", "collapse", "collapsed"],
        "snomed_code": "161898004",
        "snomed_term": "Falls",
    },
    "leg swelling": {
        "patterns": ["leg swelling", "ankle swelling", "peripheral oedema", "edema"],
        "snomed_code": "102572006",
        "snomed_term": "Peripheral oedema",
    },
    "weight loss": {
        "patterns": ["weight loss", "losing weight", "unintentional weight loss"],
        "snomed_code": "89362005",
        "snomed_term": "Weight loss",
    },
    "haemoptysis": {
        "patterns": ["haemoptysis", "hemoptysis", "coughing blood", "blood in sputum"],
        "snomed_code": "66857006",
        "snomed_term": "Haemoptysis",
    },
    "back pain": {
        "patterns": ["back pain", "low back pain", "lower back pain", "lbp"],
        "snomed_code": "161891005",
        "snomed_term": "Back pain",
    },
}

# ============================================
# NEGATION CUES
# Words that negate a clinical finding
# ============================================

NEGATION_CUES = [
    "no ", "no evidence of", "not ", "denies", "denied",
    "negative for", "without", "absence of", "ruled out",
    "unlikely", "not consistent with", "no signs of",
    "no symptoms of", "non-", "never had",
]