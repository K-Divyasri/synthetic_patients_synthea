"""Generate the sample dataset this project ships with.

Writes Synthea-shaped CSVs to data/sample/csv/ and one patient's FHIR bundle to
data/sample/fhir/. Run this once; the notebooks, labs, and reports read what it
produces. Re-running gives identical output (it's seeded).

    python generate_sample.py
"""
from __future__ import annotations

import json
from pathlib import Path

from synthea_mini import generate_population, write_tables, build_patient_bundle
from synthea_explorer import summarize, patient_with_most_encounters, load_synthea

N_PATIENTS = 25
SEED = 12


def main():
    here = Path(__file__).parent
    csv_dir = here / "data" / "sample" / "csv"
    fhir_dir = here / "data" / "sample" / "fhir"
    fhir_dir.mkdir(parents=True, exist_ok=True)

    tables = generate_population(n=N_PATIENTS, seed=SEED)
    write_tables(tables, csv_dir)
    print(f"Wrote {len(tables)} CSV files to {csv_dir}")

    # Pick the patient with the richest history and export their FHIR bundle.
    loaded = load_synthea(csv_dir)
    pid = patient_with_most_encounters(loaded)
    bundle = build_patient_bundle(tables, pid)
    out = fhir_dir / f"{pid}.json"
    out.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    print(f"Wrote FHIR bundle for patient {pid} ({len(bundle['entry'])} entries) to {out}")

    s = summarize(loaded)
    print(f"\nPopulation: {s['n_patients']} patients, {s['n_encounters']} encounters "
          f"({s['encounters_per_patient']} each)")
    print("Reminder: this is synthetic data. Never put real patient data in a repo.")


if __name__ == "__main__":
    main()
