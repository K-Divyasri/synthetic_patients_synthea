# Running the real Synthea (the genuine article)

The mini generator in this folder writes data in Synthea's exact shape so you can
learn with zero setup. But you should run the real Synthea at least once - it's the
tool the roadmap leans on, and "I've generated populations with Synthea" is a real
line on your resume. The good news: the explorer, notebooks, and labs all read real
Synthea output without a single code change, because the schema is identical.

Real Synthea is a Java program (no pip install). Here's the whole process.

## 1. Install Java (17 or newer)

Synthea needs a Java runtime. Install Temurin (the free, standard OpenJDK build):

- Download from <https://adoptium.net/> (pick the latest LTS, version 17 or newer).
- During install, let it set JAVA_HOME / add Java to PATH.
- Open a NEW PowerShell window and check:

  ```powershell
  java -version
  ```

  You should see a version line. If "java is not recognized," reopen PowerShell
  (PATH changes need a fresh terminal), or reinstall with the PATH option ticked.

## 2. Get Synthea

The easiest route is the pre-built jar - no compiling.

- Go to the releases page: <https://github.com/synthetichealth/synthea/releases>
- Download `synthea-with-dependencies.jar` from the latest release.
- Put it in a working folder, e.g. the repo root. (It's already
  in `.gitignore` - the jar is large and shouldn't go in your repo.)

(Alternatively, clone the repo and use the `run_synthea` script - see the official
Basic Setup wiki: <https://github.com/synthetichealth/synthea/wiki/Basic-Setup-and-Running>.)

## 3. Generate a population

Generate, say, 100 living patients in Massachusetts, with CSV export turned on
(FHIR is on by default; CSV is not):

```powershell
java -jar synthea-with-dependencies.jar -p 100 --exporter.csv.export true Massachusetts
```

Useful flags (full list on the wiki):

- `-p 100` - population size (living patients).
- `-s 12` - random seed, for reproducible runs.
- `-a 18-65` - age range.
- `-g F` - gender.
- the trailing `Massachusetts` (and an optional city) sets the location.

Output lands in a new `./output/` folder:

- `./output/csv/` - the CSV files (patients.csv, encounters.csv, ...).
- `./output/fhir/` - one FHIR R4 Bundle per patient (plus hospital/practitioner bundles).

## 4. Explore the real output with this project's code

Point the explorer at the real CSV folder - same code, real data:

```powershell
.\.venv\Scripts\python.exe -c "from synthea_explorer import load_synthea, summarize; import json; print(json.dumps(summarize(load_synthea('output/csv')), indent=2, default=str))"
```

Or open any notebook and change the data path from the sample folder to
`output/csv`. Everything else just works.

## A note on scale and git

- 100 patients is plenty for learning. 1,000+ gets slow and large.
- NEVER commit the full output - it's big, and the habit of "generated data stays
  out of git" is the same one you'll use with real PHI. Commit only a tiny sample
  (this project ships ~25 patients under `data/sample/`).

## Docs

- Synthea home: <https://synthetichealth.github.io/synthea/>
- Getting started wiki: <https://github.com/synthetichealth/synthea/wiki/Getting-Started>
- CSV data dictionary: <https://github.com/synthetichealth/synthea/wiki/CSV-File-Data-Dictionary>
