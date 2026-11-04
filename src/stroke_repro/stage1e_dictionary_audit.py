"""Stage 1e: audit of the registry data dictionary received on 2 Nov 2026 (aggregate outputs only).

1. conformance between dictionary and workbook (coverage, absent variables, missing types, hedged wording, value codes);
2. the dictionary's definitions of every outcome-defining field, quoted verbatim;
3. what the dictionary settles for each question of the registry clarification request;
4. checks of the data against the dictionary definition of death1 ("passed away within the first month"),
   by admission period, and of the follow-up duration fields' units;
5. onset-to-arrival delay distribution (relevant if the month-1 window starts at the stroke).
"""
import json
import re

import numpy as np
import pandas as pd

from . import config as C
from .registry import load_raw, md5


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def period(y):
    return pd.cut(y, [2009, 2012, 2014, 2016, 2019, 2020, 2023], labels=["2010-12", "2013-14", "2015-16", "2017-19", "2020", "2021-23"])


def main():
    dmd5 = md5(C.DICT_XLSX)
    if dmd5 not in C.DICT_KNOWN_MD5:
        print(f"WARNING: dictionary {C.DICT_XLSX.name} has an unrecorded checksum {dmd5}; audited as supplied")
    d = C.load_dictionary()
    raw = load_raw()
    wl = {norm(c) for c in raw.columns}
    d["in_workbook"] = d.label.map(lambda s: norm(s) in wl)
    hedge = d.description.astype(str).str.contains(r"\b(?:likely|possibly|typically|may|might|perhaps|probably)\b", case=False)
    codes = d.description.astype(str).str.contains(r"\d\s*=|coded as \d|\d\s*:\s*\w", regex=True)
    conf = {
        "dictionary_file": C.DICT_XLSX.name, "dictionary_md5": dmd5, "dictionary_known": dmd5 in C.DICT_KNOWN_MD5, "dictionary_rows": int(len(d)), "workbook_columns": int(len(raw.columns) - 2),
        "dictionary_labels_matched_exactly": int(d.in_workbook.sum()),
        "dictionary_variables_not_in_workbook": d.loc[~d.in_workbook, ["name", "label"]].values.tolist(),
        "workbook_columns_not_matched_exactly": [c for c in raw.columns[2:] if norm(c) not in {norm(x) for x in d.label}],
        "variables_without_type": int(d.type.isna().sum()),
        "descriptions_with_hedging_words": d.loc[hedge, "name"].tolist(),
        "descriptions_with_value_codes": int(codes.sum()),
        "categories": d.category.value_counts().to_dict(),
    }
    # verbatim definitions of outcome-defining and timing fields
    keys = ["datentré", "datesor", "datesort1", "duréehos", "devenir", "caudece", "rankin", "délaicon", "délaihgd",
            "dursuiv1", "décès1", "barthel1", "rankin1", "dursuiv3", "décès3", "ranki_m3", "décès6", "décès9"]
    defs = d[d.name.isin(keys)][["name", "label", "type", "description"]]
    defs["description"] = defs.description.str.strip()
    defs.to_csv(C.AUDIT / "dictionary_outcome_field_definitions.csv", index=False)

    # data vs the dictionary definition of death1 among in-hospital deaths within 30 days
    P = pd.read_pickle(C.RESTRICTED / "cohort_primary.pkl")
    P["period"] = period(P.admission_year)
    ih = P[(P.disp == "death") & (P.los_days <= C.WINDOW_DAYS)]
    tab = pd.crosstab(ih.period, ih.death1.fillna("missing"))
    for c in ["Yes", "No", "missing"]:
        if c not in tab:
            tab[c] = 0
    tab = tab[["Yes", "No", "missing"]]
    tab["n"] = tab.sum(axis=1)
    tab["pct_recorded_as_dictionary_requires"] = (100 * tab.Yes / tab.n).round(1)
    tab.to_csv(C.AUDIT / "death1_vs_dictionary_definition_inhospital.csv")

    # follow-up duration fields: values by period (unit inference)
    raw["year"] = pd.to_datetime(raw["Date of entry"], errors="coerce").dt.year
    raw["period"] = period(raw.year)
    dur = {}
    for f in ["duration followed1", "duration followed3"]:
        v = pd.to_numeric(raw[f], errors="coerce")
        dur[f] = pd.crosstab(raw.period, v).to_dict()
    dur_tab = pd.concat({f: pd.crosstab(raw.period, pd.to_numeric(raw[f], errors="coerce")) for f in ["duration followed1", "duration followed3"]}, axis=1)
    dur_tab.to_csv(C.AUDIT / "followup_duration_values_by_period.csv")

    # onset-to-arrival delay (unit undocumented; heaping at 24/48/72 suggests hours)
    a = pd.to_numeric(raw["HGD arrival time"], errors="coerce")
    heap = float(((a > 0) & (a % 24 == 0)).sum() / a.notna().sum())
    lab = P[P.labelled]
    first = lab.src_ids.str.split("|")
    amap = pd.Series(a.values, index=raw.src_id)
    delay = first.map(lambda ids: amap.reindex(ids).dropna().unique())
    delay = delay.map(lambda u: float(u[0]) if len(u) == 1 else np.nan)
    n2 = lab.y_class == "N2_month1_alive"
    pd.DataFrame({"patient_key": lab.patient_key.values, "arrival_delay_raw": delay.values}).to_pickle(C.RESTRICTED / "arrival_delay_labelled.pkl")
    delay_summary = {
        "n_nonmissing_all_rows": int(a.notna().sum()), "share_at_multiples_of_24": round(heap, 3),
        "quantiles_all_rows": {str(k): float(v) for k, v in a.quantile([.25, .5, .75, .9, .99]).items()},
        "N2_labels": int(n2.sum()), "N2_with_delay_recorded": int((n2 & delay.notna()).sum()),
        "N2_with_delay_gt_threshold": int((n2 & (delay > C.ONSET_GAP_HOURS)).sum()),
        "threshold_hours_assumed": C.ONSET_GAP_HOURS,
    }

    # what the dictionary settles (clarification-request questions)
    q = [  # numbering follows docs/registry_clarification_request.md
        ("Q1 meaning of death1; change around 2014-15", "Partly settled",
         "décès1: 'Death at Month 1, recording if the patient passed away within the first month' (option a of Q1). No explanation of the change in completion around 2014-15."),
        ("Q2 time origin of the month-1 contact", "Partly settled (implicit)",
         "No explicit origin for décès1; month-1 to month-12 assessments are described as '... after the stroke' (e.g. barthel1 'one month after the stroke'). No statement on telephone follow-up after discharge."),
        ("Q3 meaning of death1 = No", "Not settled", "Not stated whether 'No' certifies survival through the month or may be entered when the patient was not reached."),
        ("Q4 disposition 'death'", "Partly settled", "devenir: 'Outcome after leaving the UNV'; consistent with A1. Release date at death not stated."),
        ("Q5 disposition 'Other'", "Not settled", "No code list."),
        ("Q6 units and codes of follow-up durations; codes 9/3/99", "Partly settled",
         "dursuiv1: 'Duration of follow-up at Month 1' without unit; observed values 1 (2010-16) and 30 (2017-19), 3 or 90 at month 3, consistent with months vs days; 0 unexplained; no value codes."),
        ("Q7 post-discharge deaths from 2015", "Not settled", "The single dictionary definition implies in-hospital deaths within month 1 should be recorded as death1 = Yes; the data show they were mostly left blank from 2015."),
        ("Q8 missing dispositions 2020", "Not settled", ""),
        ("Q9 admission Rankin; timing of laboratory values", "Not settled", "rankin: 'Modified Rankin Scale score' without timing; laboratory items without timing."),
        ("Q10 repeated identifiers", "Not settled", "Code_uniq is described as a unique patient identifier, so the 38 repeated codes are entry errors or collisions; source adjudication still needed."),
        ("Q11 date anomalies", "Not settled", ""),
        ("Q12 dates of death for 33 post-discharge deaths", "Not settled", "No date-of-death variable in the dictionary."),
    ]
    qa = pd.DataFrame(q, columns=["question", "status", "evidence"])
    qa.to_csv(C.AUDIT / "clarification_questions_vs_dictionary.csv", index=False)

    out = dict(conformance=conf, death1_vs_definition_inhospital=tab.reset_index().astype(str).to_dict(orient="records"),
               onset_delay=delay_summary)
    json.dump(out, open(C.AUDIT / "dictionary_audit.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False)[:3000])
    print(tab.to_string()); print(dur_tab.to_string()); print(qa.to_string())


if __name__ == "__main__":
    main()
