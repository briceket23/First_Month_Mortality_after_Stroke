"""Generate a fully synthetic registry workbook with the real column names and codings, so that the whole pipeline can be
exercised online (Binder/Colab/CI) without any patient data.  Nothing here is derived from real records: values are drawn
from parametric distributions chosen to mimic the registry's *structure* (coding conventions, missingness that changes by
period, duplicate identifiers, invalid dates, undocumented codes), not its results.

    python scripts/make_synthetic_fixture.py [N] [SEED]  -> data/synthetic_fixtures/synthetic_registry.xlsx (+ .md5)
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import os
os.environ.setdefault("STROKE_SYNTHETIC", "1")       # config resolves the fixture path; the file is created below
from stroke_repro.registry import RAW_FIELDS  # noqa: E402

COLUMNS_FILE = ROOT / "config" / "workbook_columns.txt"   # the 251 real header names (no data)


def main(n=900, seed=7):
    rng = np.random.default_rng(seed)
    cols = [c.strip() for c in COLUMNS_FILE.read_text(encoding="utf-8").splitlines() if c.strip()]
    df = pd.DataFrame(index=range(n), columns=cols, dtype=object)
    year = rng.choice(np.arange(2010, 2024), n, p=np.r_[np.full(7, 0.09), np.full(7, (1 - 0.63) / 7)])
    entry = pd.to_datetime({"year": year, "month": rng.integers(1, 13, n), "day": rng.integers(1, 29, n)})
    age = np.clip(rng.normal(60, 14, n), 19, 95).round()
    male = rng.random(n) < 0.55
    sev = rng.normal(0, 1, n)                                   # latent severity
    nihss = np.clip((9 + 6 * sev + rng.normal(0, 3, n)).round(), 0, 40)
    gcs = np.clip((13 - 2.5 * sev + rng.normal(0, 1.5, n)).round(), 3, 15)
    hem = rng.random(n) < 0.38
    p_death = 1 / (1 + np.exp(-(-1.3 + 1.4 * sev + 0.5 * hem + 0.02 * (age - 60))))
    died_inhosp = rng.random(n) < p_death * 0.75
    los = np.where(died_inhosp, rng.gamma(1.6, 3.0, n), rng.gamma(2.5, 3.2, n)).round().clip(0, 70)
    release = entry + pd.to_timedelta(los, unit="D")
    post_death = (~died_inhosp) & (rng.random(n) < 0.05)
    recorded_m1 = rng.random(n) < np.where(year <= 2014, 0.9, np.where(year <= 2016, 0.6, 0.25))
    # from 2015 in-hospital deaths are mostly NOT written into death1 (structural feature of the registry)
    d1 = np.where(died_inhosp, np.where(year <= 2014, "Yes", np.where(rng.random(n) < 0.05, "Yes", None)),
                  np.where(post_death, "Yes", np.where(recorded_m1, "No", None)))
    df["unique_code"] = [f"S{rng.integers(0, 26)}{rng.integers(0, 26)}{d:%Y-%m-%d}" for d in entry]
    df["Date of entry"] = entry
    df["Release date"] = release
    df["Length of hospitalization"] = los.astype(int)
    df["age"] = age
    df["sex"] = np.where(male, "male", "female")
    df["diagnostic"] = np.where(hem, "AVCH", np.where(rng.random(n) < 0.03, "AIT", "AVCI"))
    df["Become after leaving UNV"] = np.where(died_inhosp, "death", np.where(rng.random(n) < 0.08, "Other", "RAD"))
    df["Cause of death"] = np.where(died_inhosp, rng.choice(["sepsis", "mixed causes", "brain engagement", "0"], n), None)
    df["death1"] = d1
    later = (~died_inhosp) & recorded_m1 & (rng.random(n) < np.where(year <= 2016, 0.8, 0.15))
    df["death3"] = np.where(later, np.where(rng.random(n) < 0.06, "Yes", "No"), None)
    df["duration followed1"] = np.where(recorded_m1, np.where(year <= 2016, 1, 30), None)
    df["duration followed3"] = np.where(later, np.where(year <= 2016, 3, 90), None)
    miss = lambda p: rng.random(n) < p
    def put(col, vals, p_missing):
        df[col] = np.where(miss(p_missing), None, vals)
    put("NIHSS score", nihss, 0.4); put("glagow score", gcs, 0.12); put("Modified Rankin score", np.clip((3 + sev).round(), 0, 5), 0.45)
    put("Systolic BP", (150 + 25 * rng.normal(size=n)).round(), 0.1); put("Diastolic BP", (90 + 15 * rng.normal(size=n)).round(), 0.1)
    put("cardiac frequency", (85 + 15 * rng.normal(size=n)).round(), 0.15); put("respiratory rate", (20 + 4 * rng.normal(size=n)).round(), 0.3)
    put("temperature", (37 + 0.8 * rng.normal(size=n)).round(1), 0.2); put("SA O2", (96 + 3 * rng.normal(size=n)).round(), 0.7)
    put("Body mass index", (26 + 4 * rng.normal(size=n)).round(1), 0.9); put("capillary blood sugar", np.abs(1.3 + 0.6 * rng.normal(size=n)).round(2), 0.25)
    put("creatinine", np.abs(12 + 6 * rng.normal(size=n)).round(1), 0.3); put("uremia", np.abs(0.4 + 0.2 * rng.normal(size=n)).round(2), 0.35)
    put("Total cholesterol", np.abs(1.9 + 0.5 * rng.normal(size=n)).round(2), 0.4); put("Tx Hb", (12.5 + 2 * rng.normal(size=n)).round(1), 0.2)
    put("GB blood", np.abs(8 + 3 * rng.normal(size=n)).round(1), 0.2); put("Blood platelets", np.abs(250 + 80 * rng.normal(size=n)).round(), 0.2)
    put("CRP", np.abs(25 + 40 * rng.normal(size=n)).round(), 0.45); put("Na+", (138 + 5 * rng.normal(size=n)).round(), 0.3); put("K+", (4 + 0.6 * rng.normal(size=n)).round(1), 0.3)
    for c, p in [("HISTORY of hypertension", 0.7), ("Diabetes ATCD", 0.2), ("Smoking", 0.15), ("ATCD of heart disease", 0.12),
                 ("ATCD of atrial fibrillation", 0.08), ("Stroke ATCD", 0.15)]:
        df[c] = np.where(miss(0.05), None, np.where(rng.random(n) < p, "Yes", "No"))
    arrival = np.where(rng.random(n) < 0.45, rng.choice([24, 48, 72, 96, 120], n), rng.integers(1, 20, n)).astype(float)
    df["HGD arrival time"] = np.where(miss(0.3), None, arrival)        # onset-to-arrival delay (hours; heaped at multiples of 24)
    df["illness-consultation start time"] = np.where(miss(0.3), None, (arrival * 0.8).round())
    df["Ischemik stroke on scanner"] = np.where(hem, "No", "Yes"); df["Stroke Hemorrhagic"] = np.where(hem, "Yes", "No")
    # structural defects on purpose: duplicate identifiers, invalid dates, LOS code 99, undocumented codes
    dup = rng.choice(n, 20, replace=False)
    extra = df.iloc[dup].copy()
    extra.iloc[:10, extra.columns.get_loc("death1")] = None            # partner rows missing month-1 status
    extra.iloc[10:15, extra.columns.get_loc("NIHSS score")] = 3          # conflicting predictor
    extra.iloc[15:18, extra.columns.get_loc("sex")] = "female"           # identifier collision
    df = pd.concat([df, extra], ignore_index=True)
    df.loc[rng.choice(len(df), 3, replace=False), "Length of hospitalization"] = 99
    i = rng.choice(len(df), 2, replace=False)
    df.loc[i[0], "Release date"] = pd.Timestamp("2916-05-01"); df.loc[i[1], "Date of entry"] = pd.Timestamp("3016-05-01")
    df["death1"] = df["death1"].astype(object); df.loc[rng.choice(len(df), 2, replace=False), "death1"] = 9
    df.loc[rng.choice(len(df), 4, replace=False), "Release date"] = df["Date of entry"].iloc[0] - pd.Timedelta(days=3)
    out = ROOT / "data" / "synthetic_fixtures" / "synthetic_registry.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(out, index=False, sheet_name="Feuil1")
    md5 = hashlib.md5(out.read_bytes()).hexdigest()
    (out.with_suffix(".md5")).write_text(md5 + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(df)} rows x {df.shape[1]} cols), md5 {md5}")
    assert set(RAW_FIELDS) <= set(df.columns)


if __name__ == "__main__":
    main(*(int(a) for a in sys.argv[1:3]))
