"""Stitch one patient's records, scattered across files, into a single timeline.

This is the move that makes clinical data click: the patient is one person, but
their story is split across patients/encounters/conditions/observations/... linked
by the PATIENT id. Pull every row for one patient, line it up by date, and you get
their medical history as a story. That join-by-patient-id is the daily bread of a
healthcare data engineer.
"""
from __future__ import annotations

import pandas as pd


# (table name, date column, label)
_SOURCES = [
    ("encounters", "START", "Encounter"),
    ("conditions", "START", "Condition"),
    ("observations", "DATE", "Observation"),
    ("medications", "START", "Medication"),
    ("procedures", "START", "Procedure"),
    ("immunizations", "DATE", "Immunization"),
    ("allergies", "START", "Allergy"),
]


def patient_timeline(tables, patient_id: str) -> pd.DataFrame:
    """Return a date-sorted DataFrame of one patient's events across all files."""
    events = []
    for name, datecol, label in _SOURCES:
        df = tables.get(name)
        if df is None or df.empty:
            continue
        sub = df[df["PATIENT"] == patient_id]
        for _, r in sub.iterrows():
            raw = str(r.get(datecol, ""))
            events.append({
                "date": raw[:10],
                "kind": label,
                "code": r.get("CODE", ""),
                "description": r.get("DESCRIPTION", ""),
            })
    out = pd.DataFrame(events, columns=["date", "kind", "code", "description"])
    if not out.empty:
        out = out.sort_values("date", kind="stable").reset_index(drop=True)
    return out
