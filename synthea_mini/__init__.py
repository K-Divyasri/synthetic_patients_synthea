"""synthea_mini - a schema-faithful stand-in for Synthea (no Java needed).

Generates patient data in Synthea's exact CSV shape, plus a FHIR R4 Bundle, so the
rest of the project runs anywhere and the explorer code also works on REAL Synthea
output. See run_real_synthea.md for the genuine article.
"""
from .generate import generate_population, write_tables, CSV_SCHEMA
from .fhir import build_patient_bundle

__all__ = ["generate_population", "write_tables", "CSV_SCHEMA", "build_patient_bundle"]
