"""Generate a synthetic patient population in Synthea's CSV shape.

This is a small stand-in for Synthea itself (which needs Java). It writes the same
files, with the same column names and the same coding systems, so:
  - everything in this project runs with zero Java, and
  - the explorer code works UNCHANGED on real Synthea output later.

It is NOT a clinical simulator like the real Synthea - it won't model disease
progression realistically. It's a faithful *schema* twin for learning. When you're
ready for the real thing, see run_real_synthea.md; the explorer
and notebooks will load that output too.
"""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta

from faker import Faker

from . import vocab

# Exact column order for each Synthea CSV file (matches the official CSV Data
# Dictionary). "Id" keeps its capitalisation the way Synthea writes it.
CSV_SCHEMA = {
    "patients": ["Id", "BIRTHDATE", "DEATHDATE", "SSN", "DRIVERS", "PASSPORT",
                 "PREFIX", "FIRST", "MIDDLE", "LAST", "SUFFIX", "MAIDEN",
                 "MARITAL", "RACE", "ETHNICITY", "GENDER", "BIRTHPLACE",
                 "ADDRESS", "CITY", "STATE", "COUNTY", "FIPS", "ZIP", "LAT",
                 "LON", "HEALTHCARE_EXPENSES", "HEALTHCARE_COVERAGE", "INCOME"],
    "encounters": ["Id", "START", "STOP", "PATIENT", "ORGANIZATION", "PROVIDER",
                   "PAYER", "ENCOUNTERCLASS", "CODE", "DESCRIPTION",
                   "BASE_ENCOUNTER_COST", "TOTAL_CLAIM_COST", "PAYER_COVERAGE",
                   "REASONCODE", "REASONDESCRIPTION"],
    "conditions": ["START", "STOP", "PATIENT", "ENCOUNTER", "SYSTEM", "CODE",
                   "DESCRIPTION"],
    "observations": ["DATE", "PATIENT", "ENCOUNTER", "CATEGORY", "CODE",
                     "DESCRIPTION", "VALUE", "UNITS", "TYPE"],
    "medications": ["START", "STOP", "PATIENT", "PAYER", "ENCOUNTER", "CODE",
                    "DESCRIPTION", "BASE_COST", "PAYER_COVERAGE", "DISPENSES",
                    "TOTALCOST", "REASONCODE", "REASONDESCRIPTION"],
    "procedures": ["START", "STOP", "PATIENT", "ENCOUNTER", "SYSTEM", "CODE",
                   "DESCRIPTION", "BASE_COST", "REASONCODE", "REASONDESCRIPTION"],
    "immunizations": ["DATE", "PATIENT", "ENCOUNTER", "CODE", "DESCRIPTION", "COST"],
    "careplans": ["Id", "START", "STOP", "PATIENT", "ENCOUNTER", "CODE",
                  "DESCRIPTION", "REASONCODE", "REASONDESCRIPTION"],
    "allergies": ["START", "STOP", "PATIENT", "ENCOUNTER", "CODE", "SYSTEM",
                  "DESCRIPTION", "TYPE", "CATEGORY", "REACTION1", "DESCRIPTION1",
                  "SEVERITY1", "REACTION2", "DESCRIPTION2", "SEVERITY2"],
}

RACES = ["white", "black", "asian", "native", "other"]
ETHNICITIES = ["hispanic", "nonhispanic"]
MARITAL = ["M", "S"]


def _uuid(rng: random.Random) -> str:
    """A reproducible UUID-shaped id (Synthea ids look like this)."""
    h = "%032x" % rng.getrandbits(128)
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def _ts(d: datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def write_tables(tables, out_dir):
    """Write each table to <out_dir>/<name>.csv with the exact Synthea columns.
    This mirrors how real Synthea lays out its ./output/csv folder."""
    import pandas as pd
    from pathlib import Path

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        cols = CSV_SCHEMA[name]
        df = pd.DataFrame(rows, columns=cols)
        df.to_csv(out / f"{name}.csv", index=False)
    return out


def generate_population(n=25, seed=12, as_of=date(2026, 1, 1)):
    """Build a population and return a dict of {table_name: list_of_row_dicts}.

    `as_of` is passed in (never date.today()) so the data is reproducible and the
    tests don't drift over time.
    """
    rng = random.Random(seed)
    fake = Faker("en_US")
    Faker.seed(seed)

    tables = {name: [] for name in CSV_SCHEMA}

    for _ in range(n):
        _make_patient(rng, fake, as_of, tables)

    return tables


def _make_patient(rng, fake, as_of, tables):
    pid = _uuid(rng)
    gender = rng.choice(["M", "F"])
    first = fake.first_name_male() if gender == "M" else fake.first_name_female()
    last = fake.last_name()
    age = rng.randint(1, 95)
    birth = as_of - timedelta(days=age * 365 + rng.randint(0, 364))
    # A small fraction have died (older patients more likely).
    death = ""
    if age > 70 and rng.random() < 0.25:
        death = (birth + timedelta(days=int((age - rng.randint(0, 5)) * 365))).isoformat()

    tables["patients"].append({
        "Id": pid, "BIRTHDATE": birth.isoformat(), "DEATHDATE": death,
        "SSN": fake.ssn(), "DRIVERS": f"S{rng.randint(10000000, 99999999)}",
        "PASSPORT": f"X{rng.randint(10000000, 99999999)}X",
        "PREFIX": rng.choice(["Mr.", "Ms.", "Mrs.", "Dr.", ""]),
        "FIRST": first, "MIDDLE": fake.first_name(), "LAST": last, "SUFFIX": "",
        "MAIDEN": fake.last_name() if gender == "F" and rng.random() < 0.4 else "",
        "MARITAL": rng.choice(MARITAL) if age >= 18 else "",
        "RACE": rng.choice(RACES), "ETHNICITY": rng.choice(ETHNICITIES),
        "GENDER": gender, "BIRTHPLACE": f"{fake.city()} {fake.state_abbr()} US",
        "ADDRESS": fake.street_address().replace("\n", " "), "CITY": fake.city(),
        "STATE": "Massachusetts", "COUNTY": f"{fake.last_name()} County",
        "FIPS": str(rng.randint(25001, 25027)), "ZIP": fake.zipcode_in_state("MA"),
        "LAT": round(rng.uniform(41.3, 42.9), 6), "LON": round(rng.uniform(-73.5, -69.9), 6),
        "HEALTHCARE_EXPENSES": round(rng.uniform(1000, 250000), 2),
        "HEALTHCARE_COVERAGE": round(rng.uniform(0, 80000), 2),
        "INCOME": rng.randint(10000, 180000),
    })

    # Decide this patient's chronic conditions up front (they recur/persist).
    chronic = [c for c in vocab.CONDITIONS if c[0] in vocab.CHRONIC and rng.random() < c[2]]

    # Encounters spread across the patient's life (at least 1).
    n_enc = max(1, min(age // 3, rng.randint(1, 12)))
    enc_dates = sorted(
        birth + timedelta(days=rng.randint(0, max(1, (as_of - birth).days)))
        for _ in range(n_enc)
    )

    first_chronic_done = set()
    for i, edate in enumerate(enc_dates):
        eid = _uuid(rng)
        eclass, ecode, edesc = rng.choice(vocab.ENCOUNTER_TYPES)
        start = datetime(edate.year, edate.month, edate.day, rng.randint(8, 16), 0, 0)
        stop = start + timedelta(minutes=rng.choice([15, 20, 30, 45, 60]))
        base = round(rng.uniform(70, 160), 2)
        total = round(base + rng.uniform(0, 400), 2)
        cover = round(total * rng.uniform(0, 1), 2)
        tables["encounters"].append({
            "Id": eid, "START": _ts(start), "STOP": _ts(stop), "PATIENT": pid,
            "ORGANIZATION": _uuid(rng), "PROVIDER": _uuid(rng), "PAYER": _uuid(rng),
            "ENCOUNTERCLASS": eclass, "CODE": ecode, "DESCRIPTION": edesc,
            "BASE_ENCOUNTER_COST": base, "TOTAL_CLAIM_COST": total,
            "PAYER_COVERAGE": cover, "REASONCODE": "", "REASONDESCRIPTION": "",
        })

        # Record each chronic condition once, at its first encounter.
        for code, desc, _p in chronic:
            if code not in first_chronic_done:
                first_chronic_done.add(code)
                stop_val = "" if code in vocab.CHRONIC else _ts(stop)
                tables["conditions"].append({
                    "START": start.date().isoformat(), "STOP": stop_val,
                    "PATIENT": pid, "ENCOUNTER": eid, "SYSTEM": "SNOMED-CT",
                    "CODE": code, "DESCRIPTION": desc,
                })
                tables["careplans"].append({
                    "Id": _uuid(rng), "START": start.date().isoformat(), "STOP": "",
                    "PATIENT": pid, "ENCOUNTER": eid, "CODE": "734163000",
                    "DESCRIPTION": "Care plan (record artifact)",
                    "REASONCODE": code, "REASONDESCRIPTION": desc,
                })

        # An acute condition sometimes shows up at a visit.
        if rng.random() < 0.35:
            code, desc, _p = rng.choice([c for c in vocab.CONDITIONS if c[0] not in vocab.CHRONIC])
            tables["conditions"].append({
                "START": start.date().isoformat(), "STOP": _ts(stop + timedelta(days=rng.randint(5, 21))),
                "PATIENT": pid, "ENCOUNTER": eid, "SYSTEM": "SNOMED-CT",
                "CODE": code, "DESCRIPTION": desc,
            })

        # Vitals: most encounters record a few observations.
        for code, desc, unit, low, high in rng.sample(vocab.OBSERVATIONS, k=rng.randint(3, 6)):
            val = round(rng.uniform(low, high), 1)
            tables["observations"].append({
                "DATE": _ts(start), "PATIENT": pid, "ENCOUNTER": eid,
                "CATEGORY": "vital-signs" if unit != "%" else "laboratory",
                "CODE": code, "DESCRIPTION": desc, "VALUE": val, "UNITS": unit,
                "TYPE": "numeric",
            })

        # Medications, tied to a chronic condition the patient has.
        chronic_codes = {c[0] for c in chronic}
        for mcode, mdesc, treats in vocab.MEDICATIONS:
            if treats in chronic_codes and rng.random() < 0.5:
                base_c = round(rng.uniform(5, 80), 2)
                disp = rng.randint(1, 12)
                tables["medications"].append({
                    "START": start.date().isoformat(), "STOP": "", "PATIENT": pid,
                    "PAYER": _uuid(rng), "ENCOUNTER": eid, "CODE": mcode,
                    "DESCRIPTION": mdesc, "BASE_COST": base_c,
                    "PAYER_COVERAGE": round(base_c * rng.uniform(0, 1), 2),
                    "DISPENSES": disp, "TOTALCOST": round(base_c * disp, 2),
                    "REASONCODE": treats,
                    "REASONDESCRIPTION": next(c[1] for c in vocab.CONDITIONS if c[0] == treats),
                })

        # A procedure now and then.
        if rng.random() < 0.4:
            pcode, pdesc = rng.choice(vocab.PROCEDURES)
            tables["procedures"].append({
                "START": _ts(start), "STOP": _ts(stop), "PATIENT": pid,
                "ENCOUNTER": eid, "SYSTEM": "SNOMED-CT", "CODE": pcode,
                "DESCRIPTION": pdesc, "BASE_COST": round(rng.uniform(20, 600), 2),
                "REASONCODE": "", "REASONDESCRIPTION": "",
            })

        # Flu shot at wellness visits, sometimes.
        if eclass == "wellness" and rng.random() < 0.6:
            icode, idesc = rng.choice(vocab.IMMUNIZATIONS)
            tables["immunizations"].append({
                "DATE": _ts(start), "PATIENT": pid, "ENCOUNTER": eid,
                "CODE": icode, "DESCRIPTION": idesc, "COST": round(rng.uniform(20, 140), 2),
            })

    # A minority of patients have an allergy on file.
    if rng.random() < 0.3 and tables["encounters"]:
        acode, adesc, rcode, rdesc = rng.choice(vocab.ALLERGIES)
        enc = next(e for e in tables["encounters"] if e["PATIENT"] == pid)
        tables["allergies"].append({
            "START": enc["START"][:10], "STOP": "", "PATIENT": pid,
            "ENCOUNTER": enc["Id"], "CODE": acode, "SYSTEM": "SNOMED-CT",
            "DESCRIPTION": adesc, "TYPE": "allergy", "CATEGORY": "environment",
            "REACTION1": rcode, "DESCRIPTION1": rdesc,
            "SEVERITY1": rng.choice(["MILD", "MODERATE", "SEVERE"]),
            "REACTION2": "", "DESCRIPTION2": "", "SEVERITY2": "",
        })
