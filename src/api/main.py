"""
NHS Data Pipeline - FastAPI Application
=========================================
RESTful API with FHIR R4 compatible endpoints for NHS health data.

Features:
- Patient demographics and clinical data
- FHIR R4 Condition, MedicationStatement, Observation resources
- Research cohort summaries (Diabetes, CV Risk, Readmissions)
- Hospital activity metrics
- NLP pipeline statistics

Usage:
    poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

Docs:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router

# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="NHS Data Pipeline API",
    description="""
## NHS Health Data Platform API

RESTful API providing access to NHS health data with **FHIR R4** compatible endpoints.

### Features
- **Patient Data**: Demographics, conditions, medications, lab results
- **FHIR R4**: Standards-compliant clinical data resources
- **Research Cohorts**: Pre-built cohorts for diabetes, cardiovascular risk, readmissions
- **Hospital Metrics**: Trust-level activity and performance data
- **NLP Analytics**: Clinical text extraction statistics

### Data Standards
- **ICD-10**: Diagnosis coding
- **OPCS-4**: Procedure coding
- **SNOMED-CT**: Clinical terminology
- **OMOP CDM**: Common data model
- **FHIR R4**: Interoperability standard

### Disclaimer
All data is **synthetic**. No real patient data is used or exposed.
    """,
    version="1.0.0",
    contact={
        "name": "NHS Data Engineering Team",
        "email": "data-engineering@nhs.net",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================
# CORS Middleware
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Include Routes
# ============================================

app.include_router(router, prefix="/api/v1")


# ============================================
# Root Endpoint
# ============================================

@app.get("/", tags=["System"])
def root():
    """Root endpoint — API information."""
    return {
        "service": "NHS Data Pipeline API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_base": "/api/v1",
        "endpoints": {
            "health": "/api/v1/health",
            "patients": "/api/v1/patients/{nhs_number}",
            "conditions": "/api/v1/patients/{nhs_number}/conditions",
            "medications": "/api/v1/patients/{nhs_number}/medications",
            "observations": "/api/v1/patients/{nhs_number}/observations",
            "cohort_diabetes": "/api/v1/cohorts/diabetes",
            "cohort_cardiovascular": "/api/v1/cohorts/cardiovascular",
            "cohort_readmissions": "/api/v1/cohorts/readmissions",
            "hospital_activity": "/api/v1/hospitals/activity",
            "nlp_stats": "/api/v1/nlp/stats",
        },
    }