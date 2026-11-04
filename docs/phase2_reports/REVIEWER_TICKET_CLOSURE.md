# Reviewer ticket closure

Status values: VERIFIED (acceptance criteria met with retained evidence), IMPLEMENTED_NOT_VERIFIED (implemented; final verification needs a human decision), BLOCKED_BY_REGISTRY_CLARIFICATION, BLOCKED_BY_AUTHOR_CONFIRMATION, NOT_IMPLEMENTED_WITH_JUSTIFICATION.

| Status | Count |
|---|---|
| VERIFIED | 43 |
| BLOCKED_BY_REGISTRY_CLARIFICATION | 7 |
| IMPLEMENTED_NOT_VERIFIED | 5 |
| BLOCKED_BY_AUTHOR_CONFIRMATION | 4 |
| NOT_IMPLEMENTED_WITH_JUSTIFICATION | 1 |

| Ticket | Title | Priority | Requirement | Status |
|---|---|---|---|---|
| ADMIN-001 | Manuscript title vs repository/README titles mismatch | P3_LOW | REQ-14 | IMPLEMENTED_NOT_VERIFIED |
| CLAIM-001 | Separate the ascertainment finding from the modelling contribution | P1_HIGH | REQ-12 | VERIFIED |
| CLAIM-002 | Narrow the contribution statements | P1_HIGH | REQ-12 | VERIFIED |
| CLAIM-003 | Remove the 'first … model' priority claim | P1_HIGH | REQ-12 | VERIFIED |
| CLAIM-004 | State single-centre retrospective design and absence of external/prospective validation as limitations | P1_HIGH | REQ-12 | VERIFIED |
| DATA-DATE-001 | Reconcile the Pandas vs openpyxl LOS/date diagnostic counts | P0_CRITICAL | REQ-01 | VERIFIED |
| DATA-DATE-002 | Recorded LOS and date-derived interval disagree in 667 of 1,488 pairs; authoritative field unknown | P0_CRITICAL | REQ-01 | BLOCKED_BY_REGISTRY_CLARIFICATION |
| DATA-DATE-003 | Negative intervals and impossible years must be flagged, never corrected | P1_HIGH | REQ-01 | VERIFIED |
| DATA-DICT-001 | Parse the dictionary correctly (cp1252, ';') and record dictionary–workbook mismatches | P1_HIGH | REQ-01 | VERIFIED |
| DATA-DICT-002 | Undocumented codes: death1 '9', death3 '3'/'9', LOS 99, cause-of-death '0'/'9'/'99', disposition 'Other' and '6' | P1_HIGH | REQ-01 | BLOCKED_BY_REGISTRY_CLARIFICATION |
| DATA-DUP-001 | Repeated unique_code groups need an approved reconciliation rule | P0_CRITICAL | REQ-02 | BLOCKED_BY_REGISTRY_CLARIFICATION |
| DATA-DUP-002 | Replace keep="first" deduplication in all four pipeline stages | P0_CRITICAL | REQ-02 | VERIFIED |
| DECL-001 | IRB reference/date in main.tex vs CORRECTIONS.md placeholder | P0_CRITICAL | REQ-15 | BLOCKED_BY_AUTHOR_CONFIRMATION |
| DECL-002 | CRediT roles populated in main.tex vs 'individual CRediT roles' pending in CORRECTIONS.md | P1_HIGH | REQ-15 | BLOCKED_BY_AUTHOR_CONFIRMATION |
| DECL-003 | Generative-AI declaration says no AI was used; revision was prepared with AI assistance | P0_CRITICAL | REQ-15 | BLOCKED_BY_AUTHOR_CONFIRMATION |
| DECL-004 | Data/code availability statement contradictory (openly released vs on request vs future deposit); no repository exists | P1_HIGH | REQ-15 | IMPLEMENTED_NOT_VERIFIED |
| DECL-005 | Funding, competing interests and co-author approval of the final manuscript | P1_HIGH | REQ-15 | BLOCKED_BY_AUTHOR_CONFIRMATION |
| EPI-MORT-001 | 33.8% must not be reported as registry-wide mortality; report denominators and bounds | P0_CRITICAL | REQ-04 | VERIFIED |
| EPI-MORT-002 | Withdraw the 14-point under-ascertainment figure | P1_HIGH | REQ-04 | VERIFIED |
| EPI-SEL-001 | Compare labelled and unresolved patients on admission variables with effect sizes | P1_HIGH | REQ-04 | VERIFIED |
| EPI-SEL-002 | Ascertainability (observation) model using baseline-time variables | P1_HIGH | REQ-04 | VERIFIED |
| EPI-SEL-003 | IPW estimate of registry mortality with weight diagnostics; no claim that IPW solves MNAR | P1_HIGH | REQ-04 | VERIFIED |
| EPI-SEL-004 | MNAR sensitivity: delta-adjustment / tipping point | P1_HIGH | REQ-04 | VERIFIED |
| EPI-SURV-001 | Feasibility of discrete-time / interval-censored survival analysis | P1_HIGH | REQ-05 | NOT_IMPLEMENTED_WITH_JUSTIFICATION |
| MODEL-COMP-001 | Full specification of the clinical-reference comparator | P1_HIGH | REQ-07 | VERIFIED |
| MODEL-IMP-001 | Imputation description must match code: deterministic IterativeImputer (single-split) and median imputation (nested CV) are not MICE | P1_HIGH | REQ-06 | VERIFIED |
| MODEL-IMP-002 | Missingness mechanism discussion and sensitivity for all materially incomplete predictors | P1_HIGH | REQ-06 | VERIFIED |
| MODEL-LEAK-001 | Exclude post-baseline fields from predictors; splits at the patient level | P0_CRITICAL | REQ-06 | VERIFIED |
| MODEL-LEAK-002 | Feature selection, scaling, imputation and tuning inside training folds only | P0_CRITICAL | REQ-06 | VERIFIED |
| MODEL-LIST-001 | XGBoost reported but absent from nested CV | P1_HIGH | REQ-07 | VERIFIED |
| OUTCOME-REC-001 | Justify the day-30 boundary and report the stay distribution of in-hospital deaths | P1_HIGH | REQ-03 | VERIFIED |
| OUTCOME-REC-002 | Rule 'discharged alive after > 30 d ⇒ alive at day 30' — justify with chronology and stay data | P1_HIGH | REQ-03 | VERIFIED |
| OUTCOME-REC-003 | Semantics and completeness of death3/6/9 and their use as survival evidence | P1_HIGH | REQ-03 | IMPLEMENTED_NOT_VERIFIED |
| OUTCOME-REC-004 | Units and meaning of duration followed1/3/6/9 | P1_HIGH | REQ-05 | BLOCKED_BY_REGISTRY_CLARIFICATION |
| OUTCOME-REC-005 | Report the number of labels assigned by each rule with provenance and evidence grade | P1_HIGH | REQ-03 | VERIFIED |
| OUTCOME-REC-006 | Manuscript statement of telephone follow-up at days 7, 14 and 30 after discharge is unsupported | P1_HIGH | REQ-03 | VERIFIED |
| OUTCOME-TIME-001 | Meaning and time origin of death1 (Month 1) | P0_CRITICAL | REQ-03 | IMPLEMENTED_NOT_VERIFIED |
| OUTCOME-TIME-002 | Meaning of death1 = No (confirmed alive vs not reached vs no death recorded) | P0_CRITICAL | REQ-03 | BLOCKED_BY_REGISTRY_CLARIFICATION |
| OUTCOME-TIME-003 | Availability of actual dates of death | P0_CRITICAL | REQ-03 | BLOCKED_BY_REGISTRY_CLARIFICATION |
| OUTCOME-TIME-004 | Meaning of Release date and LOS when disposition is 'death' (assumption A1) | P0_CRITICAL | REQ-03 | BLOCKED_BY_REGISTRY_CLARIFICATION |
| REPRO-001 | Fresh end-to-end rerun in a pinned environment; stale joblib artefacts not evidence | P0_CRITICAL | REQ-13 | VERIFIED |
| REPRO-002 | Complete methodological reporting (TRIPOD+AI; RECORD for the registry component) | P1_HIGH | REQ-13 | VERIFIED |
| REPRO-003 | Row-level data and raw workbook present in stroke_project (data/raw, interim, processed, joblib, outputs.zip) | P0_CRITICAL | REQ-13 | VERIFIED |
| REPRO-004 | CITATION.cff has placeholder authors and DOI | P3_LOW | REQ-13 | VERIFIED |
| STAT-AUC-001 | Paired AUROC difference with 95% CI for every model comparison | P1_HIGH | REQ-09 | VERIFIED |
| STAT-AUC-002 | Remove equivalence/'matches' claims | P1_HIGH | REQ-09 | VERIFIED |
| STAT-CAL-001 | Calibration fitting/selection protocol and test-set lock | P0_CRITICAL | REQ-09 | VERIFIED |
| STAT-RISK-001 | Empty Low tier: explain and replace data-driven tiers with pre-specified cut-points | P1_HIGH | REQ-10 | VERIFIED |
| STAT-RISK-002 | Utility claims: decision curves as exploratory; tiers not recommended; pathway as hypothesis | P1_HIGH | REQ-10 | VERIFIED |
| STAT-SIZE-001 | Sample-size justification (EPV reported on selected features) | P2_MEDIUM | REQ-07 | VERIFIED |
| SUBM-001 | Editable LaTeX source set for Editorial Manager (flat, compilable) | P0_CRITICAL | REQ-14 | VERIFIED |
| SUBM-002 | main.bbl absent although CORRECTIONS.md says it is bundled | P1_HIGH | REQ-14 | VERIFIED |
| SUBM-003 | main_no_title.tex references \input{macros} (root) while the file is tables/macros.tex; identify the authoritative master | P1_HIGH | REQ-14 | VERIFIED |
| SUBM-004 | Journal format: structured abstract ≤ 250 words, ≤ 7 keywords, highlights, declarations, graphical abstract/word-limit check | P1_HIGH | REQ-14 | IMPLEMENTED_NOT_VERIFIED |
| VAL-TEMP-001 | Time-varying ascertainment, label-source composition and the circularity argument | P0_CRITICAL | REQ-08 | VERIFIED |
| VAL-TEMP-002 | Reconstructed and observed-only temporal analyses used different cut-offs (2016-08-24 vs 2015-12-26) | P0_CRITICAL | REQ-08 | VERIFIED |
| VAL-TEMP-003 | Internal temporal validation is not external validation | P1_HIGH | REQ-08 | VERIFIED |
| XAI-001 | Treat the GCS/NIHSS ratio as exploratory; test whether it adds information | P2_MEDIUM | REQ-11 | VERIFIED |
| XAI-002 | Characterise rank concordance as moderate with an interval | P2_MEDIUM | REQ-11 | VERIFIED |
| XAI-003 | LIME cases: illustrative only or removed | P2_MEDIUM | REQ-11 | VERIFIED |

Evidence per requirement: docs/requirements_traceability_matrix.md; verification_report.json; execution_log.txt; the response letter lists ticket and requirement IDs under each reviewer comment.
