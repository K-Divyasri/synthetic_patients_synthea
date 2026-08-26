"""Small, real code sets so our synthetic data speaks the SAME languages a real
EHR (and real Synthea) speaks:

  - SNOMED CT  -> conditions and procedures ("what's wrong", "what was done")
  - LOINC      -> observations (labs and vital signs)
  - RxNorm     -> medications
  - CVX        -> vaccines

These are tiny curated subsets - real Synthea draws on thousands of codes - but
every code below is a genuine one. So when you later query real Synthea output, or
a real warehouse, the codes look familiar and what you learned here transfers.
"""

# (SNOMED code, description, rough lifetime probability) - chronic ones persist.
CONDITIONS = [
    ("59621000",  "Essential hypertension (disorder)",            0.30),
    ("44054006",  "Type 2 diabetes mellitus (disorder)",          0.18),
    ("195967001", "Asthma (disorder)",                            0.12),
    ("162864005", "Body mass index 30+ - obesity (finding)",      0.28),
    ("15777000",  "Prediabetes (finding)",                        0.15),
    ("10509002",  "Acute bronchitis (disorder)",                  0.22),
    ("444814009", "Viral sinusitis (disorder)",                   0.35),
    ("43878008",  "Streptococcal sore throat (disorder)",         0.10),
    ("82423001",  "Chronic pain (finding)",                       0.08),
]
# Which conditions are chronic (no STOP date - they stay with the patient).
CHRONIC = {"59621000", "44054006", "195967001", "162864005", "15777000", "82423001"}

# (LOINC code, description, unit, low, high) - vitals and labs measured at visits.
OBSERVATIONS = [
    ("8302-2",  "Body Height",                                       "cm",     150, 190),
    ("29463-7", "Body Weight",                                       "kg",      50, 110),
    ("39156-5", "Body mass index (BMI) [Ratio]",                     "kg/m2",   18,  38),
    ("8480-6",  "Systolic Blood Pressure",                          "mm[Hg]",  100, 160),
    ("8462-4",  "Diastolic Blood Pressure",                         "mm[Hg]",   60, 100),
    ("8867-4",  "Heart rate",                                        "/min",     55, 100),
    ("4548-4",  "Hemoglobin A1c/Hemoglobin.total in Blood",         "%",        4.5, 9.5),
    ("2339-0",  "Glucose [Mass/volume] in Blood",                    "mg/dL",    70, 180),
    ("2093-3",  "Cholesterol [Mass/volume] in Serum or Plasma",     "mg/dL",   130, 260),
]

# (RxNorm code, description) and which SNOMED condition each tends to treat.
MEDICATIONS = [
    ("860975", "metformin hydrochloride 500 MG Oral Tablet",            "44054006"),
    ("314076", "lisinopril 10 MG Oral Tablet",                          "59621000"),
    ("197361", "amlodipine 5 MG Oral Tablet",                           "59621000"),
    ("308136", "albuterol 0.09 MG/ACTUAT metered dose inhaler",         "195967001"),
    ("308182", "amoxicillin 500 MG Oral Capsule",                       "43878008"),
    ("311036", "acetaminophen 325 MG Oral Tablet",                      "82423001"),
]

# (SNOMED code, description) - things done at a visit.
PROCEDURES = [
    ("430193006", "Medication reconciliation (procedure)"),
    ("5880005",   "Physical examination procedure (procedure)"),
    ("117015009", "Throat culture (procedure)"),
    ("710841007", "Assessment of anxiety (procedure)"),
]

# (CVX code, description) - vaccines.
IMMUNIZATIONS = [
    ("140", "Influenza, seasonal, injectable, preservative free"),
    ("113", "Td (adult) preservative free"),
    ("33",  "pneumococcal polysaccharide vaccine, 23 valent"),
]

# (encounter class, SNOMED code, description). EncounterClass is Synthea's own
# small vocabulary (wellness/ambulatory/outpatient/emergency/urgentcare).
ENCOUNTER_TYPES = [
    ("wellness",   "162673000", "General examination of patient (procedure)"),
    ("ambulatory", "185349003", "Encounter for check up (procedure)"),
    ("outpatient", "185345009", "Encounter for symptom (procedure)"),
    ("emergency",  "50849002",  "Emergency room admission (procedure)"),
    ("urgentcare", "702927004", "Urgent care clinic (procedure)"),
]

# (SNOMED code, description) allergens, plus their reaction.
ALLERGIES = [
    ("419263009", "Allergy to tree pollen (finding)",   "21626009",  "Cutaneous hypersensitivity (finding)"),
    ("232347008", "Dander (animal) allergy (finding)",  "76067001",  "Sneezing (finding)"),
    ("91934008",  "Allergy to nut (finding)",           "271807003", "Eruption of skin (disorder)"),
]
