"""Build a FHIR R4 transaction Bundle for a single patient.

A Bundle is how FHIR ships a set of related resources together. Real Synthea
writes one Bundle per patient containing their whole record. We build a faithful
small version from the generated tables, using the SAME code systems FHIR uses:

  SNOMED CT -> http://snomed.info/sct
  LOINC     -> http://loinc.org
  RxNorm    -> http://www.nlm.nih.gov/research/umls/rxnorm
  CVX       -> http://hl7.org/fhir/sid/cvx

The point is to teach the "anatomy" of a bundle: a list of entries, each a typed
resource, wired together with references (an Observation points at its Patient and
its Encounter). The explorer's fhir_anatomy.py reads exactly this structure.
"""
from __future__ import annotations

SNOMED = "http://snomed.info/sct"
LOINC = "http://loinc.org"
RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"
CVX = "http://hl7.org/fhir/sid/cvx"


def _ref(resource_id: str) -> dict:
    return {"reference": f"urn:uuid:{resource_id}"}


def _cc(system: str, code: str, display: str) -> dict:
    return {"coding": [{"system": system, "code": str(code), "display": display}],
            "text": display}


def _entry(resource: dict) -> dict:
    return {
        "fullUrl": f"urn:uuid:{resource['id']}",
        "resource": resource,
        "request": {"method": "POST", "url": resource["resourceType"]},
    }


def build_patient_bundle(tables, patient_id: str) -> dict:
    """Assemble one patient's resources into a FHIR R4 transaction Bundle."""
    rows = {name: [r for r in tbl if r.get("PATIENT") == patient_id or r.get("Id") == patient_id]
            for name, tbl in tables.items()}
    patient = next(p for p in tables["patients"] if p["Id"] == patient_id)

    entries = [_entry(_patient_resource(patient))]

    for e in [e for e in tables["encounters"] if e["PATIENT"] == patient_id]:
        entries.append(_entry(_encounter_resource(e, patient_id)))
    for c in [c for c in tables["conditions"] if c["PATIENT"] == patient_id]:
        entries.append(_entry(_condition_resource(c, patient_id)))
    for o in [o for o in tables["observations"] if o["PATIENT"] == patient_id]:
        entries.append(_entry(_observation_resource(o, patient_id)))
    for m in [m for m in tables["medications"] if m["PATIENT"] == patient_id]:
        entries.append(_entry(_medication_resource(m, patient_id)))
    for p in [p for p in tables["procedures"] if p["PATIENT"] == patient_id]:
        entries.append(_entry(_procedure_resource(p, patient_id)))
    for im in [i for i in tables["immunizations"] if i["PATIENT"] == patient_id]:
        entries.append(_entry(_immunization_resource(im, patient_id)))

    return {"resourceType": "Bundle", "type": "transaction", "entry": entries}


def _patient_resource(p) -> dict:
    res = {
        "resourceType": "Patient", "id": p["Id"],
        "name": [{"use": "official", "family": p["LAST"],
                  "given": [g for g in [p["FIRST"], p["MIDDLE"]] if g],
                  "prefix": [p["PREFIX"]] if p["PREFIX"] else []}],
        "gender": "male" if p["GENDER"] == "M" else "female",
        "birthDate": p["BIRTHDATE"],
        "address": [{"line": [p["ADDRESS"]], "city": p["CITY"],
                     "state": p["STATE"], "postalCode": p["ZIP"]}],
        "identifier": [{"system": "http://hl7.org/fhir/sid/us-ssn", "value": p["SSN"]}],
    }
    if p["DEATHDATE"]:
        res["deceasedDateTime"] = p["DEATHDATE"]
    return res


def _encounter_resource(e, pid) -> dict:
    return {
        "resourceType": "Encounter", "id": e["Id"], "status": "finished",
        "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                  "code": e["ENCOUNTERCLASS"]},
        "type": [_cc(SNOMED, e["CODE"], e["DESCRIPTION"])],
        "subject": _ref(pid),
        "period": {"start": e["START"], "end": e["STOP"]},
    }


def _condition_resource(c, pid) -> dict:
    res = {
        "resourceType": "Condition", "id": _row_id(c, pid, "cond"),
        "clinicalStatus": {"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "active" if not c["STOP"] else "resolved"}]},
        "code": _cc(SNOMED, c["CODE"], c["DESCRIPTION"]),
        "subject": _ref(pid), "encounter": _ref(c["ENCOUNTER"]),
        "onsetDateTime": c["START"],
    }
    return res


def _observation_resource(o, pid) -> dict:
    return {
        "resourceType": "Observation", "id": _row_id(o, pid, "obs"),
        "status": "final",
        "category": [{"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
            "code": o["CATEGORY"]}]}],
        "code": _cc(LOINC, o["CODE"], o["DESCRIPTION"]),
        "subject": _ref(pid), "encounter": _ref(o["ENCOUNTER"]),
        "effectiveDateTime": o["DATE"],
        "valueQuantity": {"value": o["VALUE"], "unit": o["UNITS"],
                          "system": "http://unitsofmeasure.org", "code": o["UNITS"]},
    }


def _medication_resource(m, pid) -> dict:
    return {
        "resourceType": "MedicationRequest", "id": _row_id(m, pid, "med"),
        "status": "active", "intent": "order",
        "medicationCodeableConcept": _cc(RXNORM, m["CODE"], m["DESCRIPTION"]),
        "subject": _ref(pid), "encounter": _ref(m["ENCOUNTER"]),
        "authoredOn": m["START"],
    }


def _procedure_resource(p, pid) -> dict:
    return {
        "resourceType": "Procedure", "id": _row_id(p, pid, "proc"),
        "status": "completed",
        "code": _cc(SNOMED, p["CODE"], p["DESCRIPTION"]),
        "subject": _ref(pid), "encounter": _ref(p["ENCOUNTER"]),
        "performedPeriod": {"start": p["START"], "end": p["STOP"]},
    }


def _immunization_resource(im, pid) -> dict:
    return {
        "resourceType": "Immunization", "id": _row_id(im, pid, "imm"),
        "status": "completed",
        "vaccineCode": _cc(CVX, im["CODE"], im["DESCRIPTION"]),
        "patient": _ref(pid), "encounter": _ref(im["ENCOUNTER"]),
        "occurrenceDateTime": im["DATE"],
    }


def _row_id(row, pid, prefix) -> str:
    """Child rows in the CSVs have no Id of their own, so derive a stable one from
    the patient, encounter, code, and date. Deterministic = reproducible bundles."""
    key = f"{prefix}-{pid}-{row.get('ENCOUNTER','')}-{row.get('CODE','')}-{row.get('DATE') or row.get('START','')}"
    import hashlib
    h = hashlib.sha1(key.encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
