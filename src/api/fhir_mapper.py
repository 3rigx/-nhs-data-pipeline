"""
NHS Data Pipeline - FHIR Resource Mapper
==========================================
Converts NHS data models to FHIR R4 compatible resources.
"""

from src.api.schemas import (
    FHIRBundle,
    FHIRCodeableConcept,
    FHIRCoding,
    FHIRConditionResource,
    FHIRMedicationStatementResource,
    FHIRObservationResource,
    FHIRPeriod,
    FHIRReference,
)


def build_condition_resource(diagnosis: dict, nhs_number: str) -> FHIRConditionResource:
    """Build a FHIR Condition resource from a diagnosis record."""
    return FHIRConditionResource(
        id=str(diagnosis.get("diagnosis_id", "")),
        subject=FHIRReference(
            reference=f"Patient/{nhs_number}",
            display=f"NHS Number: {nhs_number}",
        ),
        code=FHIRCodeableConcept(
            coding=[
                FHIRCoding(
                    system="http://hl7.org/fhir/sid/icd-10",
                    code=str(diagnosis.get("diagnosis_code", "")),
                    display=str(diagnosis.get("icd10_chapter_name", "")),
                )
            ],
            text=str(diagnosis.get("diagnosis_code", "")),
        ),
        clinicalStatus=FHIRCodeableConcept(
            coding=[
                FHIRCoding(
                    system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                    code="active",
                    display="Active",
                )
            ],
            text="Active",
        ),
        category=[
            FHIRCodeableConcept(
                coding=[
                    FHIRCoding(
                        system="http://terminology.hl7.org/CodeSystem/condition-category",
                        code="encounter-diagnosis",
                        display="Encounter Diagnosis",
                    )
                ],
                text=str(diagnosis.get("diagnosis_type", "primary")),
            )
        ],
        onsetDateTime=str(diagnosis.get("diagnosis_date", "")),
        recordedDate=str(diagnosis.get("coding_date", "")),
    )


def build_medication_resource(medication: dict, nhs_number: str) -> FHIRMedicationStatementResource:
    """Build a FHIR MedicationStatement resource."""
    return FHIRMedicationStatementResource(
        id=str(medication.get("medication_id", "")),
        subject=FHIRReference(
            reference=f"Patient/{nhs_number}",
            display=f"NHS Number: {nhs_number}",
        ),
        medicationCodeableConcept=FHIRCodeableConcept(
            coding=[
                FHIRCoding(
                    system="http://www.nlm.nih.gov/research/umls/rxnorm",
                    code=str(medication.get("rxnorm_code", "0")),
                    display=str(medication.get("medication_name", "")),
                )
            ],
            text=str(medication.get("medication_name", "")),
        ),
        status="active" if medication.get("is_active") else "stopped",
        dosage=[
            {
                "text": f"{medication.get('dose', '')} {medication.get('form', '')} "
                       f"{medication.get('frequency', '')}",
                "route": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "display": str(medication.get("route", "")),
                        }
                    ]
                },
            }
        ],
        effectivePeriod=FHIRPeriod(
            start=str(medication.get("prescribed_date", "")),
            end=str(medication.get("end_date", "")) if medication.get("end_date") else None,
        ),
    )


def build_observation_resource(observation: dict, nhs_number: str) -> FHIRObservationResource:
    """Build a FHIR Observation resource from a lab result."""

    interpretation = None
    if observation.get("abnormal_flag") == "HIGH":
        interpretation = [
            FHIRCodeableConcept(
                coding=[
                    FHIRCoding(
                        system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                        code="H",
                        display="High",
                    )
                ],
                text="High",
            )
        ]
    elif observation.get("abnormal_flag") == "LOW":
        interpretation = [
            FHIRCodeableConcept(
                coding=[
                    FHIRCoding(
                        system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                        code="L",
                        display="Low",
                    )
                ],
                text="Low",
            )
        ]

    return FHIRObservationResource(
        id=str(observation.get("observation_id", "")),
        subject=FHIRReference(
            reference=f"Patient/{nhs_number}",
            display=f"NHS Number: {nhs_number}",
        ),
        code=FHIRCodeableConcept(
            coding=[
                FHIRCoding(
                    system="http://loinc.org",
                    code=str(observation.get("test_code", "")),
                    display=str(observation.get("test_name", "")),
                )
            ],
            text=str(observation.get("test_name", "")),
        ),
        valueQuantity={
            "value": observation.get("value"),
            "unit": str(observation.get("unit", "")),
            "system": "http://unitsofmeasure.org",
        },
        referenceRange=[
            {
                "low": {"value": observation.get("reference_range_low"), "unit": str(observation.get("unit", ""))},
                "high": {"value": observation.get("reference_range_high"), "unit": str(observation.get("unit", ""))},
            }
        ],
        effectiveDateTime=str(observation.get("observation_date", "")),
        interpretation=interpretation,
    )


def build_bundle(resources: list, resource_type: str) -> dict:
    """Build a FHIR Bundle from a list of resources."""
    entries = []
    for resource in resources:
        entries.append({
            "resource": resource.model_dump(),
            "search": {"mode": "match"},
        })

    return FHIRBundle(
        type="searchset",
        total=len(resources),
        entry=entries,
    ).model_dump()