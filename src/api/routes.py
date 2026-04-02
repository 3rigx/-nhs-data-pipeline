"""
NHS Data Pipeline - API Routes
================================
All API endpoint definitions.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from src.api.database import get_db_connection, query_to_dict, query_single
from src.api.fhir_mapper import (
    build_bundle,
    build_condition_resource,
    build_medication_resource,
    build_observation_resource,
)
from src.api.schemas import (
    CardiovascularCohortSummary,
    CohortSummary,
    DiabetesCohortSummary,
    HealthCheck,
    HospitalActivity,
    HospitalActivityResponse,
    NLPStats,
    PatientDemographics,
    PatientSummary,
    ReadmissionSummary,
)

router = APIRouter()


# ============================================
# Health Check
# ============================================

@router.get("/health", response_model=HealthCheck, tags=["System"])
def health_check():
    """API health check — verifies database connectivity."""
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthCheck(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        timestamp=datetime.now(),
    )


# ============================================
# Patient Endpoints
# ============================================

@router.get(
    "/patients/{nhs_number}",
    response_model=PatientSummary,
    tags=["Patients"],
    summary="Get patient demographics and summary",
)
def get_patient(nhs_number: str):
    """
    Retrieve patient demographics by NHS Number.

    Returns patient details including age, gender, GP practice,
    and summary counts of clinical data.
    """
    conn = get_db_connection()

    # Get patient demographics
    patient = query_single(conn, """
        SELECT
            patient_id, nhs_number, gender, date_of_birth,
            age, ethnicity_code, postcode, lsoa_code,
            gp_practice_code, gp_practice_name, is_active, is_deceased
        FROM main_staging.stg_patients
        WHERE nhs_number = ?
    """, [nhs_number])

    if not patient:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Patient with NHS Number {nhs_number} not found")

    # Get summary counts
    patient_id = patient["patient_id"]

    episodes = query_single(conn, """
        SELECT COUNT(*) as count FROM main_staging.stg_episodes WHERE patient_id = ?
    """, [patient_id])

    diagnoses = query_single(conn, """
        SELECT COUNT(*) as count FROM main_staging.stg_diagnoses WHERE patient_id = ?
    """, [patient_id])

    medications = query_single(conn, """
        SELECT COUNT(*) as count FROM main_staging.stg_medications WHERE patient_id = ?
    """, [patient_id])

    observations = query_single(conn, """
        SELECT COUNT(*) as count FROM main_staging.stg_observations WHERE patient_id = ?
    """, [patient_id])

    conn.close()

    return PatientSummary(
        patient=PatientDemographics(**patient),
        total_episodes=episodes.get("count", 0),
        total_diagnoses=diagnoses.get("count", 0),
        total_medications=medications.get("count", 0),
        total_observations=observations.get("count", 0),
    )


@router.get(
    "/patients/{nhs_number}/conditions",
    tags=["Patients", "FHIR"],
    summary="Get patient conditions (FHIR Bundle)",
)
def get_patient_conditions(nhs_number: str):
    """
    Retrieve patient conditions as a FHIR R4 Bundle.

    Returns ICD-10 coded conditions in FHIR Condition resource format.
    """
    conn = get_db_connection()

    patient = query_single(conn, """
        SELECT patient_id FROM main_staging.stg_patients WHERE nhs_number = ?
    """, [nhs_number])

    if not patient:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Patient with NHS Number {nhs_number} not found")

    diagnoses = query_to_dict(conn, """
        SELECT
            diagnosis_id, diagnosis_code, diagnosis_type,
            icd10_chapter_name, diagnosis_date, coding_date
        FROM main_intermediate.int_patient_diagnoses
        WHERE patient_id = ?
        ORDER BY diagnosis_date DESC
    """, [patient["patient_id"]])

    conn.close()

    resources = [build_condition_resource(d, nhs_number) for d in diagnoses]
    return build_bundle(resources, "Condition")


@router.get(
    "/patients/{nhs_number}/medications",
    tags=["Patients", "FHIR"],
    summary="Get patient medications (FHIR Bundle)",
)
def get_patient_medications(nhs_number: str):
    """
    Retrieve patient medications as a FHIR R4 Bundle.

    Returns medications in FHIR MedicationStatement resource format.
    """
    conn = get_db_connection()

    patient = query_single(conn, """
        SELECT patient_id FROM main_staging.stg_patients WHERE nhs_number = ?
    """, [nhs_number])

    if not patient:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Patient with NHS Number {nhs_number} not found")

    medications = query_to_dict(conn, """
        SELECT
            medication_id, medication_name, dose, form, route,
            frequency, indication, prescription_status, is_active,
            prescribed_date, end_date, medication_category
        FROM main_intermediate.int_patient_medications
        WHERE patient_id = ?
        ORDER BY prescribed_date DESC
    """, [patient["patient_id"]])

    conn.close()

    # Get rxnorm codes from concept mapping
    rxnorm_lookup = {}
    try:
        conn2 = get_db_connection()
        rxnorm = query_to_dict(conn2, """
            SELECT source_code, omop_concept_id
            FROM main.omop_concept_mappings
            WHERE source_vocabulary = 'RxNorm'
        """)
        conn2.close()
        rxnorm_lookup = {r["source_code"]: r["omop_concept_id"] for r in rxnorm}
    except Exception:
        pass

    for med in medications:
        med["rxnorm_code"] = rxnorm_lookup.get(med["medication_name"], "0")

    resources = [build_medication_resource(m, nhs_number) for m in medications]
    return build_bundle(resources, "MedicationStatement")


@router.get(
    "/patients/{nhs_number}/observations",
    tags=["Patients", "FHIR"],
    summary="Get patient observations (FHIR Bundle)",
)
def get_patient_observations(
    nhs_number: str,
    test_code: str = Query(None, description="Filter by test code (e.g., HBA1C, CREAT)"),
    limit: int = Query(50, description="Maximum results to return", le=200),
):
    """
    Retrieve patient lab results as a FHIR R4 Bundle.

    Returns observations in FHIR Observation resource format.
    Optionally filter by test code.
    """
    conn = get_db_connection()

    patient = query_single(conn, """
        SELECT patient_id FROM main_staging.stg_patients WHERE nhs_number = ?
    """, [nhs_number])

    if not patient:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Patient with NHS Number {nhs_number} not found")

    sql = """
        SELECT
            observation_id, test_code, test_name, value, unit,
            reference_range_low, reference_range_high,
            abnormal_flag, observation_date
        FROM main_staging.stg_observations
        WHERE patient_id = ?
    """
    params = [patient["patient_id"]]

    if test_code:
        sql += " AND test_code = ?"
        params.append(test_code.upper())

    sql += f" ORDER BY observation_date DESC LIMIT {limit}"

    observations = query_to_dict(conn, sql, params)
    conn.close()

    resources = [build_observation_resource(o, nhs_number) for o in observations]
    return build_bundle(resources, "Observation")


# ============================================
# Cohort Endpoints
# ============================================

@router.get(
    "/cohorts/diabetes",
    response_model=CohortSummary,
    tags=["Cohorts"],
    summary="Get diabetes cohort summary",
)
def get_diabetes_cohort():
    """
    Diabetes population cohort summary.

    Returns patient counts, risk distribution, HbA1c control categories,
    and detection source breakdown.
    """
    conn = get_db_connection()

    total = query_single(conn, "SELECT COUNT(*) as count FROM main_cohorts.cohort_diabetes")

    risk_dist = query_to_dict(conn, """
        SELECT risk_category, COUNT(*) as count
        FROM main_cohorts.cohort_diabetes
        GROUP BY risk_category
    """)

    control_dist = query_to_dict(conn, """
        SELECT diabetes_control_category, COUNT(*) as count
        FROM main_cohorts.cohort_diabetes
        GROUP BY diabetes_control_category
    """)

    avg_hba1c = query_single(conn, """
        SELECT ROUND(AVG(latest_hba1c_value), 1) as avg_val
        FROM main_cohorts.cohort_diabetes
        WHERE latest_hba1c_value IS NOT NULL
    """)

    avg_meds = query_single(conn, """
        SELECT ROUND(AVG(diabetes_medication_count), 1) as avg_val
        FROM main_cohorts.cohort_diabetes
    """)

    conn.close()

    return CohortSummary(
        cohort_name="diabetes_population",
        cohort_version="1.0.0",
        total_patients=total.get("count", 0),
        generated_date=str(datetime.now().date()),
        summary={
            "risk_distribution": {r["risk_category"]: r["count"] for r in risk_dist},
            "control_distribution": {r["diabetes_control_category"]: r["count"] for r in control_dist},
            "avg_hba1c": avg_hba1c.get("avg_val"),
            "avg_medications": avg_meds.get("avg_val", 0),
        },
    )


@router.get(
    "/cohorts/cardiovascular",
    response_model=CohortSummary,
    tags=["Cohorts"],
    summary="Get cardiovascular risk cohort summary",
)
def get_cardiovascular_cohort():
    """
    Cardiovascular risk stratification cohort summary.

    Returns risk score distribution and condition prevalence.
    """
    conn = get_db_connection()

    total = query_single(conn, "SELECT COUNT(*) as count FROM main_cohorts.cohort_cardiovascular_risk")

    risk_dist = query_to_dict(conn, """
        SELECT cv_risk_category, COUNT(*) as count
        FROM main_cohorts.cohort_cardiovascular_risk
        GROUP BY cv_risk_category
    """)

    avg_score = query_single(conn, """
        SELECT
            ROUND(AVG(cv_risk_score), 1) as avg_score,
            ROUND(AVG(comorbidity_count), 1) as avg_comorbidities
        FROM main_cohorts.cohort_cardiovascular_risk
    """)

    prevalence = query_single(conn, """
        SELECT
            ROUND(AVG(has_hypertension) * 100, 1) as hypertension_pct,
            ROUND(AVG(has_diabetes) * 100, 1) as diabetes_pct,
            ROUND(AVG(has_heart_failure) * 100, 1) as heart_failure_pct,
            ROUND(AVG(has_atrial_fibrillation) * 100, 1) as af_pct,
            ROUND(AVG(has_high_cholesterol) * 100, 1) as high_chol_pct
        FROM main_cohorts.cohort_cardiovascular_risk
    """)

    conn.close()

    return CohortSummary(
        cohort_name="cardiovascular_risk",
        cohort_version="1.0.0",
        total_patients=total.get("count", 0),
        generated_date=str(datetime.now().date()),
        summary={
            "risk_distribution": {r["cv_risk_category"]: r["count"] for r in risk_dist},
            "avg_risk_score": avg_score.get("avg_score", 0),
            "avg_comorbidities": avg_score.get("avg_comorbidities", 0),
            "condition_prevalence_pct": prevalence,
        },
    )


@router.get(
    "/cohorts/readmissions",
    response_model=CohortSummary,
    tags=["Cohorts"],
    summary="Get emergency readmission metrics",
)
def get_readmission_cohort():
    """
    30-day emergency readmission analysis.

    Returns readmission rates, time bands, and trust-level metrics.
    """
    conn = get_db_connection()

    total = query_single(conn, """
        SELECT
            COUNT(*) as total_episodes,
            SUM(CASE WHEN is_30day_emergency_readmission THEN 1 ELSE 0 END) as readmit_30d,
            SUM(CASE WHEN is_7day_emergency_readmission THEN 1 ELSE 0 END) as readmit_7d
        FROM main_cohorts.cohort_emergency_readmissions
    """)

    time_bands = query_to_dict(conn, """
        SELECT readmission_time_band, COUNT(*) as count
        FROM main_cohorts.cohort_emergency_readmissions
        WHERE is_30day_emergency_readmission = TRUE
        GROUP BY readmission_time_band
    """)

    conn.close()

    total_eps = total.get("total_episodes", 1)
    readmit_30d = total.get("readmit_30d", 0)
    readmit_7d = total.get("readmit_7d", 0)

    return CohortSummary(
        cohort_name="emergency_readmissions_30day",
        cohort_version="1.0.0",
        total_patients=total_eps,
        generated_date=str(datetime.now().date()),
        summary={
            "total_index_episodes": total_eps,
            "readmission_30day_count": readmit_30d,
            "readmission_30day_rate_pct": round(readmit_30d * 100 / max(total_eps, 1), 1),
            "readmission_7day_count": readmit_7d,
            "readmission_7day_rate_pct": round(readmit_7d * 100 / max(total_eps, 1), 1),
            "by_time_band": {r["readmission_time_band"]: r["count"] for r in time_bands},
        },
    )


# ============================================
# Hospital Endpoints
# ============================================

@router.get(
    "/hospitals/activity",
    response_model=HospitalActivityResponse,
    tags=["Hospitals"],
    summary="Get London hospital activity metrics",
)
def get_hospital_activity():
    """
    Hospital activity summary across London NHS Trusts.

    Returns episode counts, emergency rates, mortality,
    and demographic breakdowns per trust.
    """
    conn = get_db_connection()

    hospitals = query_to_dict(conn, """
        SELECT
            trust_code, trust_name, total_episodes, unique_patients,
            emergency_rate_pct, avg_length_of_stay, mortality_rate_pct,
            avg_age_at_admission as avg_age
        FROM main_intermediate.int_hospital_activity
        ORDER BY total_episodes DESC
    """)

    conn.close()

    return HospitalActivityResponse(
        total_trusts=len(hospitals),
        hospitals=[HospitalActivity(**h) for h in hospitals],
    )


# ============================================
# NLP Endpoints
# ============================================

@router.get(
    "/nlp/stats",
    response_model=NLPStats,
    tags=["NLP"],
    summary="Get NLP pipeline statistics",
)
def get_nlp_stats():
    """
    Clinical NLP pipeline processing statistics.

    Returns entity extraction counts, coverage metrics,
    and top extracted conditions and medications.
    """
    conn = get_db_connection()

    overview = query_single(conn, """
        SELECT
            COUNT(*) as total_notes,
            SUM(CASE WHEN total_entities > 0 THEN 1 ELSE 0 END) as notes_with_entities
        FROM nlp.nlp_note_summaries
    """)

    entity_counts = query_to_dict(conn, """
        SELECT entity_type, COUNT(*) as count
        FROM nlp.nlp_extracted_entities
        GROUP BY entity_type
        ORDER BY count DESC
    """)

    total_entities = sum(e["count"] for e in entity_counts)

    top_conditions = query_to_dict(conn, """
        SELECT entity_name as name, COUNT(*) as count
        FROM nlp.nlp_extracted_entities
        WHERE entity_type = 'condition'
        GROUP BY entity_name
        ORDER BY count DESC
        LIMIT 10
    """)

    top_medications = query_to_dict(conn, """
        SELECT entity_name as name, COUNT(*) as count
        FROM nlp.nlp_extracted_entities
        WHERE entity_type = 'medication'
        GROUP BY entity_name
        ORDER BY count DESC
        LIMIT 10
    """)

    conn.close()

    total_notes = overview.get("total_notes", 1)
    notes_with = overview.get("notes_with_entities", 0)

    return NLPStats(
        total_notes_processed=total_notes,
        total_entities_extracted=total_entities,
        notes_with_entities_pct=round(notes_with * 100 / max(total_notes, 1), 1),
        avg_entities_per_note=round(total_entities / max(total_notes, 1), 1),
        entity_type_breakdown={e["entity_type"]: e["count"] for e in entity_counts},
        top_conditions=top_conditions,
        top_medications=top_medications,
    )