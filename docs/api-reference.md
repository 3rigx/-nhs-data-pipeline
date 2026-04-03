# API Reference

The NHS Data Pipeline exposes a FHIR R4-compatible REST API built with FastAPI.
Interactive documentation (Swagger UI) is available at `http://localhost:8000/docs`
when the API is running locally.

All responses follow the HL7 FHIR R4 resource format (HL7 International, 2023)[^1].

---

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### Health check

```
GET /health
```

Returns the API status and version. Used by Docker healthchecks and the CI smoke test.

**Response**

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

---

### Patient

#### Get a patient by ID

```
GET /Patient/{patient_id}
```

Returns a FHIR R4 Patient resource for the given patient.

**Path parameters**

| Parameter | Type | Description |
|---|---|---|
| patient_id | string | Internal patient identifier (e.g. P00001) |

**Example response**

```json
{
  "resourceType": "Patient",
  "id": "P00001",
  "identifier": [
    {
      "system": "https://fhir.nhs.uk/Id/nhs-number",
      "value": "123-456-7890"
    }
  ],
  "gender": "male",
  "birthDate": "1965-03-14",
  "address": [
    {
      "postalCode": "SW1"
    }
  ]
}
```

**Error responses**

| Status | Meaning |
|---|---|
| 404 | Patient not found |
| 422 | Invalid patient_id format |

---

#### Search patients

```
GET /Patient
```

Returns a FHIR Bundle of Patient resources. Supports filtering.

**Query parameters**

| Parameter | Type | Description |
|---|---|---|
| gender | string | Filter by gender: male, female, unknown |
| birthdate | string | Filter by birth year (e.g. 1965) |
| _count | integer | Number of results per page (default 20, max 100) |
| _offset | integer | Pagination offset (default 0) |

---

### Condition

#### Get conditions for a patient

```
GET /Condition?subject={patient_id}
```

Returns a FHIR Bundle of Condition resources for a given patient.

**Example response**

```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 2,
  "entry": [
    {
      "resource": {
        "resourceType": "Condition",
        "id": "C00001",
        "subject": { "reference": "Patient/P00001" },
        "code": {
          "coding": [
            {
              "system": "http://hl7.org/fhir/sid/icd-10",
              "code": "I21.0",
              "display": "Acute transmural myocardial infarction of anterior wall"
            }
          ]
        },
        "onsetDateTime": "2022-06-14"
      }
    }
  ]
}
```

---

### Observation

#### Get observations for a patient

```
GET /Observation?subject={patient_id}
```

Returns a FHIR Bundle of Observation resources (lab results, vital signs).

**Query parameters**

| Parameter | Type | Description |
|---|---|---|
| subject | string | Patient ID (required) |
| code | string | LOINC or SNOMED code to filter by |
| date | string | Date range in FHIR format (e.g. ge2022-01-01) |

---

### Research cohort

#### List available cohorts

```
GET /cohort
```

Returns the five pre-defined research cohorts with their current patient counts.

**Example response**

```json
[
  { "cohort_id": "CHD_COHORT", "name": "Coronary Heart Disease", "patient_count": 412 },
  { "cohort_id": "T2D_COHORT", "name": "Type 2 Diabetes", "patient_count": 738 },
  { "cohort_id": "STROKE_COHORT", "name": "Stroke and TIA", "patient_count": 201 },
  { "cohort_id": "RESP_COHORT", "name": "Respiratory Disease", "patient_count": 534 },
  { "cohort_id": "FRAILTY_COHORT", "name": "Elderly Frailty", "patient_count": 289 }
]
```

#### Get patients in a cohort

```
GET /cohort/{cohort_id}/patients
```

Returns patient IDs belonging to the specified cohort.

---

## Authentication

The API currently runs without authentication in development mode.
For any production deployment, Bearer token authentication should be added
before exposing the API outside a private network.

---

[^1]: HL7 International (2023) *FHIR R4: HL7 Fast Healthcare Interoperability Resources*. Available at: https://hl7.org/fhir/R4/ (Accessed: 3 April 2026).
