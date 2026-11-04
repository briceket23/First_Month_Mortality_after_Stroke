"""Update the authors' execution tracker with the state of the revision.

Original cells (columns, statuses, formulas) are preserved; the original Action Tracker status is copied to a
new column before the status column is updated, so the tracker keeps an audit trail.  Manuscript locations
are read from the compiled manuscript's .aux file and numbers from outputs/tables/macros.json.
Usage: python tools/build_tracker.py ORIGINAL.xlsx OUT.xlsx
"""
import json
import sys
from copy import copy
from pathlib import Path

import openpyxl
import pandas as pd
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from stroke_repro.locations import Loc  # noqa: E402

TODAY = "2 Nov 2026"


def main(src, dst):
    m = {k: v.replace("{,}", ",").replace("$<$", "<").replace("\\%", "%") for k, v in json.load(open(ROOT / "outputs/tables/macros.json", encoding="utf-8")).items()}
    L = Loc(ROOT / "manuscript" / "main.aux")
    flows = json.load(open(ROOT / "outputs/cohort/cohort_flows.json", encoding="utf-8"))
    cc = flows["primary"]["class_counts"]
    tr = pd.read_csv(ROOT / "outputs/audit/tracker_count_reconciliation.csv").set_index("item").revision_value.astype(str)
    ver = json.load(open(ROOT / "outputs/reports/verification_report.json", encoding="utf-8"))
    npass = sum(c["passed"] for c in ver)

    wb = openpyxl.load_workbook(src)
    hdr_font = Font(name="Carlito", size=10, bold=True, color="FFFFFFFF")
    hdr_fill = PatternFill("solid", fgColor="FF17365D")
    new_fill = PatternFill("solid", fgColor="FF0F6B78")          # revision columns: teal header (dashboard accent)
    body = Font(name="Carlito", size=9, color="FF1F2937")
    wrap = Alignment(wrap_text=True, vertical="top")
    status_fill = {"Addressed": "FFE6F4EA", "Addressed – conditional": "FFFFF4E5", "Partly addressed": "FFFFF4E5",
                   "Open – author action": "FFFDECEA", "Complete": "FFE6F4EA", "In progress": "FFFFF4E5",
                   "Blocked": "FFFDECEA", "Not started": "FFF3F4F6"}

    def header(ws, col, text, width, revision=True):
        c = ws.cell(row=1, column=col, value=text)
        c.font, c.fill = hdr_font, (new_fill if revision else hdr_fill)
        c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = width

    def put(ws, row, col, val, status=False):
        c = ws.cell(row=row, column=col, value=val)
        c.font, c.alignment = body, wrap
        if status and val in status_fill:
            c.fill = PatternFill("solid", fgColor=status_fill[val])
        return c

    # ------------------------------------------------------------------ Reviewer Matrix
    ws = wb["Reviewer Matrix"]
    for col, (t, w) in enumerate([("Revision status (" + TODAY + ")", 18), ("What was done (verified by code)", 60),
                                  ("Revised manuscript location (verified)", 40), ("Response letter", 14), ("Remaining action / owner", 40)], start=7):
        header(ws, col, t, w)
    sec, tab, fig, line = L.sec, L.tab, L.fig, L.line
    RM = {
        "R1-1": ("Addressed",
                 f"Data dictionary (received 2 Nov) defines death1 as death 'within the first month' and follow-up assessments as months 'after the stroke'; audited against the workbook. "
                 f"Endpoint specified (day 0 = admission; in-hospital deaths included) with assumptions A1/A2 (both supported by the dictionary) and evidence grades; no label reaches E1/E0 (no explicit time origin, no dates of death). "
                 f"Stroke-anchored sensitivity: {m['NtwoGap']} death1 = No labels with arrival delay >72 h unresolved, AUROC {m['SensOg']}. "
                 f"Day-40 example addressed explicitly. Recording of death1 shown to change in 2014-15 (in-hospital deaths recorded {m['IHDeathOneEarly']} in 2010-12 vs {m['IHDeathOneLate']} from 2015). "
                 f"{m['NEone']} events timed by hospital record, {m['NEtwo']} depend on A2; strict variant excludes them (AUROC {m['SensSt']}). Title changed to 'first-month mortality'.",
                 f"{sec('sec:outcome')}, {line('L:endpoint')}; {tab('tab:recon')}; {sec('sec:res-ascert')}; {fig('fig:ascert')}",
                 "Residual: no dates of death (Q12, optional); authors confirm the dictionary is the registry's official version"),
        "R1-2": ("Addressed",
                 f"33.8% no longer presented as registry mortality. Revised labelled-subset {m['Mortlab']}% ({m['Ndeaths']}/{m['Nlab']}) reported as upper-biased; {m['Nunres']} unresolved reported; "
                 f"bounds {m['BoundLo']}-{m['BoundHi']}%; in-hospital 30-d {m['Mortinhosp']}%; IPW {m['Mortipw']}%; delta-adjusted {m['DeltaMin']}-{m['DeltaMax']}%.",
                 f"{sec('sec:res-mort')}; {tab('tab:reconbounds')}; {tab('tab:period')}; Abstract; Conclusion", "—"),
        "A-1": ("Addressed",
                f"Common outcome-independent temporal cut-off {m['TCut']} for primary, strict and observed-only endpoints; period-specific provenance/ascertainment (Table A.1, shift table); "
                f"event counts and CIs reported; observed-only test has {m['TObE']} deaths (uninformative); claim that reconstruction disproves dataset shift withdrawn.",
                f"{sec('sec:validation')}; {sec('sec:res-temporal')}; {tab('tab:temporal')}; {tab('tab:tempshift')}; {line('L:disc-temporal')}",
                "—"),
        "A-2": ("Addressed", "Introduction poses ascertainment and prediction as separate questions; Results and Discussion follow the split; contributions narrowed.",
                f"{line('L:intro-ascert')}; {line('L:disc-main')}; {line('L:disc-model')}", "—"),
        "A-3": ("Addressed", "'True'/'corrected' mortality, 'not dataset shift', 'first', equivalence and deployment claims removed; clinical use framed as hypothesis; same-centre temporal split described as internal.",
                f"{line('L:disc-novelty')}; {line('L:disc-utility')}; {sec('sec:limits')}; Abstract", "Authors to confirm narrowed contribution statement"),
        "A-4": ("Addressed",
                f"Each rule documented with justification and grade; stay distribution by disposition reported; date-derived stays >120 d not used ({m['Nstayimpl']} records); boundary conflicts left unresolved; "
                f"label transitions submitted→revised tabulated; sensitivity counts (strict {m['NstrictLab']}/{m['NstrictDeaths']}; two duplicate rules); 'Other' disposition no longer used as survival evidence.",
                f"{sec('sec:dups')}; {sec('sec:outcome')}; {tab('tab:lostab')}; {tab('tab:transitions')}; {tab('tab:sens')}",
                "Fields documented in the data dictionary (definitions; no codes); 'Other' disposition and codes 3/9 undocumented"),
        "A-5": ("Addressed", f"Missingness recalculated on final cohort; MCAR/MAR/MNAR discussed; MICE (IterativeImputer, BayesianRidge, ≤15 iterations, converged in 11) inside every training fold; "
                f"same imputation in all analyses; sensitivity: stochastic MI {m['SensMi']}, NIHSS indicator {m['SensNi']}, complete NIHSS {m['SensCn']}.",
                f"{sec('sec:missing')}; {tab('tab:missing')}; {tab('tab:sens')}", "—"),
        "A-6": ("Addressed", "Local clinical-reference model fully specified (age, NIHSS, GCS, admission mRS, haemorrhagic subtype, sex; unpenalised logistic; same fold-wise imputation; no tuning); stated not to be iScore/PLAN.",
                f"{sec('sec:comparator')}", "—"),
        "A-7": ("Addressed", f"Empty low tier explained (thresholds tuned on small validation split); pre-specified cut-points <10% / ≥40%; OOF low tier {m['TierOLowPct']}% of patients ({m['TierOLowMort']}% mortality); "
                "OOF and temporal reported separately; DCA exploratory (unweighted and IPW).",
                f"{line('L:tiers-methods')}; {sec('sec:res-tiers')}; {tab('tab:tiers')}; {fig('fig:dca')}", "—"),
        "A-8": ("Addressed", f"SHAP rank concordance LR vs XGBoost ρ = {m['ShapRho']} ({m['ShapRhoLo']}-{m['ShapRhoHi']}) described as moderate; bootstrap ORs and top-5 frequency; permutation importance on temporal test; "
                f"LIME removed; Glasgow-to-NIHSS ratio exploratory and adds nothing ({m['SensRa']} vs {m['NestLR']}).",
                f"{sec('sec:interp-methods')}; {sec('sec:res-interp')}; {tab('tab:interp')}; {fig('fig:shap')}", "—"),
        "R1-3": ("Addressed", f"Labelled vs unresolved compared (SMDs, period, disposition); observation model with positivity diagnostics (IPW population {m['Nipwpop']}, {m['Nnodisp']} without disposition excluded), "
                 f"truncation at p99 ({m['IPWntrunc']} weights), ESS {m['IPWess']}; delta-adjustment δ 0.25-8; survival analysis not done (no event/censoring dates).",
                 f"{sec('sec:selbias')}; {sec('sec:res-selbias')}; {tab('tab:selbias')}; {tab('tab:delta')}; {fig('fig:delta')}", "—"),
        "R1-4": ("Addressed", f"Equivalence wording removed. Submitted ΔAUC −0.026 cannot get a paired CI (original predictions unavailable). New paired differences: nested CV {m['PairNestDiff']} "
                 f"({m['PairNestLo']} to {m['PairNestHi']}); temporal {m['TPairDiff']} ({m['TPairLo']} to {m['TPairHi']}), p = {m['TPairP']}.",
                 f"{sec('sec:res-paired')}; {tab('tab:paireddelong')}", "—"),
        "R1-5": ("Addressed", f"Submitted calibration downgraded (method compared on test set). New: primary model not recalibrated; Platt/isotonic fitted in-fold as sensitivity; OOF slope {m['NestLRSlope']}, "
                 f"intercept {m['NestLRInt']}; temporal intercept {m['TLRInt']} (IPW {m['TLRipwInt']}).",
                 f"{sec('sec:calib')}; {sec('sec:res-calib')}; {tab('tab:recal')}; {fig('fig:cal')}", "—"),
        "A-9": ("Addressed", "Same-centre temporal evaluation described as internal; external/prospective validation listed as required before clinical use.",
                f"{line('L:validation')}; {sec('sec:limits')}; Conclusion", "—"),
        "A-10": ("Open – author action", "Statement now gives the actual status: code supplied as supplementary material; not yet in a public repository; no future deposit presented as complete.",
                 f"Data and code availability, {line('L:availability')}", "Corresponding author: confirm, or create repository and add identifier"),
        "A-11": ("Partly addressed", f"All preliminary counts re-derived under stated rules: 37/38 any difference; 35/38 timing/outcome; release<entry 23 (22 within registry years); LOS vs dates >1 d 174; union 175; "
                 "implausible dates rows 767/773/808. 194-row total and 28 clinical-difference groups not reproducible without audit build script (28 = timing/outcome both-present).",
                 f"{tab('tab:auditrecon')}; {tab('tab:dupfields')}; {sec('sec:dups')}", "Locate original audit build script and selected-variable list"),
        "A-12": ("Open – author action", "Revised paper defines day 0 as admission and explains why a post-discharge reading of death1 cannot be excluded; strict endpoint isolates hospital-timed events. "
                 "Earlier draft not available to check overlap.",
                 f"{sec('sec:outcome')}; {sec('sec:res-ascert')}", "Authors: reconcile earlier draft (dataset, inclusion, outputs); disclose prior dissemination in cover letter"),
    }
    RM["A-13"] = ("Addressed", "Full methodological reporting: data preparation, endpoint rule with grades, duplicate rules, imputation model (conditional model, iterations, auxiliary variables, "
                  "number of imputations), grids, comparator, validation design, calibration and tier rules, software, seeds; code, execution log, unit tests, verification report, protocol and TRIPOD+AI map supplied.",
                  f"{sec('sec:repro')}; {sec('sec:missing')}; {sec('sec:validation')}; supplementary protocol and TRIPOD+AI map", "Public repository (A-10)")
    RM["E-1"] = ("Addressed", "Complete LaTeX source project (elsarticle) with tables, figures and bibliography; compiles cleanly; clean and change-marked PDFs; no coloured links; line numbers.",
                 "Package folder 01_manuscript/source", "Check Guide for Authors for highlights / graphical abstract")
    from openpyxl.utils import get_column_letter as _gcl
    # new rows for items missing from the original matrix
    last = max(r for r in range(1, ws.max_row + 1) if ws.cell(r, 1).value not in (None, ""))
    existing = [ws.cell(r, 1).value for r in range(2, last + 1)]
    newrows = [("A-13", "Incomplete methodological reporting for reproducibility (reviewer's serious concern 4)", "Major", "Not started",
                "Report every analytic decision; supply code, protocol and reporting checklist.", "Added 19 Oct from the verbatim decision letter."),
               ("E-1", "Editor: upload source files (no PDF for production); follow journal formatting guidelines", "Required", "Not started",
                "Submit compilable LaTeX project in journal format.", "Added 19 Oct from the decision letter.")]
    for rid, concern, pr, st, act, note in newrows:
        if rid not in existing:
            last += 1
            for col, val in enumerate([rid, concern, pr, st, act, note], start=1):
                put(ws, last, col, val)
    header(ws, 12, "Source", 18)
    internal = {"A-10": "Internal (authors' audit)", "A-11": "Internal (authors' audit)", "A-12": "Internal (version check)"}
    for r in range(2, ws.max_row + 1):
        rid = ws.cell(r, 1).value
        if rid in RM:
            st, done, loc, todo = RM[rid]
            put(ws, r, 7, st, status=True); put(ws, r, 8, done); put(ws, r, 9, loc); put(ws, r, 10, f"Item {rid}"); put(ws, r, 11, todo)
            put(ws, r, 12, internal.get(rid, "Reviewer #1 (verbatim)" if not rid.startswith("E") else "Editor (verbatim)"))
    dv = DataValidation(type="list", formula1='"Addressed,Addressed – conditional,Partly addressed,Open – author action"', allow_blank=True)
    ws.add_data_validation(dv); dv.add("G2:G200")

    # ------------------------------------------------------------------ Action Tracker
    ws = wb["Action Tracker"]
    header(ws, 9, "Status 16 Oct (original)", 16); header(ws, 10, "Revision evidence (" + TODAY + ")", 60); header(ws, 11, "Remaining / owner", 40)
    AT = {
        "T0": ("Complete", "Inventory with dates, purposes, version status and missing artifacts; raw workbook MD5 08541ef1…; file manifest in docs/01_inventory_and_decision_gate.md.", "—"),
        "T1": ("In progress", "38 groups, date checks, outcome codes and missingness reconciled with stated rules (Table A.4); all tracker counts reproduced except 194 total and 28 clinical groups.", "Audit build script / variable list (authors)"),
        "T2": ("Complete", "Explicit re-scope decision (Scenario B): registry-recorded first-month outcome; E1/E0/R/I/U/X grades applied; no label reaches E1/E0; strict and observed-only variants.", "Dictionary received 2 Nov and applied; author approval of re-scope"),
        "T3": ("Complete", "Every group categorised (D0 1, D1 4, D2 26, D3 7) by pre-stated rules not based on outcome or completeness; conflicts preserved as unresolved; scenario counts for keep-first and exclude-conflicts.", "Source adjudication (Q10) optional upgrade"),
        "T4": ("In progress", f"Reproducible flow ({m['Nreg']} → {m['Nrecon']} → {m['Nelig']}; {m['Nlab']} labelled, {m['Nunres']} unresolved) and provenance table; label transitions vs submitted.", "Lock after T2"),
        "T5": ("Complete", f"Labelled vs unresolved comparison; observation model with positivity diagnostics; IPW {m['Mortipw']}%; delta-adjusted {m['DeltaMin']}-{m['DeltaMax']}%; estimand and assumptions stated.", "Re-run if T2 changes labels"),
        "T6": ("Complete", f"Common cut-off {m['TCut']} for all endpoint definitions; provenance and shift summaries; event counts and CIs; no causal wording.", "Re-run if T2 changes labels"),
        "T7": ("Complete", "New verified pipeline: fold-level MICE, scaling, tuning; predictor timing audited (post-admission variables excluded); comparator specified. Original scripts unavailable → original claims downgraded.", "—"),
        "T8": ("Complete", f"Calibrators fitted in-fold only; no test-set selection; paired ΔAUC with CI from new predictions (CV {m['PairNestDiff']}, temporal {m['TPairDiff']}).", "—"),
        "T9": ("Complete", "Zero low-tier claim corrected; pre-specified tiers; DCA and explanation-stability wording restricted.", "—"),
        "T10": ("In progress", "Manuscript rewritten (Methods/Results then Abstract/Discussion); compiles with no errors; change-marked PDF produced.", "Author approval"),
        "T11": ("In progress", f"Final-draft response letter (dictionary applied) quotes all reviewer and editor comments verbatim and answers 19 items with verified locations; checklist drafted; {npass}/{len(ver)} verification checks pass.", "Author approvals; extension no longer needed for the endpoint"),
    }
    for r in range(2, ws.max_row + 1):
        tid = ws.cell(r, 1).value
        if tid in AT:
            old = ws.cell(r, 7).value
            put(ws, r, 9, old)
            st, ev, rem = AT[tid]
            c = put(ws, r, 7, st, status=True)
            put(ws, r, 10, ev); put(ws, r, 11, rem)
    dv = DataValidation(type="list", formula1='"Complete,In progress,Blocked,Not started"', allow_blank=True)
    ws.add_data_validation(dv); dv.add("G2:G200")

    # ------------------------------------------------------------------ Evidence Reconciliation
    ws = wb["Evidence Reconciliation"]
    header(ws, 5, "Revision re-check (code, " + TODAY + ")", 46); header(ws, 6, "Match", 12)
    ER = {
        "Raw source rows": (tr["Source rows"], "Yes"), "Raw columns": (tr["Source columns"], "Yes"),
        "Distinct unique_code values": (tr["Distinct unique_code values"], "Yes"), "Repeated-code groups": (tr["Repeated-code groups"], "Yes"),
        "Groups with any field discrepancy": (tr["Groups with any field discrepancy"], "Yes"),
        "Groups with timing/outcome-field differences": (tr["Groups with timing/outcome-field differences"] + " (missing-vs-present counted); " + tr["  same, both rows non-missing"] + " with two different non-missing values", "Yes"),
        "Groups with selected clinical-variable differences": ("Not reproducible without variable list; 28 equals timing/outcome groups with two different non-missing values; any admission-clinical conflict: " + tr["Groups with selected clinical-variable differences"], "Open"),
        "Release before entry": (tr["Release before entry"] + " (years 1900-2030); " + tr["  same, unfiltered"] + " unfiltered; " + tr["  same, registry window"] + " within registry years (analysis rule)", "Yes"),
        "Length-of-stay/date interval differs >1 day": (tr["LOS differs from date interval by >1 day"] + " (>1 d); " + m["LOSdisagree"] + " with >2 d tolerance after excluding derived stays >120 d (analysis rule)", "Yes"),
        "Union of these two timing flags": (tr["Union of the two timing flags"] + "; 194 total not reproducible without build script", "Partly"),
        "Implausible dates": (tr["Implausible dates"], "Yes"),
        "Raw death1 values": (tr["Raw death1 values"], "Yes"), "Raw death3 values": (tr["Raw death3 values"], "Yes"),
        "Raw NIHSS missingness": (tr["Raw NIHSS missingness"], "Yes"), "Raw modified Rankin missingness": (tr["Raw modified Rankin missingness"], "Yes"),
        "Raw SA O2 missingness": (tr["Raw SA O2 missingness"], "Yes"), "Raw BMI missingness": (tr["Raw BMI missingness"], "Yes"),
        "Current manuscript reconstructed cohort": (f"Reproduced exactly: {m['OrigObs']} + {m['OrigInf']} = {m['OrigLab']}; {m['OrigUnl']} unresolved. Revised: {m['Nlab']} labelled, {m['Nunres']} unresolved of {m['Nelig']} eligible", "Yes (superseded)"),
        "Current reported mortality": (f"345/1,021 reproduced; revised labelled-subset {m['Ndeaths']}/{m['Nlab']} = {m['Mortlab']}% (upper-biased); registry-wide not identified", "Superseded"),
        "Temporal comparison": (f"Not reproduced (code unavailable). Revised common cut-off {m['TCut']}: primary {m['TLR']} (n={m['TNte']}, {m['TEte']} deaths); observed-only {m['TObLR']} (n={m['TObN']}, {m['TObE']} deaths)", "Superseded"),
        "Model comparison": (f"Original paired predictions unavailable. Revised paired ΔAUC CV {m['PairNestDiff']} ({m['PairNestLo']} to {m['PairNestHi']}); temporal {m['TPairDiff']} ({m['TPairLo']} to {m['TPairHi']})", "Superseded"),
        "Calibration": (f"Original fitting data could not be audited; revised OOF slope {m['NestLRSlope']}, intercept {m['NestLRInt']}; no recalibration adopted", "Superseded"),
        "Audit package artifacts": ("Still absent; revision outputs regenerate equivalent registers from code (duplicate log, integrity log, restricted annex)", "Open"),
    }
    for r in range(2, ws.max_row + 1):
        it = ws.cell(r, 1).value
        if it in ER:
            v, mt = ER[it]
            put(ws, r, 5, v); c = put(ws, r, 6, mt)
            c.fill = PatternFill("solid", fgColor={"Yes": "FFE6F4EA", "Open": "FFFDECEA", "Partly": "FFFFF4E5"}.get(mt.split(" ")[0], "FFF3F4F6"))

    # ------------------------------------------------------------------ Endpoint Rules
    ws = wb["Endpoint Rules"]
    header(ws, 6, "Revision classes mapped to this grade", 46); header(ws, 7, "Count (eligible n=" + m["Nelig"] + ")", 16)
    g = lambda *ks: sum(cc.get(k, 0) for k in ks)
    nx = 0
    ER2 = {"E1": ("None: no event is confirmed by documented dates; the data dictionary (2 Nov) defines the fields but not their time origin or codes.", 0),
           "E0": ("None: no survival status is confirmed against a documented reference date.", 0),
           "R": ("E2 post-discharge death1=Yes; N2 death1=No; N4 alive at month 3/6/9", g("E2_month1_death_postdischarge", "N2_month1_alive", "N4_alive_later_contact")),
           "I": ("E1 in-hospital death ≤30 d; N1 in-hospital death >30 d; N3 discharged alive >30 d (disposition + stay; A1)", g("E1_inhosp_death_le30", "N1_inhosp_death_gt30", "N3_discharged_alive_gt30")),
           "U": ("All U_* classes (no follow-up, missing/'Other' disposition, conflicts, misaligned, boundary, timing unknown)", flows["primary"]["unresolved"]),
           "X": ("Undocumented codes (death1 '9', death3 '3'/'9') treated as unknown; records end in U unless other evidence exists", "see U")}
    for r in range(2, ws.max_row + 1):
        k = ws.cell(r, 1).value
        if k in ER2:
            put(ws, r, 6, ER2[k][0]); put(ws, r, 7, ER2[k][1])
    r0 = ws.max_row + 2
    put(ws, r0, 1, "Note"); ws.cell(r0, 1).font = Font(name="Carlito", size=9, bold=True)
    put(ws, r0, 2, "Under these thresholds a strict primary endpoint (E1/E0 only) cannot be estimated until the registry documents the fields. The revised paper therefore "
                   "analyses R + I labels as a registry-recorded first-month outcome under stated assumptions (A1, A2) and reports the hospital-timed (strict) and R-only (observed-only) variants.")
    ws.merge_cells(start_row=r0, start_column=2, end_row=r0, end_column=7)
    ws.row_dimensions[r0].height = 40

    # ------------------------------------------------------------------ Publication Portfolio
    ws = wb["Publication Portfolio"]
    header(ws, 9, "Revision note (" + TODAY + ")", 50)
    PP = {"1": "Core integrity results (duplicate discordance, date flags, scenarios) are now inside the current paper (Tables A.3-A.4, B.1).",
          "2": "Not used in this revision; completeness by period is reported only where it affects ascertainment.",
          "3": "Integrated into the current paper (Sections 2.5, 3.3-3.4); a separate paper would overlap heavily.",
          "4": "Not touched (no-go stands: delay units unverified).",
          "5": "Integrated as sensitivity analyses (Table 10); stays supplementary."}
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(r, 1).value)
        if k in PP:
            put(ws, r, 9, PP[k])

    # ------------------------------------------------------------------ Dashboard
    ws = wb["Dashboard"]
    gates = {10: ("Complete", "Data dictionary (2 Nov) defines death1 (death within the first month after the stroke); A1/A2 supported and tested; residual: no explicit time origin, no dates of death (stated)"),
             11: ("Complete", "Rule-based log for all 38 groups; conflicts unresolved; two alternative rules; source adjudication optional"),
             12: ("Complete", f"New leakage-free pipeline; {npass}/{len(ver)} verification checks pass; original results not reproducible and superseded"),
             13: ("Not ready", "Package complete; remaining author actions only: approvals (AI declaration, title, ethics date, dictionary as supplementary file) and editorial-office answer on graphical abstract/word limit")}
    for r, (st, basis) in gates.items():
        ws.cell(r, 2).comment = Comment(f"16 Oct status: {ws.cell(r, 2).value}; basis: {ws.cell(r, 3).value}", "revision")
        c = ws.cell(r, 2, value=st); c.font = Font(name="Carlito", size=11)
        c.fill = PatternFill("solid", fgColor={"Blocked": "FFFDECEA", "Complete": "FFE6F4EA", "Not ready": "FFFDECEA"}[st])
        c = ws.cell(r, 3, value=basis); c.font = Font(name="Carlito", size=11); c.alignment = wrap
    ws["D3"] = "Reviewer items"; ws["E3"] = "Count"
    for cc_ in ("D3", "E3"):
        ws[cc_].font = copy(ws["A3"].font); ws[cc_].fill = copy(ws["A3"].fill)
    for i, st in enumerate(["Addressed", "Addressed – conditional", "Partly addressed", "Open – author action"], start=4):
        ws.cell(i, 4, value=st).font = Font(name="Carlito", size=11)
        c = ws.cell(i, 5, value=f"=COUNTIF('Reviewer Matrix'!$G$2:$G$300,D{i})"); c.font = Font(name="Carlito", size=11)
    ws.cell(9, 4, value="of which reviewer/editor items: 16; internal: 3").font = Font(name="Carlito", size=9, italic=True)
    ws.cell(8, 4, value="Total").font = Font(name="Carlito", size=11, bold=True)
    ws.cell(8, 5, value="=SUM(E4:E7)").font = Font(name="Carlito", size=11, bold=True)
    ws.column_dimensions["D"].width = 24
    ws["A21"] = "Days to deadline"; ws["B21"] = "=DATE(2026,11,6)-TODAY()"
    ws["A22"] = "Revised cohort (17 Oct)"; ws["B22"] = f"{m['Nelig']} eligible; {m['Nlab']} labelled ({m['Ndeaths']} deaths); {m['Nunres']} unresolved"
    ws["A23"] = "Registry-wide 30-day mortality"; ws["B23"] = f"Not identified: bounds {m['BoundLo']}-{m['BoundHi']}%; IPW {m['Mortipw']}%"
    ws["A24"] = "Readiness decision"; ws["B24"] = "NOT READY FOR RESUBMISSION (conditional package prepared)"
    for r in range(21, 25):
        for col in (1, 2):
            ws.cell(r, col).font = Font(name="Carlito", size=11, bold=(col == 1 or r == 24))
    ws["B21"].number_format = "0"
    ws["A16"].comment = Comment("Facts in rows 16-20 are the authors' original entries; rows 22-24 are the revision's results.", "revision")

    # ------------------------------------------------------------------ Revision Log (new sheet)
    lg = wb.create_sheet("Revision Log")
    cols = [("Date", 12), ("Workstream", 24), ("Change / result", 70), ("Evidence (file)", 46), ("Tracker items", 16)]
    for j, (t, w) in enumerate(cols, start=1):
        header(lg, j, t, w, revision=False)
    entries = [
        ("16 Oct 2026", "Inventory", "Inventoried both archives; identified missing artifacts; earlier pipeline reproduces only observed-only analysis.", "docs/01_inventory_and_decision_gate.md", "T0"),
        ("16 Oct 2026", "Audit", "Reproduced submitted reconstruction exactly (803/218/594; 345 deaths).", "outputs/audit/reproduction_of_submitted_counts.json", "T1, A-11"),
        ("16 Oct 2026", "Endpoint", "Found time-varying recording of death1 and disposition; endpoint re-scoped with A1/A2 and strict variant; 18 unit tests.", "docs/02_endpoint_specification.md; tests/", "T2, R1-1"),
        ("16 Oct 2026", "Duplicates", "Rule-based reconciliation of 38 groups; conflicts unresolved; two alternative rules.", "outputs/cohort/duplicate_decision_log.csv", "T3, A-11"),
        ("16 Oct 2026", "Ascertainment", "Labelled vs unresolved, IPW, bounds, delta-adjustment.", "outputs/analysis/ascertainment_summary.json", "T5, R1-2, R1-3"),
        ("16 Oct 2026", "Models", "Nested CV, common-cut-off temporal validation, in-fold calibration, paired ΔAUC, pre-specified tiers, SHAP, 10 sensitivity analyses.", "outputs/analysis/model_results.json", "T6-T9"),
        ("16 Oct 2026", "Manuscript/letter", "Manuscript rewritten; conditional response letter; registry clarification request; change log; checklist.", "manuscript/main.tex; outputs/response_to_reviewers_*.docx", "T10, T11"),
        ("17 Oct 2026", "Tracker", "Applied the execution tracker: response letter re-keyed to items R1-1…R1-5, A-1…A-12; four new responses (A-4, A-9, A-10, A-12).", "outputs/response_to_reviewers_*.docx", "All"),
        ("17 Oct 2026", "Audit", "Re-derived the Evidence Reconciliation counts under stated rules: all 15 verifiable counts reproduced; the 194-row total and the 28 clinical-difference groups could not be reproduced without the original audit script.", "outputs/audit/tracker_count_reconciliation.csv", "T1, A-11"),
        ("17 Oct 2026", "Endpoint", "Added evidence grades E1/E0/R/I/U/X to every label (none reaches E1/E0); day-40 example addressed; correction: manuscript no longer says the clarification request 'has been sent'.", "manuscript/main.tex Section 2.4; Table 1", "R1-1, T2"),
        ("17 Oct 2026", "Endpoint", f"Date-derived stays >120 d ({m['Nstayimpl']} records, five 365-376 d) no longer used; labelled {m['Nlab']}, deaths {m['Ndeaths']}; full re-run from clean state.", "stroke_repro/registry.py; outputs/execution_log.txt", "A-4"),
        ("17 Oct 2026", "Manuscript", "Added stay-by-disposition, label-transition and audit-reconciliation tables; code-availability statement states actual status.", "manuscript/tables/lostab.tex, transitions.tex, auditrecon.tex", "A-4, A-10, A-11"),
        ("17 Oct 2026", "Verification", "Verification checks pass after the clean re-run; LaTeX compiles without errors.", "outputs/verification_report.json", "T11"),
        ("19 Oct 2026", "Tracker", "Verbatim decision letter received; every reviewer sentence mapped to a tracker item; A-13 (reproducibility reporting) and E-1 (editor: source files) added; A-10–A-12 marked internal.", "docs/reviewer_comments_verbatim.md", "All"),
        ("19 Oct 2026", "Analysis", "A-4: completeness of later follow-up by period and sensitivity without later-contact labels; A-5: multiple imputation m=5 with between-draw variability, missingness indicators for all predictors >20% missing, low-missing-predictor model; A-7: patients-per-death effort figures.", "outputs/analysis/model_results.json; ascertainment_by_period_primary.csv", "A-4, A-5, A-7"),
        ("19 Oct 2026", "Protocol", "High-level re-analysis protocol written (v1.1) with reviewer-item map; TRIPOD+AI reporting map generated from the compiled manuscript.", "docs/00_reanalysis_protocol.md; docs/TRIPOD_AI_reporting_map.md", "A-13"),
        ("19 Oct 2026", "Manuscript", "Language pass (clear, short sentences; one term per concept; verbs over nouns); Discussion restructured into four subsections; no coloured links; imputation model fully specified; 'why 30 days' stated; later-contact completeness reported.", "manuscript/main.tex", "A-3, A-4, A-5, A-13"),
        ("19 Oct 2026", "Letter", "Response letter rebuilt with verbatim quotations; old table/figure numbers mapped to the revised ones; 19 items.", "outputs/response_to_reviewers_*.docx", "All"),
        ("19 Oct 2026", "Verification", "Clean re-run; all 79 verification checks then defined passed.", "outputs/verification_report.json", "T11"),
        ("2 Nov 2026", "Citations", "Introduction statements checked against PubMed records: case-fatality sentence, Nkoke readmission figures (15.2% readmitted, not a third), off-topic dialysis citation and iScore/PLAN citation corrected; iScore, PLAN, RECORD and STROBE references added.", "manuscript/main.tex; stroke_bib.bib; docs/03_change_log.md items 51-54", "A-3, A-13"),
        ("2 Nov 2026", "Journal", "Current Guide for Authors checked: abstract cut to <=250 words; 7 keywords (limit 7); highlights file; graphical abstract and word limit flagged for author verification (guide versions disagree).", "docs/highlights.txt; docs/04_submission_checklist.md", "E-1"),
        ("2 Nov 2026", "Manuscript", "Title names population, outcome and model development; intended use stated; RECORD/STROBE cited; unit of analysis and non-linkable readmissions stated; post hoc Riley sample-size check added.", "manuscript/main.tex; tools/riley_samplesize.py", "A-2, A-3, A-13"),
        ("2 Nov 2026", "Letter", "Opening to the handling editor; explicit position per item (agree / partially agree); response matrix; statement that one reviewer report was received.", "outputs/response_to_reviewers_*.docx", "All"),
        ("2 Nov 2026", "Assessment", "Prompt-series assessment (portfolio n=1, review-pattern analysis, claims audit, route scoring, follow-on questions, protocol v1.2 work plan, red-team scorecard).", "docs/06_prompt_series_assessment.docx/.pdf", "All"),
        ("2 Nov 2026", "Dictionary", "Registry data dictionary received (256 variables); audited against the workbook (stage 1e): death1 defined as death within the first month; follow-up dated 'after the stroke'; no value codes; no date of death. Gate G1 closed with residual uncertainty stated.", "outputs/audit/dictionary_audit.json; dictionary_outcome_field_definitions.csv", "R1-1, A-4, T2"),
        ("2 Nov 2026", "Analysis", "New sensitivity analyses for a stroke-anchored month-1 window (death1 = No with arrival delay >72 h, or unknown, treated as unresolved).", "outputs/analysis/model_results.json", "R1-1"),
        ("2 Nov 2026", "Verification", f"Clean re-run; {npass}/{len(ver)} verification checks pass.", "outputs/verification_report.json", "T11"),
    ]
    for i, e in enumerate(entries, start=2):
        for j, v in enumerate(e, start=1):
            put(lg, i, j, v)
    lg.freeze_panes = "A2"

    import math
    for wsx in wb.worksheets:
        if wsx.title != "Dashboard":
            wsx.freeze_panes = "A2"
            for r in range(2, wsx.max_row + 1):
                lines = 1
                for c in wsx[r]:
                    if c.value is None or type(c).__name__ == "MergedCell":
                        continue
                    w = wsx.column_dimensions[c.column_letter].width or 10
                    lines = max(lines, math.ceil(len(str(c.value)) / max(1.0, w * 1.15)))
                wsx.row_dimensions[r].height = min(409, 12.5 * lines + 3)
    wb.save(dst)
    print("saved", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
