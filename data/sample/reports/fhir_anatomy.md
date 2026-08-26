# Anatomy of a FHIR bundle

This bundle is a `transaction` Bundle with 77 entries.

## Resource types in the bundle

- Observation: 55
- Encounter: 12
- Condition: 3
- MedicationRequest: 3
- Procedure: 3
- Patient: 1

## How resources reference each other

Each line is: a resource -> the field -> what it points at.

- Encounter.subject -> urn:... (another resource in the bundle)
- Condition.subject -> urn:... (another resource in the bundle)
- Condition.encounter -> urn:... (another resource in the bundle)
- Observation.subject -> urn:... (another resource in the bundle)
- Observation.encounter -> urn:... (another resource in the bundle)
- MedicationRequest.subject -> urn:... (another resource in the bundle)
- MedicationRequest.encounter -> urn:... (another resource in the bundle)
- Procedure.subject -> urn:... (another resource in the bundle)
- Procedure.encounter -> urn:... (another resource in the bundle)
