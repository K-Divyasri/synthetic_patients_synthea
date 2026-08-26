"""Tests for the explorer: loading, summarising, and per-patient timelines."""

from datetime import date

from synthea_mini import generate_population, write_tables
from synthea_explorer import (load_synthea, summarize, patient_timeline,
                              patient_with_most_encounters)


def build(tmp_path, n=20, seed=5):
    tables = generate_population(n=n, seed=seed)
    write_tables(tables, tmp_path)
    return load_synthea(tmp_path)


def test_summary_basic(tmp_path):
    tables = build(tmp_path)
    s = summarize(tables, as_of=date(2026, 1, 1))
    assert s["n_patients"] == 20
    assert s["n_encounters"] > 0
    assert s["top_conditions"], "expected at least one condition"
    assert set(s["gender"]) <= {"M", "F"}


def test_timeline_sorted_and_nonempty(tmp_path):
    tables = build(tmp_path)
    pid = patient_with_most_encounters(tables)
    tl = patient_timeline(tables, pid)
    assert not tl.empty
    dates = list(tl["date"])
    assert dates == sorted(dates), "timeline should be in date order"
    assert "Encounter" in set(tl["kind"])


def test_timeline_only_that_patient(tmp_path):
    tables = build(tmp_path)
    pid = patient_with_most_encounters(tables)
    tl = patient_timeline(tables, pid)
    # Every encounter in the timeline must belong to that patient.
    enc = tables["encounters"]
    their_codes = set(enc[enc["PATIENT"] == pid]["CODE"])
    tl_enc_codes = set(tl[tl["kind"] == "Encounter"]["code"])
    assert tl_enc_codes <= their_codes
