"""
NHS Data Pipeline - API Data Schemas
=====================================
Pydantic models for request/response validation.
Includes FHIR R4 compatible resource models.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============================================
# Base Models
# ============================================

class HealthCheck(BaseModel):
    """API health check response."""
    status: str = "healthy"
    service: str = "NHS Data Pipeline API"
    version: str = "1.0.0"
    database: str = "connected"
    timestamp: datetime


# ============================================
# Patient Models
# ============================================

class PatientDemographics(BaseModel):
    """Patient demographics response."""
    patient_id: str
    nhs_number: str
    gender: str
    date_of_birth: date
    age: int
    ethnicity_code: Optional[str] = None
    postcode: Optional[str] = None
    lsoa_code: Optional[str] = None
    gp_practice_code: Optional[str] = None
    gp_practice_name: Optional[str] = None
    is_active: bool
    is_deceased: bool


class PatientSummary(BaseModel):
    """Patient summary with key metrics."""
    patient: PatientDemographics
    total_episodes: int = 0
    total_diagnoses: int = 0
    total_medications: int = 0
    total_observations: int = 0


# ============================================
# FHIR R4 Compatible Models
# ============================================

class FHIRCoding(BaseModel):
    """FHIR Coding element."""
    system: str
    code: str
    display: str


class FHIRCodeableConcept(BaseModel):
    """FHIR CodeableConcept element."""
    coding: list[FHIRCoding]
    text: str


class FHIRReference(BaseModel):
    """FHIR Reference element."""
    reference: str
    display: Optional[str] = None


class FHIRPeriod(BaseModel):
    """FHIR Period element."""
    start: Optional[str] = None
    end: Optional[str] = None


class FHIRConditionResource(BaseModel):
    """FHIR R4 Condition resource."""
    resourceType: str = "Condition"
    id: str
    subject: FHIRReference
    code: FHIRCodeableConcept
    clinicalStatus: FHIRCodeableConcept
    category: list[FHIRCodeableConcept]
    onsetDateTime: Optional[str] = None
    recordedDate: Optional[str] = None


class FHIRMedicationStatementResource(BaseModel):
    """FHIR R4 MedicationStatement resource."""
    resourceType: str = "MedicationStatement"
    id: str
    subject: FHIRReference
    medicationCodeableConcept: FHIRCodeableConcept
    status: str
    dosage: list[dict]
    effectivePeriod: Optional[FHIRPeriod] = None


class FHIRObservationResource(BaseModel):
    """FHIR R4 Observation resource."""
    resourceType: str = "Observation"
    id: str
    subject: FHIRReference
    code: FHIRCodeableConcept
    status: str = "final"
    valueQuantity: Optional[dict] = None
    referenceRange: Optional[list[dict]] = None
    effectiveDateTime: Optional[str] = None
    interpretation: Optional[list[FHIRCodeableConcept]] = None


class FHIRBundle(BaseModel):
    """FHIR R4 Bundle resource."""
    resourceType: str = "Bundle"
    type: str = "searchset"
    total: int
    entry: list[dict]


# ============================================
# Cohort Models
# ============================================

class CohortSummary(BaseModel):
    """Generic cohort summary response."""
    cohort_name: str
    cohort_version: str
    total_patients: int
    generated_date: str
    summary: dict


class DiabetesCohortSummary(BaseModel):
    """Diabetes cohort summary."""
    total_patients: int
    risk_distribution: dict
    control_distribution: dict
    avg_hba1c: Optional[float] = None
    avg_medications: float
    detection_sources: dict


class CardiovascularCohortSummary(BaseModel):
    """Cardiovascular risk cohort summary."""
    total_patients: int
    risk_distribution: dict
    avg_risk_score: float
    avg_comorbidities: float
    condition_prevalence: dict


class ReadmissionSummary(BaseModel):
    """Emergency readmission summary."""
    total_index_episodes: int
    readmission_30day_count: int
    readmission_30day_rate: float
    readmission_7day_count: int
    readmission_7day_rate: float
    same_trust_readmission_rate: float
    by_time_band: dict


# ============================================
# Hospital Models
# ============================================

class HospitalActivity(BaseModel):
    """Hospital activity metrics."""
    trust_code: str
    trust_name: str
    total_episodes: int
    unique_patients: int
    emergency_rate_pct: float
    avg_length_of_stay: float
    mortality_rate_pct: float
    avg_age: float


class HospitalActivityResponse(BaseModel):
    """Hospital activity response."""
    total_trusts: int
    hospitals: list[HospitalActivity]


# ============================================
# NLP Models
# ============================================

class NLPStats(BaseModel):
    """NLP pipeline statistics."""
    total_notes_processed: int
    total_entities_extracted: int
    notes_with_entities_pct: float
    avg_entities_per_note: float
    entity_type_breakdown: dict
    top_conditions: list[dict]
    top_medications: list[dict]