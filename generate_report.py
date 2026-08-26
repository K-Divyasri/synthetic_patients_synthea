"""Profile the sample dataset and write the Markdown reports.

    python generate_report.py

Reads data/sample/csv + data/sample/fhir and writes:
  data/sample/reports/population_report.md
  data/sample/reports/fhir_anatomy.md
"""
from __future__ import annotations

import json
from pathlib import Path

from synthea_explorer import (load_synthea, summarize, render_population_report,
                              render_fhir_anatomy, unresolved_references)


def main():
    here = Path(__file__).parent
    csv_dir = here / "data" / "sample" / "csv"
    fhir_dir = here / "data" / "sample" / "fhir"
    reports = here / "data" / "sample" / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    if not csv_dir.exists():
        raise SystemExit("No sample data. Run: python generate_sample.py first.")

    tables = load_synthea(csv_dir)
    (reports / "population_report.md").write_text(
        render_population_report(summarize(tables)), encoding="utf-8")
    print(f"Wrote {reports / 'population_report.md'}")

    bundles = sorted(fhir_dir.glob("*.json"))
    if bundles:
        bundle = json.loads(bundles[0].read_text(encoding="utf-8"))
        (reports / "fhir_anatomy.md").write_text(
            render_fhir_anatomy(bundle), encoding="utf-8")
        missing = unresolved_references(bundle)
        print(f"Wrote {reports / 'fhir_anatomy.md'}")
        print(f"Bundle reference check: {'all resolve' if not missing else f'{len(missing)} unresolved'}")


if __name__ == "__main__":
    main()
