"""Render the explorer's findings as Markdown - the "anatomy of an EHR" write-up
that goes in your repo and tells a recruiter you understand clinical data."""
from __future__ import annotations

from .fhir_anatomy import resource_counts, reference_edges


def render_population_report(summary) -> str:
    L = []
    L.append("# Synthetic population report")
    L.append("")
    L.append("Generated from synthetic data only - no real patients.")
    L.append("")
    L.append(f"- Patients: {summary['n_patients']}")
    L.append(f"- Encounters: {summary['n_encounters']} "
             f"({summary['encounters_per_patient']} per patient)")
    if summary["age_stats"]:
        a = summary["age_stats"]
        L.append(f"- Age: min {a['min']}, mean {a['mean']}, max {a['max']}")
    L.append("")

    L.append("## Demographics")
    L.append("")
    L.append("Gender: " + ", ".join(f"{k}={v}" for k, v in summary["gender"].items()))
    L.append("")
    L.append("Race: " + ", ".join(f"{k}={v}" for k, v in summary["race"].items()))
    L.append("")

    L.append("## Encounters by class")
    L.append("")
    for k, v in summary["encounter_class"].items():
        L.append(f"- {k}: {v}")
    L.append("")

    L.append("## Top conditions")
    L.append("")
    for desc, n in summary["top_conditions"].items():
        L.append(f"- {desc}: {n}")
    L.append("")

    L.append("## Top medications")
    L.append("")
    for desc, n in summary["top_medications"].items():
        L.append(f"- {desc}: {n}")
    L.append("")

    L.append("## Files loaded")
    L.append("")
    for name, n in summary["tables_loaded"].items():
        L.append(f"- {name}.csv: {n} rows")
    L.append("")
    return "\n".join(L)


def render_fhir_anatomy(bundle) -> str:
    counts = resource_counts(bundle)
    edges = reference_edges(bundle)
    L = []
    L.append("# Anatomy of a FHIR bundle")
    L.append("")
    L.append(f"This bundle is a `{bundle.get('type', '?')}` Bundle with "
             f"{len(bundle.get('entry', []))} entries.")
    L.append("")
    L.append("## Resource types in the bundle")
    L.append("")
    for rt, n in counts.most_common():
        L.append(f"- {rt}: {n}")
    L.append("")
    L.append("## How resources reference each other")
    L.append("")
    L.append("Each line is: a resource -> the field -> what it points at.")
    L.append("")
    seen = set()
    for rt, field, ref in edges:
        key = (rt, field)
        if key in seen:
            continue
        seen.add(key)
        L.append(f"- {rt}.{field} -> {ref.split(':')[0]}:... (another resource in the bundle)")
    L.append("")
    return "\n".join(L)
