"""Central configuration for the NEURI-D-26-00184 revision re-analysis.

All analytic decisions that affect cohort, endpoint or modelling are declared here.
Paths are relative to the revision root (parent of this file's folder).
"""
from pathlib import Path

import os
ROOT = Path(__file__).resolve().parents[2]           # project root (src/stroke_repro/config.py)
_raw = None
if os.environ.get("STROKE_SYNTHETIC") == "1":                                # the fixture always wins: tests and demos never touch registry data
    _raw = str(ROOT / "data" / "synthetic_fixtures" / "synthetic_registry.xlsx")
_raw = _raw or os.environ.get("STROKE_DATA_PATH") or os.environ.get("STROKE_RAW_XLSX")
if not _raw and (ROOT / "data" / "raw" / "database_stroke_copy.xlsx").exists():
    _raw = str(ROOT / "data" / "raw" / "database_stroke_copy.xlsx")        # local secure copy (git-ignored)
if not _raw:
    raise SystemExit("Set STROKE_DATA_PATH to the registry workbook, place it in data/raw/ (git-ignored), or set STROKE_SYNTHETIC=1 to use the synthetic fixture.")
RAW_XLSX = Path(_raw)
SYNTHETIC = os.environ.get("STROKE_SYNTHETIC") == "1"

import yaml  # noqa: E402
YAML = {n: yaml.safe_load((ROOT / "config" / f"{n}.yaml").read_text(encoding="utf-8"))
        for n in ("project", "registry_schema", "outcome_definition", "preprocessing", "modelling", "analysis_plan")}
OUTCOME_APPROVAL_STATE = YAML["outcome_definition"]["approval_state"]
RAW_MD5 = "08541ef199c1656c184291f24b4cc3e3"      # md5 of the analysed workbook (1,653 x 251)

RESTRICTED = ROOT / "data" / "processed"           # row-level files (git-ignored): NOT for distribution
OUT = ROOT / "outputs"
LOGS, MANIFESTS, REPORTS = OUT / "logs", OUT / "manifests", OUT / "reports"
AUDIT, COHORT, ANALYSIS = OUT / "audit", OUT / "cohort", OUT / "analysis"
FIG, TAB = OUT / "figures", OUT / "tables"
for _d in (RESTRICTED, AUDIT, COHORT, ANALYSIS, FIG, TAB, LOGS, MANIFESTS, REPORTS):
    _d.mkdir(parents=True, exist_ok=True)

SEED = 20261016

# ----------------------------------------------------------------- record integrity
VALID_ENTRY_YEARS = (2010, 2023)          # registry span observed in the workbook
VALID_RELEASE_YEARS = (2010, 2024)
LOS_MISSING_CODES = {99.0}                # 99 is used as a missing-value code throughout the workbook
LOS_MAX_PLAUSIBLE = 120
LOS_AGREEMENT_TOL = 2                     # days; recorded LOS vs date-derived elapsed days
SHIFT_JUNK_MIN = 3                        # >= this many numeric codes in Yes/No fields => column misalignment

# ----------------------------------------------------------------- duplicates
DUP_AGE_DIFF_DISTINCT = 5                 # |age difference| > 5 y, or sex conflict => identifier collision
DUP_LOS_TOL = 1
DUP_OUTCOME_FIELDS = ["death1", "death3", "death6", "death9", "disp", "los_recorded", "release_date"]

# ----------------------------------------------------------------- endpoint
WINDOW_DAYS = 30                          # day 0 = admission (Date of entry); event if elapsed days <= 30
EXCLUDED_DIAGNOSES = {"AIT"}              # transient ischaemic attack is not stroke

# ----------------------------------------------------------------- predictors (admission-time only)
NUMERIC = ["age", "nihss", "gcs", "mrs", "sbp", "dbp", "heart_rate", "resp_rate", "temperature",
           "spo2", "glucose_cap", "creatinine", "urea", "total_cholesterol", "hemoglobin",
           "wbc", "platelets", "crp", "sodium", "potassium"]
BINARY = ["male", "hypertension", "diabetes", "smoking", "heart_disease", "atrial_fib",
          "prior_stroke", "hemorrhagic"]
MAX_MISSING_FOR_PREDICTOR = 0.60          # predictors more missing than this in the cohort are not used
CLINICAL_REFERENCE = ["age", "nihss", "gcs", "mrs", "hemorrhagic", "male"]

# ----------------------------------------------------------------- validation
OUTER_FOLDS, OUTER_REPEATS = 5, 5
INNER_FOLDS = 3
BOOTSTRAP_N = 1000
RISK_TIERS = (0.10, 0.40)                 # pre-specified absolute-risk cut-points: <10% low, >=40% high
DCA_RANGE = (0.05, 0.50)

# ----------------------------------------------------------------- data dictionary (received 2 Nov 2026)
def _find_dictionary():
    """Dictionary lookup order: STROKE_DICT_PATH; data/raw/ (xlsx or the semicolon/cp1252 CSV, either spelling of the name);
    the copy shipped in dictionary/."""
    if os.environ.get("STROKE_DICT_PATH"):
        return Path(os.environ["STROKE_DICT_PATH"])
    for n in ("stroke_data_dictionary.xlsx", "stroke_data_dictionnary.xlsx", "database_stroke_dict.csv", "stroke_data_dictionary.csv"):
        if (ROOT / "data" / "raw" / n).exists():
            return ROOT / "data" / "raw" / n
    return ROOT / "dictionary" / "stroke_data_dictionary.xlsx"


DICT_XLSX = _find_dictionary()
DICT_MD5 = "be778aa084720376bdc1c27392a260af"                         # shipped xlsx dictionary (2 Nov 2026)
DICT_KNOWN_MD5 = {"be778aa084720376bdc1c27392a260af": "stroke_data_dictionary.xlsx (2 Nov 2026)",
                  "e7c33acfe3e3d616d68344aa26a3c63f": "database_stroke_dict.csv (cp1252, ';'; same content)"}


def load_dictionary():
    """Return the dictionary as a DataFrame with columns category/name/type/label/description, whatever the file format."""
    import pandas as pd
    if DICT_XLSX.suffix.lower() == ".csv":
        d = pd.read_csv(DICT_XLSX, sep=";", encoding="cp1252", dtype=str, keep_default_na=False)
        d = d[d.apply(lambda r: any(str(v).strip() for v in r), axis=1)]
        d.columns = ["name", "type", "label", "description"][:len(d.columns)]
        d.insert(0, "category", None)
    else:
        d = pd.read_excel(DICT_XLSX, sheet_name=0)
        d.columns = ["category", "name", "type", "label", "description"][:len(d.columns)]
    d["category"] = d["category"].ffill()
    return d
# Sensitivity for a stroke-anchored month-1 window (dictionary wording "after the stroke"): a death1 = No
# then certifies survival to onset + 1 month, which can end before admission + 30 d by the onset-to-arrival
# delay.  'HGD arrival time' has no documented unit; values heap at 24/48/72, read here as HOURS (assumption).
ONSET_GAP_HOURS = 72

# consistency between the declared plan (YAML) and the executable constants
assert sorted(YAML["preprocessing"]["candidate_predictors"]) == sorted(NUMERIC + BINARY), "preprocessing.yaml candidate list differs from config.py"
assert YAML["modelling"]["clinical_reference"] == CLINICAL_REFERENCE and YAML["modelling"]["seed"] == SEED
assert tuple(YAML["modelling"]["risk_tiers"]["cut_points"]) == RISK_TIERS
assert YAML["modelling"]["nested_cv"] == {"outer_folds": OUTER_FOLDS, "outer_repeats": OUTER_REPEATS, "inner_folds": INNER_FOLDS}
