# Requirements traceability matrix (Phase 2, Gate 0)

Phase 1 ticket IDs are preserved exactly; one requirement may close several tickets. Status values: APPROVED_FOR_IMPLEMENTATION, AUTHOR_DECISION_REQUIRED, REGISTRY_BLOCKED, REWRITE_ONLY, SUBMISSION_ONLY, REJECTED_WITH_RATIONALE, NOT_IMPLEMENTED_WITH_JUSTIFICATION.

| Requirement | Title | Source tickets | Status |
|---|---|---|---|
| REQ-01 | Data ingestion, integrity flags and date/LOS reconciliation | DATA-DATE-001; DATA-DATE-002; DATA-DATE-003; DATA-DICT-001; DATA-DICT-002 | APPROVED_FOR_IMPLEMENTATION |
| REQ-02 | Duplicate reconciliation with per-group evidence and sensitivity rules | DATA-DUP-001; DATA-DUP-002 | AUTHOR_DECISION_REQUIRED |
| REQ-03 | Versioned endpoint with provenance, evidence grades and sensitivity variants | OUTCOME-TIME-001; OUTCOME-TIME-002; OUTCOME-TIME-003; OUTCOME-TIME-004; OUTCOME-REC-001; OUTCOME-REC-002; OUTCOME-REC-003; OUTCOME-REC-005; OUTCOME-REC-006 | AUTHOR_DECISION_REQUIRED |
| REQ-04 | Registry-wide mortality: selection comparison, observation model, IPW, delta-adjustment, bounds | EPI-MORT-001; EPI-MORT-002; EPI-SEL-001; EPI-SEL-002; EPI-SEL-003; EPI-SEL-004 | APPROVED_FOR_IMPLEMENTATION |
| REQ-05 | Survival / interval-censored analysis feasibility | EPI-SURV-001; OUTCOME-REC-004 | NOT_IMPLEMENTED_WITH_JUSTIFICATION |
| REQ-06 | Admission-time predictors, missingness and imputation inside folds | MODEL-IMP-001; MODEL-IMP-002; MODEL-LEAK-001; MODEL-LEAK-002 | APPROVED_FOR_IMPLEMENTATION |
| REQ-07 | Model set, clinical comparator, nested CV, sample size | MODEL-LIST-001; MODEL-COMP-001; STAT-SIZE-001 | APPROVED_FOR_IMPLEMENTATION |
| REQ-08 | Temporal validation at one outcome-independent cut-off; period shift description | VAL-TEMP-001; VAL-TEMP-002; VAL-TEMP-003 | APPROVED_FOR_IMPLEMENTATION |
| REQ-09 | Paired AUROC differences with CIs; calibration protocol with test-set lock | STAT-AUC-001; STAT-AUC-002; STAT-CAL-001 | APPROVED_FOR_IMPLEMENTATION |
| REQ-10 | Pre-specified risk tiers, explanation of the collapsed tier, exploratory decision curves | STAT-RISK-001; STAT-RISK-002 | APPROVED_FOR_IMPLEMENTATION |
| REQ-11 | Interpretation without over-claiming | XAI-001; XAI-002; XAI-003 | APPROVED_FOR_IMPLEMENTATION |
| REQ-12 | Claims, framing and separation of contributions | CLAIM-001; CLAIM-002; CLAIM-003; CLAIM-004 | REWRITE_ONLY |
| REQ-13 | Reproducibility, provenance and privacy | REPRO-001; REPRO-002; REPRO-003; REPRO-004 | APPROVED_FOR_IMPLEMENTATION |
| REQ-14 | Submission package: flat compilable LaTeX source, bibliography, format checks | SUBM-001; SUBM-002; SUBM-003; SUBM-004; ADMIN-001 | SUBMISSION_ONLY |
| REQ-15 | Declarations confirmed by humans | DECL-001; DECL-002; DECL-003; DECL-004; DECL-005 | AUTHOR_DECISION_REQUIRED |

## Ticket → requirement

| Ticket | Priority | Requirement |
|---|---|---|
| ADMIN-001 | P3_LOW | REQ-14 |
| CLAIM-001 | P1_HIGH | REQ-12 |
| CLAIM-002 | P1_HIGH | REQ-12 |
| CLAIM-003 | P1_HIGH | REQ-12 |
| CLAIM-004 | P1_HIGH | REQ-12 |
| DATA-DATE-001 | P0_CRITICAL | REQ-01 |
| DATA-DATE-002 | P0_CRITICAL | REQ-01 |
| DATA-DATE-003 | P1_HIGH | REQ-01 |
| DATA-DICT-001 | P1_HIGH | REQ-01 |
| DATA-DICT-002 | P1_HIGH | REQ-01 |
| DATA-DUP-001 | P0_CRITICAL | REQ-02 |
| DATA-DUP-002 | P0_CRITICAL | REQ-02 |
| DECL-001 | P0_CRITICAL | REQ-15 |
| DECL-002 | P1_HIGH | REQ-15 |
| DECL-003 | P0_CRITICAL | REQ-15 |
| DECL-004 | P1_HIGH | REQ-15 |
| DECL-005 | P1_HIGH | REQ-15 |
| EPI-MORT-001 | P0_CRITICAL | REQ-04 |
| EPI-MORT-002 | P1_HIGH | REQ-04 |
| EPI-SEL-001 | P1_HIGH | REQ-04 |
| EPI-SEL-002 | P1_HIGH | REQ-04 |
| EPI-SEL-003 | P1_HIGH | REQ-04 |
| EPI-SEL-004 | P1_HIGH | REQ-04 |
| EPI-SURV-001 | P1_HIGH | REQ-05 |
| MODEL-COMP-001 | P1_HIGH | REQ-07 |
| MODEL-IMP-001 | P1_HIGH | REQ-06 |
| MODEL-IMP-002 | P1_HIGH | REQ-06 |
| MODEL-LEAK-001 | P0_CRITICAL | REQ-06 |
| MODEL-LEAK-002 | P0_CRITICAL | REQ-06 |
| MODEL-LIST-001 | P1_HIGH | REQ-07 |
| OUTCOME-REC-001 | P1_HIGH | REQ-03 |
| OUTCOME-REC-002 | P1_HIGH | REQ-03 |
| OUTCOME-REC-003 | P1_HIGH | REQ-03 |
| OUTCOME-REC-004 | P1_HIGH | REQ-05 |
| OUTCOME-REC-005 | P1_HIGH | REQ-03 |
| OUTCOME-REC-006 | P1_HIGH | REQ-03 |
| OUTCOME-TIME-001 | P0_CRITICAL | REQ-03 |
| OUTCOME-TIME-002 | P0_CRITICAL | REQ-03 |
| OUTCOME-TIME-003 | P0_CRITICAL | REQ-03 |
| OUTCOME-TIME-004 | P0_CRITICAL | REQ-03 |
| REPRO-001 | P0_CRITICAL | REQ-13 |
| REPRO-002 | P1_HIGH | REQ-13 |
| REPRO-003 | P0_CRITICAL | REQ-13 |
| REPRO-004 | P3_LOW | REQ-13 |
| STAT-AUC-001 | P1_HIGH | REQ-09 |
| STAT-AUC-002 | P1_HIGH | REQ-09 |
| STAT-CAL-001 | P0_CRITICAL | REQ-09 |
| STAT-RISK-001 | P1_HIGH | REQ-10 |
| STAT-RISK-002 | P1_HIGH | REQ-10 |
| STAT-SIZE-001 | P2_MEDIUM | REQ-07 |
| SUBM-001 | P0_CRITICAL | REQ-14 |
| SUBM-002 | P1_HIGH | REQ-14 |
| SUBM-003 | P1_HIGH | REQ-14 |
| SUBM-004 | P1_HIGH | REQ-14 |
| VAL-TEMP-001 | P0_CRITICAL | REQ-08 |
| VAL-TEMP-002 | P0_CRITICAL | REQ-08 |
| VAL-TEMP-003 | P1_HIGH | REQ-08 |
| XAI-001 | P2_MEDIUM | REQ-11 |
| XAI-002 | P2_MEDIUM | REQ-11 |
| XAI-003 | P2_MEDIUM | REQ-11 |

## Full specifications

### REQ-01 — Data ingestion, integrity flags and date/LOS reconciliation

- **source_tickets**: DATA-DATE-001; DATA-DATE-002; DATA-DATE-003; DATA-DICT-001; DATA-DICT-002
- **status**: APPROVED_FOR_IMPLEMENTATION
- **scientific_objective_and_estimand**: Describe the registry rows as recorded; flag (never alter) invalid dates and LOS; reconcile parsers; audit the dictionary.
- **question**: Which rows have usable dates/stays and what the dictionary establishes.
- **inputs**: All 1,653 rows; Date of entry, Release date, Length of hospitalization; dictionary.
- **population**: All rows (no exclusion at this stage).
- **method_and_assumptions**: Rule-based flags (config/registry_schema.json); openpyxl and pandas parsers compared.
- **validation_scheme**: n/a
- **uncertainty**: n/a
- **outputs**: outputs/audit/cleaning_and_integrity_log.csv; date_los_parser_reconciliation.json; dictionary_audit.json; los_by_disposition.csv
- **automated_tests**: tests: raw Excel year guard; dictionary/schema config
- **acceptance_criteria**: Both parsers give identical counts after the year guard; every flag count reproduced; no date altered.
- **manuscript_locations**: Methods 2.1–2.2; Table A (stay); supplementary dictionary audit
- **dependencies_and_human_approvals**: DATA-DATE-002 and DATA-DICT-002 remain registry questions (interim rule disclosed).
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-02 — Duplicate reconciliation with per-group evidence and sensitivity rules

- **source_tickets**: DATA-DUP-001; DATA-DUP-002
- **status**: AUTHOR_DECISION_REQUIRED
- **scientific_objective_and_estimand**: One reconciliation function applied once; conflicting outcomes never forced; cohort under three labelled rules.
- **question**: Are results sensitive to how the 38 repeated-identifier pairs are handled?
- **inputs**: unique_code, sex, age, outcome fields, predictors.
- **population**: All 1,653 rows → 1,618 records.
- **method_and_assumptions**: Rule in config/outcome_definition.json → duplicate_policy; keep-first and exclude-conflicts as scenarios.
- **validation_scheme**: Nested CV 5×2 under each rule.
- **uncertainty**: DeLong CI per rule.
- **outputs**: outputs/cohort/duplicate_decision_log.csv (no identifiers); duplicate_conflict_matrix (stage 1b); cohort_flows.json
- **automated_tests**: tests: reconcile never picks by position; conflicts → unresolved; no keep=first in code
- **acceptance_criteria**: Every source row maps to one patient or a logged exclusion; AUROC under the three rules within 0.01.
- **manuscript_locations**: Methods 2.2; Results 3.1; Appendix A.3–A.4
- **dependencies_and_human_approvals**: Registry approval of the rule (Q8) outstanding → author must accept the interim rule; cohort totals labelled provisional.
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-03 — Versioned endpoint with provenance, evidence grades and sensitivity variants

- **source_tickets**: OUTCOME-TIME-001; OUTCOME-TIME-002; OUTCOME-TIME-003; OUTCOME-TIME-004; OUTCOME-REC-001; OUTCOME-REC-002; OUTCOME-REC-003; OUTCOME-REC-005; OUTCOME-REC-006
- **status**: AUTHOR_DECISION_REQUIRED
- **scientific_objective_and_estimand**: Death within 30 d of admission including in-hospital death, under A1/A2 (dictionary-supported); provenance per label.
- **question**: What does each label rest on, and how do results change under the alternative timing interpretations?
- **inputs**: death1/3/6/9, disposition, stay, dates; onset-to-arrival delay for the stroke-anchored variant.
- **population**: Eligible admissions (age ≥ 18, valid admission date, not TIA).
- **method_and_assumptions**: Evidence hierarchy (config/outcome_definition.json); variants primary / strict / observed-only / stroke-anchored / no-later-contact.
- **validation_scheme**: Nested CV 5×2 per variant; temporal split with common cut-off.
- **uncertainty**: DeLong CIs.
- **outputs**: outputs/cohort/label_provenance_primary.csv; crosswalk_submitted_vs_revised_labels.csv; model_results.json → sensitivity_nested
- **automated_tests**: 18 endpoint unit tests + unknown-status tests
- **acceptance_criteria**: Definition quoted verbatim from the dictionary; no label reaches E1/E0; variants reported; telephone statement removed.
- **manuscript_locations**: Title; Abstract; Methods 2.4; Table 1; Results 3.3, 3.11; Limitations
- **dependencies_and_human_approvals**: approval_state DICTIONARY_SUPPORTED_NOT_CUSTODIAN_VERIFIED: run requires --accept-provisional; authors must accept the stated assumptions (A10 of the author checklist).
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-04 — Registry-wide mortality: selection comparison, observation model, IPW, delta-adjustment, bounds

- **source_tickets**: EPI-MORT-001; EPI-MORT-002; EPI-SEL-001; EPI-SEL-002; EPI-SEL-003; EPI-SEL-004
- **status**: APPROVED_FOR_IMPLEMENTATION
- **scientific_objective_and_estimand**: Registry-wide 30-day mortality under stated assumptions; labelled-subset rate reported as selected.
- **question**: What can be said about mortality in the whole registry?
- **inputs**: Admission variables + indicators, period, disposition, stay > 30 d; labels.
- **population**: Eligible; IPW target = patients with recorded disposition (positivity).
- **method_and_assumptions**: SMDs; logistic observation model; IPW truncated at p99; bootstrap 1,000 re-estimating weights; delta-adjustment δ 0.25–8; deterministic bounds.
- **validation_scheme**: n/a
- **uncertainty**: Bootstrap CIs; bounds are deterministic (labelled as such).
- **outputs**: outputs/analysis/ascertainment_summary.json; labelled_vs_unresolved.csv; mnar_delta_primary.csv; tables reconbounds, selbias, delta
- **automated_tests**: —
- **acceptance_criteria**: IPW assumptions, ESS, truncation and tipping δ reported; no sentence calls 33.8% or 34.4% the registry rate.
- **manuscript_locations**: Abstract; Methods 2.5; Results 3.3–3.4; Discussion; Conclusion
- **dependencies_and_human_approvals**: MAR-type assumptions untestable (stated).
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-05 — Survival / interval-censored analysis feasibility

- **source_tickets**: EPI-SURV-001; OUTCOME-REC-004
- **status**: NOT_IMPLEMENTED_WITH_JUSTIFICATION
- **scientific_objective_and_estimand**: Assess whether time-to-event methods are valid with the supplied fields.
- **question**: Can a survival analysis be run without inventing event times?
- **inputs**: duration followed1/3/6/9; death fields.
- **population**: —
- **method_and_assumptions**: Feasibility checklist (docs/survival_feasibility.md).
- **validation_scheme**: —
- **uncertainty**: —
- **outputs**: docs/survival_feasibility.md
- **automated_tests**: —
- **acceptance_criteria**: Each condition (time origin, unit, event, censoring, observed vs nominal times) assessed; conclusion: not feasible.
- **manuscript_locations**: Methods 2.5 (one sentence); response R1-3
- **dependencies_and_human_approvals**: Re-assess if contact dates are supplied (Q10).
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-06 — Admission-time predictors, missingness and imputation inside folds

- **source_tickets**: MODEL-IMP-001; MODEL-IMP-002; MODEL-LEAK-001; MODEL-LEAK-002
- **status**: APPROVED_FOR_IMPLEMENTATION
- **scientific_objective_and_estimand**: Prediction at admission from 27 candidates; iterative imputation fitted in training folds; sensitivity analyses for missingness.
- **question**: Do conclusions depend on the imputation strategy?
- **inputs**: 27 candidates (config/feature_eligibility.json).
- **population**: Labelled patients.
- **method_and_assumptions**: IterativeImputer (BayesianRidge, ≤ 15 iterations) in pipeline; MI m = 5 posterior draws; indicators; low-missing subset; complete-NIHSS.
- **validation_scheme**: Nested CV.
- **uncertainty**: DeLong CIs; between-draw SD.
- **outputs**: outputs/tables/missing*.csv; model_results.json → sensitivity_nested
- **automated_tests**: tests: no post-baseline fields; preprocessing inside pipeline; fold overlap
- **acceptance_criteria**: Code and text identical in method/variables/iterations/m; linkage limitation stated.
- **manuscript_locations**: Methods 2.1, 2.6; Results 3.11; Limitations
- **dependencies_and_human_approvals**: Repeat admissions cannot be linked (disclosed).
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-07 — Model set, clinical comparator, nested CV, sample size

- **source_tickets**: MODEL-LIST-001; MODEL-COMP-001; STAT-SIZE-001
- **status**: APPROVED_FOR_IMPLEMENTATION
- **scientific_objective_and_estimand**: Discrimination of the primary model and challengers vs a fully specified local comparator.
- **question**: How well do admission data rank first-month death?
- **inputs**: 27 candidates; comparator 6 predictors.
- **population**: Labelled.
- **method_and_assumptions**: L2 LR (C grid by inner CV), RF, HGB, XGB, ClinRef unpenalised; nested 5×5/3; post hoc Riley check.
- **validation_scheme**: Nested CV; temporal.
- **uncertainty**: DeLong CIs; fold SD.
- **outputs**: outputs/tables/nestedcv.tex; riley_samplesize_posthoc.json
- **automated_tests**: —
- **acceptance_criteria**: Same model list in every table; comparator specification complete; EPV on candidates.
- **manuscript_locations**: Methods 2.7–2.8; Results 3.6
- **dependencies_and_human_approvals**: —
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-08 — Temporal validation at one outcome-independent cut-off; period shift description

- **source_tickets**: VAL-TEMP-001; VAL-TEMP-002; VAL-TEMP-003
- **status**: APPROVED_FOR_IMPLEMENTATION
- **scientific_objective_and_estimand**: Internal temporal evaluation; no generalisation claim.
- **question**: Does performance hold in later admissions, and what else changed?
- **inputs**: Admission date; all predictors; labels per variant.
- **population**: Labelled; cut-off = 70th percentile of all eligible admission dates (2018-11-20).
- **method_and_assumptions**: Same cut-off for primary/strict/observed-only; shift table; membership AUROC.
- **validation_scheme**: Temporal split.
- **uncertainty**: DeLong CIs; paired differences.
- **outputs**: model_results.json → temporal_*; tables temporal, tempshift
- **automated_tests**: —
- **acceptance_criteria**: Identical cut-off in every temporal table; 'resolves the collapse' interpretation withdrawn.
- **manuscript_locations**: Methods 2.8; Results 3.8; Discussion 4.2
- **dependencies_and_human_approvals**: —
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-09 — Paired AUROC differences with CIs; calibration protocol with test-set lock

- **source_tickets**: STAT-AUC-001; STAT-AUC-002; STAT-CAL-001
- **status**: APPROVED_FOR_IMPLEMENTATION
- **scientific_objective_and_estimand**: Compare models without equivalence claims; calibrate without test-set selection.
- **question**: Is the primary model better than the comparator, and are its probabilities calibrated?
- **inputs**: OOF and temporal predictions.
- **population**: Labelled.
- **method_and_assumptions**: Paired DeLong difference + CI; calibration intercept/slope/Brier; Platt/isotonic by inner CV in training folds only.
- **validation_scheme**: Nested CV; temporal.
- **uncertainty**: DeLong; bootstrap for calibration.
- **outputs**: tables paireddelong, calib, recal
- **automated_tests**: tests: paired CI vs paired bootstrap; recalibration code uses training folds only
- **acceptance_criteria**: Every comparison has a CI; no 'equivalent'; partition roles documented.
- **manuscript_locations**: Methods 2.9; Results 3.6, 3.9
- **dependencies_and_human_approvals**: —
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-10 — Pre-specified risk tiers, explanation of the collapsed tier, exploratory decision curves

- **source_tickets**: STAT-RISK-001; STAT-RISK-002
- **status**: APPROVED_FOR_IMPLEMENTATION
- **scientific_objective_and_estimand**: Tiers at fixed absolute-risk cut-points; utility as hypothesis.
- **question**: What would tiers imply, and are they usable?
- **inputs**: OOF and temporal predictions.
- **population**: Labelled.
- **method_and_assumptions**: Cut-points < 10% / ≥ 40%; patients per death; DCA 5–50% unweighted and IPW-weighted.
- **validation_scheme**: —
- **uncertainty**: Wilson CIs.
- **outputs**: tables tiers, dca figure
- **automated_tests**: tests: empty tier reported
- **acceptance_criteria**: Same cut-points everywhere; collapse explained; tiers not recommended.
- **manuscript_locations**: Methods 2.9; Results 3.10; Discussion
- **dependencies_and_human_approvals**: —
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-11 — Interpretation without over-claiming

- **source_tickets**: XAI-001; XAI-002; XAI-003
- **status**: APPROVED_FOR_IMPLEMENTATION
- **scientific_objective_and_estimand**: Describe model behaviour.
- **question**: Which predictors drive the model, and how stable is that description?
- **inputs**: Final LR; XGBoost.
- **population**: Labelled.
- **method_and_assumptions**: ORs per SD with bootstrap CIs; rank frequency; permutation importance; SHAP; Spearman ρ with feature bootstrap; no LIME; ratio only as sensitivity.
- **validation_scheme**: —
- **uncertainty**: Bootstrap.
- **outputs**: tables interp; shap_importance.csv
- **automated_tests**: —
- **acceptance_criteria**: ρ reported as moderate with interval; no mechanism claims.
- **manuscript_locations**: Methods 2.10; Results 3.11; Discussion
- **dependencies_and_human_approvals**: —
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-12 — Claims, framing and separation of contributions

- **source_tickets**: CLAIM-001; CLAIM-002; CLAIM-003; CLAIM-004
- **status**: REWRITE_ONLY
- **scientific_objective_and_estimand**: —
- **question**: —
- **inputs**: —
- **population**: —
- **method_and_assumptions**: Rewrite per review_audit/08.
- **validation_scheme**: —
- **uncertainty**: —
- **outputs**: manuscript/main.tex
- **automated_tests**: verify.py text checks
- **acceptance_criteria**: No 'generalises', 'matches', 'first', 'as much as'; two questions separated; limitations complete.
- **manuscript_locations**: Title; Abstract; Introduction; Discussion; Conclusion
- **dependencies_and_human_approvals**: —
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-13 — Reproducibility, provenance and privacy

- **source_tickets**: REPRO-001; REPRO-002; REPRO-003; REPRO-004
- **status**: APPROVED_FOR_IMPLEMENTATION
- **scientific_objective_and_estimand**: Fresh clean run; aggregate-only outputs; manifest.
- **question**: Can every number be regenerated?
- **inputs**: —
- **population**: —
- **method_and_assumptions**: run.py modes; SHA-256 manifest; verify.py (98 checks); privacy_check.py; allowlisted archive.
- **validation_scheme**: —
- **uncertainty**: —
- **outputs**: outputs/run_manifest.json; execution_log.txt; verification_report.json
- **automated_tests**: full test suite (31)
- **acceptance_criteria**: Clean run OK; verification all pass; archive inspected; no placeholder metadata.
- **manuscript_locations**: Methods 2.12; Appendix B; Data and code availability
- **dependencies_and_human_approvals**: CITATION.cff not shipped (placeholders) until authors decide on a repository.
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-14 — Submission package: flat compilable LaTeX source, bibliography, format checks

- **source_tickets**: SUBM-001; SUBM-002; SUBM-003; SUBM-004; ADMIN-001
- **status**: SUBMISSION_ONLY
- **scientific_objective_and_estimand**: —
- **question**: —
- **inputs**: —
- **population**: —
- **method_and_assumptions**: Flatten tables/figures to root; BibTeX; compile from a clean directory; QA PDF; manifest; upload map.
- **validation_scheme**: —
- **uncertainty**: —
- **outputs**: submission_package/
- **automated_tests**: compile log check
- **acceptance_criteria**: Compiles without errors or undefined references; .bbl present; abstract ≤ 250 words.
- **manuscript_locations**: —
- **dependencies_and_human_approvals**: Graphical abstract / word limit: editorial-office answer pending.
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

### REQ-15 — Declarations confirmed by humans

- **source_tickets**: DECL-001; DECL-002; DECL-003; DECL-004; DECL-005
- **status**: AUTHOR_DECISION_REQUIRED
- **scientific_objective_and_estimand**: —
- **question**: —
- **inputs**: —
- **population**: —
- **method_and_assumptions**: Author confirmation checklist; draft AI declaration prepared for approval.
- **validation_scheme**: —
- **uncertainty**: —
- **outputs**: submission_package/author_confirmation_required.md
- **automated_tests**: —
- **acceptance_criteria**: Written confirmations on file before upload.
- **manuscript_locations**: Declarations
- **dependencies_and_human_approvals**: Cannot be verified from the package.
- **verification_evidence**: see outputs/reports/REVIEWER_TICKET_CLOSURE.md

## Blocker register (P0 gates)

| Gate | Status | Basis |
|---|---|---|
| P0-A duplicate reconciliation | DISCLOSED LIMITATION (author decision) | Rule-based reconciliation with evidence log; two sensitivity rules change AUROC by < 0.01 and the cohort by ≤ 3 patients; registry adjudication pending (Q8) |
| P0-B outcome semantics / time origin | DISCLOSED LIMITATION (author decision) | Dictionary defines death1 (death within the first month; assessments 'after the stroke'); time origin implicit; A1/A2 stated and tested (strict, stroke-anchored); no dates of death |
| P0-C LOS/date reconciliation | RESOLVED (parser) / DISCLOSED (authoritative field) | Parser discrepancy explained to the row; interim stay rule; boundary conflicts unresolved |
| P0-D leakage and independence | VERIFIED | Config + tests; admission-level unit disclosed |
| P0-E test-set lock | VERIFIED | Calibration by inner CV; pre-specified tiers; temporal test evaluated once |