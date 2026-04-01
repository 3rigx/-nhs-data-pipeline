"""
NHS Data Pipeline - Clinical Named Entity Recognition
======================================================
Extracts clinical entities (conditions, medications, symptoms)
from unstructured NHS clinical notes using spaCy + rule-based matching.
"""

import re
import uuid
from datetime import datetime

import spacy
from spacy.matcher import PhraseMatcher

from src.nlp.clinical_entities import (
    CONDITION_PATTERNS,
    MEDICATION_PATTERNS,
    SYMPTOM_PATTERNS,
    NEGATION_CUES,
)


class ClinicalNER:
    """
    Clinical Named Entity Recognition engine.

    Uses spaCy for tokenization and a rule-based approach for
    entity extraction from NHS clinical notes.

    Approach:
    1. spaCy tokenizes and processes the text
    2. PhraseMatcher identifies clinical entities
    3. Negation detection filters false positives
    4. Entities are mapped to SNOMED-CT / ICD-10 / RxNorm codes
    """

    def __init__(self):
        """Initialize the NLP engine."""
        print("🧠 Initializing Clinical NER engine...")

        # Load spaCy English model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("📥 Downloading spaCy English model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        # Initialize phrase matchers
        self.condition_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.medication_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.symptom_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # Load patterns
        self._load_patterns()
        print("✅ Clinical NER engine ready")

    def _load_patterns(self):
        """Load all clinical patterns into matchers."""
        # Load condition patterns
        for name, config in CONDITION_PATTERNS.items():
            patterns = [self.nlp.make_doc(p) for p in config["patterns"]]
            self.condition_matcher.add(name, patterns)

        # Load medication patterns
        for name, config in MEDICATION_PATTERNS.items():
            patterns = [self.nlp.make_doc(p) for p in config["patterns"]]
            self.medication_matcher.add(name, patterns)

        # Load symptom patterns
        for name, config in SYMPTOM_PATTERNS.items():
            patterns = [self.nlp.make_doc(p) for p in config["patterns"]]
            self.symptom_matcher.add(name, patterns)

        print(
            f"   Loaded: {len(CONDITION_PATTERNS)} conditions, "
            f"{len(MEDICATION_PATTERNS)} medications, "
            f"{len(SYMPTOM_PATTERNS)} symptoms"
        )

    def _is_negated(self, text: str, entity_start: int, window: int = 50) -> bool:
        """
        Check if an entity mention is negated.

        Looks for negation cues in a window before the entity.
        E.g., "no chest pain" → chest pain is negated.
        """
        # Get text window before the entity
        start = max(0, entity_start - window)
        preceding_text = text[start:entity_start].lower()

        for cue in NEGATION_CUES:
            if cue in preceding_text:
                return True
        return False

    def _extract_vitals(self, text: str) -> list[dict]:
        """Extract vital signs from clinical text using regex."""
        vitals = []

        # Blood pressure: e.g., "BP 120/80" or "blood pressure was 140/90"
        bp_pattern = r'(?:bp|blood pressure)[:\s]+(\d{2,3})[/\\](\d{2,3})'
        for match in re.finditer(bp_pattern, text.lower()):
            vitals.append({
                "entity_type": "vital_sign",
                "entity_name": "blood_pressure_systolic",
                "value": match.group(1),
                "unit": "mmHg",
            })
            vitals.append({
                "entity_type": "vital_sign",
                "entity_name": "blood_pressure_diastolic",
                "value": match.group(2),
                "unit": "mmHg",
            })

        # Heart rate: e.g., "HR 80" or "heart rate 72 bpm"
        hr_pattern = r'(?:hr|heart rate)[:\s]+(\d{2,3})\s*(?:bpm)?'
        for match in re.finditer(hr_pattern, text.lower()):
            vitals.append({
                "entity_type": "vital_sign",
                "entity_name": "heart_rate",
                "value": match.group(1),
                "unit": "bpm",
            })

        # Temperature: e.g., "Temp 37.5C" or "temperature 38.2"
        temp_pattern = r'(?:temp|temperature)[:\s]+(\d{2}\.?\d?)\s*(?:c|°c)?'
        for match in re.finditer(temp_pattern, text.lower()):
            vitals.append({
                "entity_type": "vital_sign",
                "entity_name": "temperature",
                "value": match.group(1),
                "unit": "°C",
            })

        # Oxygen saturation: e.g., "SpO2 95%" or "saturations were 92%"
        sats_pattern = r'(?:spo2|sats|saturations?|oxygen saturations?)[:\s]+(\d{2,3})\s*%'
        for match in re.finditer(sats_pattern, text.lower()):
            vitals.append({
                "entity_type": "vital_sign",
                "entity_name": "oxygen_saturation",
                "value": match.group(1),
                "unit": "%",
            })

        return vitals

    def _extract_demographics(self, text: str) -> dict:
        """Extract age and gender from clinical text."""
        demographics = {}

        # Age: e.g., "72 year old" or "aged 65"
        age_pattern = r'(\d{1,3})\s*(?:year|yr)[\s-]*old'
        age_match = re.search(age_pattern, text.lower())
        if age_match:
            demographics["age_mentioned"] = int(age_match.group(1))

        # Gender from text
        text_lower = text.lower()
        if any(w in text_lower for w in ["male", " man ", " gentleman "]):
            demographics["gender_mentioned"] = "Male"
        elif any(w in text_lower for w in ["female", " woman ", " lady "]):
            demographics["gender_mentioned"] = "Female"

        return demographics

    def process_note(self, note_id: str, note_text: str) -> list[dict]:
        """
        Process a single clinical note and extract all entities.

        Args:
            note_id: Unique identifier for the note
            note_text: Raw clinical note text

        Returns:
            List of extracted entity dictionaries
        """
        entities = []
        doc = self.nlp(note_text)
        now = datetime.now().isoformat()

        # Extract conditions
        condition_matches = self.condition_matcher(doc)
        seen_conditions = set()

        for match_id, start, end in condition_matches:
            entity_name = self.nlp.vocab.strings[match_id]
            if entity_name in seen_conditions:
                continue

            span = doc[start:end]
            is_negated = self._is_negated(note_text, span.start_char)

            if not is_negated:
                seen_conditions.add(entity_name)
                config = CONDITION_PATTERNS[entity_name]
                entities.append({
                    "entity_id": str(uuid.uuid4()),
                    "note_id": note_id,
                    "entity_type": "condition",
                    "entity_name": entity_name,
                    "matched_text": span.text,
                    "start_char": span.start_char,
                    "end_char": span.end_char,
                    "is_negated": False,
                    "snomed_code": config.get("snomed_code", ""),
                    "snomed_term": config.get("snomed_term", ""),
                    "icd10_code": config.get("icd10_code", ""),
                    "rxnorm_code": "",
                    "category": config.get("category", ""),
                    "confidence": 0.85,
                    "extraction_method": "rule_based_spacy",
                    "extracted_at": now,
                })

        # Extract medications
        medication_matches = self.medication_matcher(doc)
        seen_medications = set()

        for match_id, start, end in medication_matches:
            entity_name = self.nlp.vocab.strings[match_id]
            if entity_name in seen_medications:
                continue

            span = doc[start:end]
            is_negated = self._is_negated(note_text, span.start_char)

            if not is_negated:
                seen_medications.add(entity_name)
                config = MEDICATION_PATTERNS[entity_name]
                entities.append({
                    "entity_id": str(uuid.uuid4()),
                    "note_id": note_id,
                    "entity_type": "medication",
                    "entity_name": entity_name,
                    "matched_text": span.text,
                    "start_char": span.start_char,
                    "end_char": span.end_char,
                    "is_negated": False,
                    "snomed_code": "",
                    "snomed_term": "",
                    "icd10_code": "",
                    "rxnorm_code": config.get("rxnorm_code", ""),
                    "category": config.get("category", ""),
                    "confidence": 0.90,
                    "extraction_method": "rule_based_spacy",
                    "extracted_at": now,
                })

        # Extract symptoms
        symptom_matches = self.symptom_matcher(doc)
        seen_symptoms = set()

        for match_id, start, end in symptom_matches:
            entity_name = self.nlp.vocab.strings[match_id]
            if entity_name in seen_symptoms:
                continue

            span = doc[start:end]
            is_negated = self._is_negated(note_text, span.start_char)

            if not is_negated:
                seen_symptoms.add(entity_name)
                config = SYMPTOM_PATTERNS[entity_name]
                entities.append({
                    "entity_id": str(uuid.uuid4()),
                    "note_id": note_id,
                    "entity_type": "symptom",
                    "entity_name": entity_name,
                    "matched_text": span.text,
                    "start_char": span.start_char,
                    "end_char": span.end_char,
                    "is_negated": False,
                    "snomed_code": config.get("snomed_code", ""),
                    "snomed_term": config.get("snomed_term", ""),
                    "icd10_code": "",
                    "rxnorm_code": "",
                    "category": "Symptom",
                    "confidence": 0.80,
                    "extraction_method": "rule_based_spacy",
                    "extracted_at": now,
                })

        # Extract vital signs
        vitals = self._extract_vitals(note_text)
        for vital in vitals:
            entities.append({
                "entity_id": str(uuid.uuid4()),
                "note_id": note_id,
                "entity_type": vital["entity_type"],
                "entity_name": vital["entity_name"],
                "matched_text": f"{vital['value']} {vital['unit']}",
                "start_char": 0,
                "end_char": 0,
                "is_negated": False,
                "snomed_code": "",
                "snomed_term": "",
                "icd10_code": "",
                "rxnorm_code": "",
                "category": "Vital Sign",
                "confidence": 0.95,
                "extraction_method": "regex",
                "extracted_at": now,
            })

        return entities