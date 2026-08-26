# synthea_explorer - generate and profile a synthetic patient population

Generates a synthetic EHR dataset in Synthea's exact shape, then loads and
profiles it: population stats, per-patient timelines, and the anatomy of a
FHIR bundle.

> Synthetic data only. The data here is invented (no real patients). The mini
> generator is a Java-free stand-in for Synthea; for the genuine tool see
> `run_real_synthea.md`. The explorer reads real Synthea output unchanged.

## Two packages

```
synthea_mini/        A schema-faithful Synthea stand-in (no Java needed).
├── vocab.py         Real SNOMED / LOINC / RxNorm / CVX codes.
├── generate.py      Build a population in Synthea's exact CSV columns.
└── fhir.py          Assemble one patient's FHIR R4 transaction Bundle.

synthea_explorer/    Works on mini OR real Synthea output (same schema).
├── load.py          Read the CSV folder into DataFrames (normalised headers).
├── population.py    Counts, demographics, top conditions/meds, encounters/patient.
├── timeline.py      One patient's events across all files, in date order.
├── fhir_anatomy.py  Resource counts + reference wiring of a bundle.
└── report.py        Render the Markdown reports.
```

## Run it

```powershell
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python generate_sample.py     # writes data/sample/csv/*.csv + a FHIR bundle
python generate_report.py     # writes data/sample/reports/*.md
pytest                        # 12 tests
```

## What it covers

- The shape of an EHR: patients, encounters, and the clinical facts (conditions,
  observations, medications, procedures, immunizations) that hang off encounters,
  all linked by ids. See `data/sample/reports/population_report.md`.
- Coding systems: SNOMED CT (conditions/procedures), LOINC (observations), RxNorm
  (medications), CVX (vaccines) - the same vocabularies real systems use.
- What a FHIR Bundle is and how its resources reference each other. See
  `data/sample/reports/fhir_anatomy.md`.
- Why synthetic data exists and why real PHI never belongs in a public repo.

## Honest scope

The mini generator reproduces Synthea's *format* faithfully, not its clinical
realism - it won't model disease progression the way the real simulator does.
That's deliberate: it makes the project run anywhere with no Java, while teaching
the data model that actually transfers. Run the real Synthea (`run_real_synthea.md`)
when you want clinically realistic histories; the same explorer code handles it.
