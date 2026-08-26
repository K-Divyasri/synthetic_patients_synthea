"""Load a folder of Synthea CSVs into pandas DataFrames.

Works on output from the mini generator AND from real Synthea - they share the
same filenames and columns. We read every column as text (so an id never gets
turned into a float and an empty cell stays an empty string), and upper-case the
headers so the rest of the code can rely on one casing. Real Synthea writes "Id"
but everything else upper-case; normalising avoids a class of annoying bugs.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_synthea(csv_dir) -> dict:
    """Return {table_name: DataFrame} for every CSV in csv_dir. Table name is the
    filename without extension, lower-cased (e.g. 'patients')."""
    d = Path(csv_dir)
    if not d.exists():
        raise FileNotFoundError(f"No such folder: {d}")
    tables = {}
    for f in sorted(d.glob("*.csv")):
        df = pd.read_csv(f, dtype=str, keep_default_na=False)
        df.columns = [c.upper() for c in df.columns]
        tables[f.stem.lower()] = df
    if not tables:
        raise FileNotFoundError(f"No CSV files found in {d}")
    return tables
