"""Population-level summary stats over a loaded Synthea dataset.

These are the questions you ask first of any clinical dataset: how many patients,
who are they, how often do they show up, and what's wrong with them. Every number
here is something a notebook plots and an interviewer might ask you to pull.
"""
from __future__ import annotations

from datetime import date


def _age_years(birthdate: str, as_of: date):
    if not birthdate:
        return None
    try:
        b = date.fromisoformat(birthdate[:10])
    except ValueError:
        return None
    return (as_of - b).days // 365


def summarize(tables, as_of=date(2026, 1, 1)) -> dict:
    pats = tables["patients"]
    n = len(pats)

    ages = [a for a in (_age_years(b, as_of) for b in pats["BIRTHDATE"]) if a is not None]
    age_stats = {}
    if ages:
        age_stats = {"min": min(ages), "max": max(ages),
                     "mean": round(sum(ages) / len(ages), 1)}

    enc = tables.get("encounters")
    n_enc = 0 if enc is None else len(enc)
    eclass = {} if enc is None else enc["ENCOUNTERCLASS"].value_counts().to_dict()

    cond = tables.get("conditions")
    top_conditions = ({} if cond is None
                      else cond["DESCRIPTION"].value_counts().head(10).to_dict())

    meds = tables.get("medications")
    top_medications = ({} if meds is None
                       else meds["DESCRIPTION"].value_counts().head(10).to_dict())

    return {
        "n_patients": n,
        "gender": pats["GENDER"].value_counts().to_dict(),
        "race": pats["RACE"].value_counts().to_dict(),
        "age_stats": age_stats,
        "n_encounters": n_enc,
        "encounters_per_patient": round(n_enc / n, 2) if n else 0,
        "encounter_class": eclass,
        "top_conditions": top_conditions,
        "top_medications": top_medications,
        "tables_loaded": {name: len(df) for name, df in tables.items()},
    }


def patient_with_most_encounters(tables) -> str:
    """Handy for demos: the id of the patient with the richest history."""
    enc = tables["encounters"]
    if enc.empty:
        return tables["patients"]["ID"].iloc[0]
    return enc["PATIENT"].value_counts().idxmax()
