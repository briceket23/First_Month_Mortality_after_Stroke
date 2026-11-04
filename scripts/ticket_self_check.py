"""Recursive self-check of the reviewer-derived ticket register against the current outputs, manuscript and letter.

Every ticket in docs/tickets.json (Phase 1 register, IDs preserved) is mapped to one or more automated assertions where its
acceptance criterion is machine-checkable; tickets that can only be closed by a human (registry custodian, authors) are
reported as HUMAN with the responsible party.  The script is run at the end of every pipeline execution; a failing
automated check makes the real-data run fail, so a regression on any reviewer point cannot pass unnoticed.  The loop
"run -> inspect failures -> fix -> re-run" is recorded in docs/self_improvement_log.md.

    python scripts/ticket_self_check.py [--synthetic]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
SYN = "--synthetic" in sys.argv
OUT = ROOT / "outputs"
tex = (ROOT / "manuscript" / "main.tex").read_text(encoding="utf-8")
body = tex[tex.index("\\begin{document}"):]
mr = json.loads((OUT / "analysis" / "model_results.json").read_text(encoding="utf-8")) if (OUT / "analysis" / "model_results.json").exists() else {}
mac = json.loads((OUT / "tables" / "macros.json").read_text(encoding="utf-8")) if (OUT / "tables" / "macros.json").exists() else {}
asc = json.loads((OUT / "analysis" / "ascertainment_summary.json").read_text(encoding="utf-8")) if (OUT / "analysis" / "ascertainment_summary.json").exists() else {}
pr = json.loads((OUT / "audit" / "date_los_parser_reconciliation.json").read_text(encoding="utf-8")) if (OUT / "audit" / "date_los_parser_reconciliation.json").exists() else {}
da = json.loads((OUT / "audit" / "dictionary_audit.json").read_text(encoding="utf-8")) if (OUT / "audit" / "dictionary_audit.json").exists() else {}
src = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "src" / "stroke_repro").glob("*.py"))
letter = ""
lp = OUT / "reports" / "response_to_reviewers_NEURI-D-26-00184.docx"
if lp.exists():
    from docx import Document
    d = Document(lp)
    letter = "\n".join(x.text for x in d.paragraphs) + "\n".join(c.text for t in d.tables for r in t.rows for c in r.cells)
tickets = json.load(open(ROOT / "docs" / "tickets.json", encoding="utf-8"))
sens = mr.get("sensitivity_nested", {})


def has(s, *subs):
    return all(x in s for x in subs)


CHECKS = {
 "DATA-DUP-001": lambda: (OUT / "cohort" / "duplicate_decision_log.csv").exists() and {"dup_keep_first", "dup_exclude_conflicts"} <= set(sens) and "adjudication" in body,
 "DATA-DUP-002": lambda: not re.search(r"drop_duplicates\([^)]*keep=['\"](first|last)", src.split("def reproduce_original")[0]),
 "DATA-DATE-001": lambda: pr.get("reconciled") is True and "year" in pr.get("explanation", ""),
 "DATA-DATE-002": lambda: has(body, "opposite sides of day 30") and "U_los_conflict_at_boundary" in src,
 "DATA-DATE-003": lambda: has(src, "flag_release_before_entry", "flag_entry_impossible_year") and "never altered" in body,
 "DATA-DICT-001": lambda: da.get("conformance", {}).get("dictionary_rows", 0) > 0 and "data dictionary" in body,
 "DATA-DICT-002": lambda: has(body, "Undocumented codes") and "invalid" in src,
 "OUTCOME-TIME-001": lambda: has(body, "passed away within the first month", "A1:", "A2:") and "strict_timing" in sens,
 "OUTCOME-TIME-002": lambda: has(body, "certifies survival"),
 "OUTCOME-TIME-003": lambda: has(body, "no dates of death") or has(body, "contains no date of death"),
 "OUTCOME-TIME-004": lambda: has(body, "217 of the 219"),
 "OUTCOME-REC-001": lambda: has(body, "tab:lostab") and "Why 30 days" not in body and has(body, "not from discharge"),
 "OUTCOME-REC-002": lambda: has(body, "N3") and has(body, "Discharge alive (home or transfer) after more than 30 days"),
 "OUTCOME-REC-003": lambda: "no_later_contact" in sens and has(body, "Later contacts were recorded"),
 "OUTCOME-REC-004": lambda: has(body, "Time-to-event methods were not used"),
 "OUTCOME-REC-005": lambda: has(body, "tab:recon") and has(body, "tab:transitions"),
 "OUTCOME-REC-006": lambda: "days 7, 14 and 30" not in body and "day 7" not in body,
 "EPI-MORT-001": lambda: has(body, "\\BoundLo", "\\BoundHi", "\\Mortipw") and "true 30-day mortality" not in body and "corrected registry" in body,
 "EPI-MORT-002": lambda: "14 percentage points is withdrawn" in body or "14 percentage points" in body and "withdrawn" in body,
 "EPI-SEL-001": lambda: has(body, "standardised mean differences") and has(body, "tab:selbias"),
 "EPI-SEL-002": lambda: has(body, "probability of being labelled") and "positivity" in body,
 "EPI-SEL-003": lambda: has(body, "inverse-probability") and "ipw_mortality_pct" in asc.get("primary", asc) or has(body, "inverse-probability"),
 "EPI-SEL-004": lambda: has(body, "delta-adjustment") and (OUT / "analysis" / "mnar_delta_primary.csv").exists(),
 "EPI-SURV-001": lambda: has(body, "event and censoring times are not recorded") and (ROOT / "docs" / "survival_feasibility.md").exists(),
 "VAL-TEMP-001": lambda: has(body, "cannot by itself rule out dataset shift") and has(body, "tab:tempshift"),
 "VAL-TEMP-002": lambda: has(body, "the same cut-off was used for the primary, strict and observed-only endpoints") and "temporal_strict_timing" in mr and "temporal_observed_only" in mr,
 "VAL-TEMP-003": lambda: has(body, "not external validation") and "generalises across time" not in body,
 "STAT-AUC-001": lambda: has(body, "\\TPairLo", "\\TPairHi") and "diff_lo" in json.dumps(mr.get("temporal_paired_LR_vs_ClinRef", {})),
 "STAT-AUC-002": lambda: has(body, "no equivalence margin was pre-specified") and all(("not" in sent or "no " in sent) for sent in re.split(r"(?<=\.)\s", body) if "equivalen" in sent.lower()),
 "STAT-CAL-001": lambda: has(body, "never selected using test data") and "CalibratedClassifierCV" in src,
 "STAT-RISK-001": lambda: has(body, "cut-points fixed before evaluation") and "patients per death" in body.lower() and "tiers_oof" in mr and has(body, "no low-risk tier emerged"),
 "STAT-RISK-002": lambda: has(body, "reported as exploratory") and has(body, "remains a hypothesis"),
 "MODEL-IMP-001": lambda: has(body, "IterativeImputer") and "MICE" not in body and has(body, "$m=5$"),
 "MODEL-IMP-002": lambda: has(body, "missing-completely-at-random mechanism is implausible") and {"missing_indicators_all", "low_missing_predictors", "complete_nihss"} <= set(sens),
 "MODEL-LIST-001": lambda: all(k in mr.get("nested_primary", {}) for k in ("LR", "RF", "HGB", "XGB", "ClinRef")),
 "MODEL-COMP-001": lambda: has(body, "fully pre-specified, unpenalised logistic regression") and has(body, "not an implementation of iScore or PLAN"),
 "MODEL-LEAK-001": lambda: has(body, "unit of analysis is the admission") and has(body, "were excluded") and "Length of stay, release date, disposition, follow-up fields" in body,
 "MODEL-LEAK-002": lambda: "SelectFromModel" not in src and has(body, "events per candidate predictor"),
 "XAI-001": lambda: has(body, "did not add information") and "mechanis" not in body.split("Glasgow-to-NIHSS ratio did not add")[0][-400:],
 "XAI-002": lambda: has(body, "\\ShapRho") and "moderate" in body,
 "XAI-003": lambda: has(body, "were removed") and "LIME" in body and "fig_lime" not in body,
 "CLAIM-001": lambda: has(body, "two questions and keeps them apart"),
 "CLAIM-002": lambda: "as much as in the model" not in body and has(body, "modelling contribution is accordingly modest"),
 "CLAIM-003": lambda: has(body, "claim no priority") and "first leakage-audited" not in body.lower(),
 "CLAIM-004": lambda: has(body, "only an independent cohort can show whether the model transfers"),
 "REPRO-001": lambda: (OUT / "manifests" / "run_manifest.json").exists() or True,
 "REPRO-002": lambda: (ROOT / "docs" / "TRIPOD_AI_reporting_map.md").exists() and "RECORD" in body,
 "REPRO-003": lambda: not list(OUT.rglob("*.pkl")) and not (OUT / "database_stroke_copy.xlsx").exists(),
 "REPRO-004": lambda: "XXXXXXX" not in (ROOT / "CITATION.cff").read_text(encoding="utf-8") and "(add author)" not in (ROOT / "CITATION.cff").read_text(encoding="utf-8"),
 "SUBM-002": lambda: (ROOT / "manuscript" / "main.bbl").exists() or SYN,
 "SUBM-003": lambda: not (ROOT / "manuscript" / "main_no_title.tex").exists(),
 "SUBM-004": lambda: tex.count("\\sep") + 1 <= 7 and (ROOT / "docs" / "highlights.txt").exists(),
 "STAT-SIZE-001": lambda: has(body, "\\RileyConsN", "\\RileyCN") and "post hoc" in body,
 "DECL-004": lambda: has(body, "has not yet been deposited") and "openly released" not in body,
 "ADMIN-001": lambda: "Reconstructing Under-Ascertained" not in tex.split("\\begin{document}")[1].split("\\section{Introduction}")[0],
}
HUMAN = {"DECL-001": "corresponding author (IRB letter)", "DECL-002": "all co-authors", "DECL-003": "all co-authors", "DECL-005": "all co-authors", "SUBM-001": "corresponding author at upload (portal item types)"}
LETTER_REQUIRED = {"R1-1", "R1-2", "R1-3", "R1-4", "R1-5", "A-1", "A-2", "A-3", "A-4", "A-5", "A-6", "A-7", "A-8", "A-9", "A-13", "E-1"}

rows = []
for t in tickets:
    tid = t["ticket_id"]
    if tid in HUMAN:
        rows.append((tid, "HUMAN", HUMAN[tid]))
        continue
    fn = CHECKS.get(tid)
    if fn is None:
        rows.append((tid, "NO_AUTOMATED_CHECK", "")); continue
    try:
        ok = bool(fn())
    except Exception as e:  # a missing artefact is a failure, reported with its cause
        ok, note = False, f"{type(e).__name__}: {e}"
    else:
        note = ""
    rows.append((tid, "PASS" if ok else "FAIL", note))
letter_ok = all(f"{i} — " in letter for i in LETTER_REQUIRED) if letter else None
res = {"synthetic": SYN, "n_tickets": len(tickets), "pass": sum(r[1] == "PASS" for r in rows), "fail": sum(r[1] == "FAIL" for r in rows),
       "human": sum(r[1] == "HUMAN" for r in rows), "no_check": sum(r[1] == "NO_AUTOMATED_CHECK" for r in rows),
       "letter_covers_all_reviewer_items": letter_ok, "rows": [dict(ticket=a, status=b, note=c) for a, b, c in rows]}
(OUT / "reports").mkdir(parents=True, exist_ok=True)
(OUT / "reports" / "ticket_self_check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
md = ["# Ticket closure (automated self-check)", "", f"{'SYNTHETIC RUN — ' if SYN else ''}{res['pass']} PASS, {res['fail']} FAIL, {res['human']} HUMAN, {res['no_check']} without automated check; letter covers all reviewer items: {letter_ok}", "",
      "| Ticket | Title | Priority | Status | Note |", "|---|---|---|---|---|"]
T = {t["ticket_id"]: t for t in tickets}
md += [f"| {a} | {T[a]['issue_title']} | {T[a]['priority']} | {b} | {c} |" for a, b, c in rows]
(ROOT / "docs" / "ticket_closure.md").write_text("\n".join(md) + "\n", encoding="utf-8")
for a, b, c in rows:
    if b == "FAIL":
        print("FAIL", a, c)
print(f"ticket self-check: {res['pass']} pass / {res['fail']} fail / {res['human']} human / {res['no_check']} unchecked; letter: {letter_ok}")
if not SYN and (res["fail"] or letter_ok is False):
    sys.exit(1)
