"""Tests for the mini-Synthea generator: correct schema and valid cross-links."""

from synthea_mini import generate_population, write_tables, CSV_SCHEMA
from synthea_explorer import load_synthea


def test_columns_match_synthea_schema(tmp_path):
    tables = generate_population(n=10, seed=1)
    write_tables(tables, tmp_path)
    loaded = load_synthea(tmp_path)
    # Loaded columns are upper-cased; compare against the schema upper-cased too.
    for name, cols in CSV_SCHEMA.items():
        assert name in loaded, f"{name}.csv missing"
        assert list(loaded[name].columns) == [c.upper() for c in cols]


def test_population_size():
    tables = generate_population(n=15, seed=2)
    assert len(tables["patients"]) == 15


def test_referential_integrity():
    tables = generate_population(n=20, seed=3)
    patient_ids = {p["Id"] for p in tables["patients"]}
    encounter_ids = {e["Id"] for e in tables["encounters"]}

    for e in tables["encounters"]:
        assert e["PATIENT"] in patient_ids
    for child in ("conditions", "observations", "medications", "procedures",
                  "immunizations"):
        for row in tables[child]:
            assert row["PATIENT"] in patient_ids, f"{child} has orphan PATIENT"
            assert row["ENCOUNTER"] in encounter_ids, f"{child} has orphan ENCOUNTER"


def test_codes_use_expected_systems():
    tables = generate_population(n=20, seed=4)
    # Conditions are SNOMED (numeric codes); observations are LOINC (n-n format).
    for c in tables["conditions"]:
        assert c["CODE"].isdigit()
    for o in tables["observations"]:
        assert "-" in o["CODE"]  # LOINC codes look like 8302-2


def test_reproducible():
    a = generate_population(n=8, seed=7)
    b = generate_population(n=8, seed=7)
    assert [p["Id"] for p in a["patients"]] == [p["Id"] for p in b["patients"]]
