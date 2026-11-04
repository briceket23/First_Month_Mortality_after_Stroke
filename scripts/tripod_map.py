"""TRIPOD+AI-aligned reporting map with verified locations from the compiled manuscript (.aux).

Topics follow the TRIPOD+AI statement (Collins et al., BMJ 2024;385:e078378). Item wording here is
abbreviated by topic; the authors must transfer the locations to the official checklist form
(tripod-statement.org) before upload, where the journal requires the form itself.
Usage: python tools/tripod_map.py manuscript/main.aux docs/TRIPOD_AI_reporting_map.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stroke_repro.locations import Loc  # noqa: E402


def main(aux, out):
    L = Loc(aux)
    S, T, F, Ln = L.sec, L.tab, L.fig, L.line
    rows = [
        ("Title", "Identifies the study as developing/evaluating a prediction model; population, outcome", "Title page (revised: names population, outcome and model development)", "Reported"),
        ("Abstract", "Structured summary with objectives, data, outcome, predictors, methods, results, conclusions", "Abstract", "Reported"),
        ("Background", "Healthcare context, rationale, intended use and users of the model", "Introduction (paragraph 1, intended use); Section 2.1 (study design)", "Reported; intended use stated as hypothetical and not evaluated"),
        ("Objectives", "Objectives, including whether development and/or evaluation", f"Introduction, {Ln('L:intro-ascert')}", "Reported"),
        ("Data source", "Source, setting, dates of data collection, registry description", f"{S('sec:dups')} (setting) and {S('sec:dups')}", "Reported"),
        ("Participants / eligibility", "Eligibility criteria, exclusions, flow of participants", f"Eligibility paragraph after {S('sec:dups')}; {F('fig:flow')}", "Reported"),
        ("Data preparation", "Cleaning, unit harmonisation, integrity flags, duplicate handling", f"{S('sec:dups')}; {S('sec:missing')}; {T('tab:auditrecon')}", "Reported"),
        ("Outcome", "Definition, time origin, window, provenance, assumptions, blinding", f"{S('sec:outcome')}; {T('tab:recon')}", "Reported; definition conditional on registry confirmation (stated)"),
        ("Predictors", "Definition, timing (admission), measurement, exclusion of post-admission variables", f"{S('sec:missing')}", "Reported"),
        ("Sample size", "Events, candidate predictors, events per predictor, justification", f"{Ln('L:samplesize')} (post hoc Riley criteria); {T('tab:nestedcv')}", "Reported (no a priori calculation; post hoc check met only under the AUROC-based assumption; stated)"),
        ("Missing data", "Amount, mechanism discussion, imputation method, variables, iterations, fold-wise fitting, sensitivity", f"{S('sec:missing')}; {T('tab:missing')}; {T('tab:sens')}", "Reported"),
        ("Analytical methods: model types", "Primary model, challengers, comparator with full specification", f"{S('sec:comparator')}", "Reported"),
        ("Analytical methods: tuning and selection", "Hyperparameter grids, inner CV, no data-driven feature selection", f"{S('sec:comparator')}; {S('sec:validation')}", "Reported"),
        ("Analytical methods: validation", "Nested CV; temporal split with pre-fixed cut-off; separation of development and evaluation", f"{S('sec:validation')}", "Reported"),
        ("Analytical methods: performance measures", "Discrimination, calibration, clinical utility, paired comparison, uncertainty", f"{S('sec:calib')}", "Reported"),
        ("Class imbalance", "Outcome prevalence and handling (no class weighting; reasons)", f"{S('sec:comparator')}", "Reported"),
        ("Fairness / subgroups", "Subgroup performance (sex, subtype, period, NIHSS recorded)", f"{S('sec:sensitivity')}; {T('tab:subgroups')}", "Reported"),
        ("Model output and intended use", "Probability output; pre-specified risk tiers; no clinical deployment claimed", f"{S('sec:calib')}; {S('sec:res-tiers')}", "Reported"),
        ("Ethical approval", "IRB reference and consent waiver", "Ethics approval statement", "Reported (date to be verified against IRB letter)"),
        ("Protocol / registration", "Analysis protocol and pre-fixed design; no registration", "Supplementary: 00_reanalysis_protocol.md; not registered (stated here)", "Partly: protocol supplied; not registered"),
        ("Data sharing", "Availability and access conditions", "Data and code availability statement", "Reported"),
        ("Code sharing", "Complete code supplied; repository status", f"Data and code availability statement, {Ln('L:availability')}", "Reported (not yet deposited; stated)"),
        ("Public involvement", "Patient and public involvement", "Not undertaken", "Not applicable / not done (state in manuscript if required)"),
        ("Results: participants", "Flow, numbers, characteristics, outcome distribution, unresolved outcomes", f"{F('fig:flow')}; {T('tab:baseline')}; {T('tab:selbias')}", "Reported"),
        ("Results: model development", "Selected hyperparameters, final specification, coefficients", f"{S('sec:res-interp')}; {T('tab:interp')}", "Reported"),
        ("Results: model performance", "Discrimination, calibration, utility with uncertainty; paired comparison; temporal", f"{T('tab:nestedcv')}; {T('tab:paireddelong')}; {T('tab:temporal')}; {F('fig:cal')}", "Reported"),
        ("Results: sensitivity analyses", "Endpoint variants, duplicates, imputation, era, IPW", f"{T('tab:sens')}", "Reported"),
        ("Discussion: interpretation", "Main findings for each question; comparison with literature", f"{Ln('L:disc-main')}; {Ln('L:disc-model')}", "Reported"),
        ("Discussion: limitations", "Specific limitations and what would resolve them", f"{S('sec:limits')}", "Reported"),
        ("Discussion: usability and next steps", "External validation, prospective ascertainment, no clinical use yet", f"{Ln('L:disc-utility')}; Conclusion", "Reported"),
    ]
    rec = [
        ("1.1-1.2", "Type of data, region and time frame in title/abstract", "Title; Abstract (Methods)", "Reported"),
        ("1.3", "Linkage between databases stated", "Not applicable: single registry, no linkage", "Not applicable"),
        ("6.1", "Methods of population selection (codes/algorithms) listed", "Eligibility subsection; " + F('fig:flow'), "Reported"),
        ("6.2", "Validation studies of codes or algorithms", S('sec:outcome') + " (data dictionary definitions; evidence grades); supplementary dictionary audit", "Reported; dictionary gives definitions but no value codes or explicit time origin (stated)"),
        ("6.3", "Linkage methods and quality", "Not applicable; repeat admissions cannot be linked (study design subsection)", "Stated"),
        ("7.1", "Complete list of codes/algorithms for outcome, predictors, covariates", S('sec:outcome') + "; " + S('sec:missing') + "; supplementary code", "Reported"),
        ("12.1", "Extent of investigators' access to the database", "Data and code availability statement", "Partly: access route stated; extent of access to source records [AUTHOR VERIFICATION]"),
        ("12.2", "Data cleaning methods", S('sec:dups') + "; " + T('tab:auditrecon'), "Reported"),
        ("12.3", "Linkage", "Not applicable", "Not applicable"),
        ("13.1", "Selection of persons, with flow diagram", F('fig:flow'), "Reported"),
        ("19.1", "Implications of data not created for the research question (misclassification, missing data, changing recording)", S('sec:limits') + "; " + Ln('L:disc-main'), "Reported"),
        ("22.1", "Access to protocol, raw data and programming code", "Data and code availability statement; supplementary protocol", "Reported"),
    ]
    md = ["# TRIPOD+AI and RECORD reporting map — NEURI-D-26-00184 (revision 1)", "",
          "Locations are read from the compiled revised manuscript. Topic wording is abbreviated; transfer to the official TRIPOD+AI checklist form "
          "(Collins et al. 2024, tripod-statement.org) before upload.", "",
          "| Topic | What is expected | Where reported | Status |", "|---|---|---|---|"]
    md += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
    md += ["", "## RECORD (extension of STROBE) items specific to routinely collected data", "",
           "Item numbers follow Benchimol et al., PLoS Med 2015;12:e1001885. STROBE core items overlap with the TRIPOD+AI topics above and are not repeated.", "",
           "| RECORD item | What is expected | Where reported | Status |", "|---|---|---|---|"]
    md += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rec]
    Path(out).write_text("\n".join(md) + "\n", encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
