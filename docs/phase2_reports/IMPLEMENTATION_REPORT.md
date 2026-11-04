# Implementation report — stroke_reproducibility_rebuilt (3 November 2026)

## What was built and run
- New project with explicit run modes (`audit`, `observed`, `reconstructed`, `sensitivity`, `all`) and a fail-safe gate on the versioned outcome definition (`config/outcome_definition.json`, approval_state `DICTIONARY_SUPPORTED_NOT_CUSTODIAN_VERIFIED`). The reported run used `--mode all --accept-provisional --clean`; `outputs/PROVISIONAL_OUTCOME_DEFINITION.txt` stamps the outputs. Mode label in the manifest: `reconstructed_provisional`; status `OK`.
- Inputs: registry workbook read from `STROKE_DATA_PATH` (SHA-256 `2b599e3d269a4d7a…`, MD5 checked), dictionary (SHA-256 `6c3a0c7bfad9bf49…`). Software: pandas 3.0.5, numpy 2.5.3, scipy 1.18.1, sklearn 1.9.1, xgboost 3.4.1, shap 0.54.1, statsmodels 0.15.0, openpyxl 3.1.5, matplotlib 3.11.2. Seed 20261016.
- Retained verified logic from the revision workspace (`strokerev`), replaced components listed in README; nothing from the June `stroke_project/` was executed and no serialised artefact was loaded.

## Requirements implemented
| Requirement | Status after run |
|---|---|
| REQ-01 Data ingestion, integrity flags and date/LOS reconciliation | APPROVED_FOR_IMPLEMENTATION |
| REQ-02 Duplicate reconciliation with per-group evidence and sensitivity rules | AUTHOR_DECISION_REQUIRED |
| REQ-03 Versioned endpoint with provenance, evidence grades and sensitivity variants | AUTHOR_DECISION_REQUIRED |
| REQ-04 Registry-wide mortality: selection comparison, observation model, IPW, delta-adjustment, bounds | APPROVED_FOR_IMPLEMENTATION |
| REQ-05 Survival / interval-censored analysis feasibility | NOT_IMPLEMENTED_WITH_JUSTIFICATION |
| REQ-06 Admission-time predictors, missingness and imputation inside folds | APPROVED_FOR_IMPLEMENTATION |
| REQ-07 Model set, clinical comparator, nested CV, sample size | APPROVED_FOR_IMPLEMENTATION |
| REQ-08 Temporal validation at one outcome-independent cut-off; period shift description | APPROVED_FOR_IMPLEMENTATION |
| REQ-09 Paired AUROC differences with CIs; calibration protocol with test-set lock | APPROVED_FOR_IMPLEMENTATION |
| REQ-10 Pre-specified risk tiers, explanation of the collapsed tier, exploratory decision curves | APPROVED_FOR_IMPLEMENTATION |
| REQ-11 Interpretation without over-claiming | APPROVED_FOR_IMPLEMENTATION |
| REQ-12 Claims, framing and separation of contributions | REWRITE_ONLY |
| REQ-13 Reproducibility, provenance and privacy | APPROVED_FOR_IMPLEMENTATION |
| REQ-14 Submission package: flat compilable LaTeX source, bibliography, format checks | SUBMISSION_ONLY |
| REQ-15 Declarations confirmed by humans | AUTHOR_DECISION_REQUIRED |

## Key fresh results (aggregate)
- Rows 1,653 → reconciled records 1,618 → eligible 1,579; labelled 982 (338 deaths, 34.4%); unresolved 597.
- Recorded month-1 status only (observed mode): 784 patients, 160 deaths (20.4%).
- Registry-wide 30-day mortality: bounds 21.4–59.2%; IPW 27.5%; delta-adjusted (δ = 1) 29.8–30.7%.
- Nested-CV AUROC: LR 0.863 (0.839–0.886); clinical reference 0.839; XGBoost 0.879; paired LR − reference 0.024 (CV), 0.022 (-0.027 to 0.070) temporal.
- Sensitivity endpoints: strict 0.872; observed-only 0.868; stroke-anchored 0.856 / 0.855; no later contact 0.859.
- Post hoc Riley sample size: required 2,100 (conservative) or 592 (AUROC-based); available 982.
- Parser reconciliation: 1488 date/LOS pairs, 821 equal, 667 differ, 23 negative; reconciled = True.

## Post-run corrections (logged in execution_log.txt)
1. Verifier path fix (tools only); verification, tracker, privacy check and manifest re-executed. 2. A hard-coded observed-only mortality (20.2%, June cohort) in the Conclusion replaced by the generated macro (20.4%); stage 4 onwards re-executed. 3. Tiers table font size reduced (overfull box); stage 4 onwards re-executed. Analysis stages 1–3 were not re-run; their outputs are unchanged and identical to the 2 November clean run.

## Not implemented, with justification
- Survival / interval-censored analysis (REQ-05): no event or censoring dates; see docs/survival_feasibility.md.
- LIME case explanations: no stability/fidelity validation feasible before the deadline; removed (XAI-003).
- Ascertainment-weighted DCA is reported but labelled exploratory (STAT-RISK-002).
