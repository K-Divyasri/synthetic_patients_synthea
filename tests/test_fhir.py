"""Tests for the FHIR bundle builder and the anatomy helpers."""

from synthea_mini import generate_population, build_patient_bundle
from synthea_explorer import (resource_counts, reference_edges,
                              unresolved_references)


def a_patient_with_history(seed=5):
    tables = generate_population(n=20, seed=seed)
    # Find a patient who actually has encounters.
    counts = {}
    for e in tables["encounters"]:
        counts[e["PATIENT"]] = counts.get(e["PATIENT"], 0) + 1
    pid = max(counts, key=counts.get)
    return tables, pid


def test_bundle_shape():
    tables, pid = a_patient_with_history()
    bundle = build_patient_bundle(tables, pid)
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "transaction"
    assert len(bundle["entry"]) >= 2


def test_bundle_has_a_patient_and_clinical_resources():
    tables, pid = a_patient_with_history()
    counts = resource_counts(build_patient_bundle(tables, pid))
    assert counts["Patient"] == 1
    assert counts["Encounter"] >= 1


def test_all_references_resolve():
    tables, pid = a_patient_with_history()
    bundle = build_patient_bundle(tables, pid)
    # Every subject/encounter reference must point at a resource in the bundle.
    assert unresolved_references(bundle) == []


def test_reference_edges_exist():
    tables, pid = a_patient_with_history()
    edges = reference_edges(build_patient_bundle(tables, pid))
    # At least one resource should reference the patient.
    assert any(field in ("subject", "patient") for _rt, field, _ref in edges)
