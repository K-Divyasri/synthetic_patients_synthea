"""Take a FHIR Bundle apart so you can see how it's built.

A Bundle is just a list of `entry` objects. Each entry has a `resource` with a
`resourceType` (Patient, Encounter, Observation, ...) and the resources point at
each other with `reference` strings like "urn:uuid:1234". These three functions
let you answer: what's in this bundle, how is it wired together, and do all the
references actually resolve to something inside the bundle.
"""
from __future__ import annotations

from collections import Counter

# Fields that commonly hold a reference to another resource.
_REF_FIELDS = ["subject", "patient", "encounter"]


def resource_counts(bundle) -> Counter:
    """How many of each resource type are in the bundle."""
    counts: Counter = Counter()
    for entry in bundle.get("entry", []):
        counts[entry["resource"]["resourceType"]] += 1
    return counts


def reference_edges(bundle):
    """List the wiring: (from_resource_type, field, target_reference)."""
    edges = []
    for entry in bundle.get("entry", []):
        res = entry["resource"]
        rt = res["resourceType"]
        for field in _REF_FIELDS:
            val = res.get(field)
            if isinstance(val, dict) and "reference" in val:
                edges.append((rt, field, val["reference"]))
    return edges


def unresolved_references(bundle):
    """Return any references that don't point at a resource in this bundle.
    An empty list means the bundle is internally consistent."""
    have = {entry.get("fullUrl") for entry in bundle.get("entry", [])}
    return [(rt, field, ref) for rt, field, ref in reference_edges(bundle)
            if ref not in have]
