"""synthea_explorer - load and profile a Synthea dataset (mini or real).

    from synthea_explorer import load_synthea, summarize, patient_timeline
"""
from .load import load_synthea
from .population import summarize, patient_with_most_encounters
from .timeline import patient_timeline
from .fhir_anatomy import resource_counts, reference_edges, unresolved_references
from .report import render_population_report, render_fhir_anatomy

__all__ = [
    "load_synthea",
    "summarize", "patient_with_most_encounters",
    "patient_timeline",
    "resource_counts", "reference_edges", "unresolved_references",
    "render_population_report", "render_fhir_anatomy",
]
