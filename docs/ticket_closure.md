# Ticket closure (automated self-check)

55 PASS, 0 FAIL, 5 HUMAN, 0 without automated check; letter covers all reviewer items: True

| Ticket | Title | Priority | Status | Note |
|---|---|---|---|---|
| DATA-DUP-001 | Repeated unique_code groups need an approved reconciliation rule | P0_CRITICAL | PASS |  |
| DATA-DUP-002 | Replace keep="first" deduplication in all four pipeline stages | P0_CRITICAL | PASS |  |
| DATA-DATE-001 | Reconcile the Pandas vs openpyxl LOS/date diagnostic counts | P0_CRITICAL | PASS |  |
| DATA-DATE-002 | Recorded LOS and date-derived interval disagree in 667 of 1,488 pairs; authoritative field unknown | P0_CRITICAL | PASS |  |
| DATA-DATE-003 | Negative intervals and impossible years must be flagged, never corrected | P1_HIGH | PASS |  |
| DATA-DICT-001 | Parse the dictionary correctly (cp1252, ';') and record dictionary–workbook mismatches | P1_HIGH | PASS |  |
| DATA-DICT-002 | Undocumented codes: death1 '9', death3 '3'/'9', LOS 99, cause-of-death '0'/'9'/'99', disposition 'Other' and '6' | P1_HIGH | PASS |  |
| OUTCOME-TIME-001 | Meaning and time origin of death1 (Month 1) | P0_CRITICAL | PASS |  |
| OUTCOME-TIME-002 | Meaning of death1 = No (confirmed alive vs not reached vs no death recorded) | P0_CRITICAL | PASS |  |
| OUTCOME-TIME-003 | Availability of actual dates of death | P0_CRITICAL | PASS |  |
| OUTCOME-TIME-004 | Meaning of Release date and LOS when disposition is 'death' (assumption A1) | P0_CRITICAL | PASS |  |
| OUTCOME-REC-001 | Justify the day-30 boundary and report the stay distribution of in-hospital deaths | P1_HIGH | PASS |  |
| OUTCOME-REC-002 | Rule 'discharged alive after > 30 d ⇒ alive at day 30' — justify with chronology and stay data | P1_HIGH | PASS |  |
| OUTCOME-REC-003 | Semantics and completeness of death3/6/9 and their use as survival evidence | P1_HIGH | PASS |  |
| OUTCOME-REC-004 | Units and meaning of duration followed1/3/6/9 | P1_HIGH | PASS |  |
| OUTCOME-REC-005 | Report the number of labels assigned by each rule with provenance and evidence grade | P1_HIGH | PASS |  |
| OUTCOME-REC-006 | Manuscript statement of telephone follow-up at days 7, 14 and 30 after discharge is unsupported | P1_HIGH | PASS |  |
| EPI-MORT-001 | 33.8% must not be reported as registry-wide mortality; report denominators and bounds | P0_CRITICAL | PASS |  |
| EPI-MORT-002 | Withdraw the 14-point under-ascertainment figure | P1_HIGH | PASS |  |
| EPI-SEL-001 | Compare labelled and unresolved patients on admission variables with effect sizes | P1_HIGH | PASS |  |
| EPI-SEL-002 | Ascertainability (observation) model using baseline-time variables | P1_HIGH | PASS |  |
| EPI-SEL-003 | IPW estimate of registry mortality with weight diagnostics; no claim that IPW solves MNAR | P1_HIGH | PASS |  |
| EPI-SEL-004 | MNAR sensitivity: delta-adjustment / tipping point | P1_HIGH | PASS |  |
| EPI-SURV-001 | Feasibility of discrete-time / interval-censored survival analysis | P1_HIGH | PASS |  |
| VAL-TEMP-001 | Time-varying ascertainment, label-source composition and the circularity argument | P0_CRITICAL | PASS |  |
| VAL-TEMP-002 | Reconstructed and observed-only temporal analyses used different cut-offs (2016-08-24 vs 2015-12-26) | P0_CRITICAL | PASS |  |
| VAL-TEMP-003 | Internal temporal validation is not external validation | P1_HIGH | PASS |  |
| STAT-AUC-001 | Paired AUROC difference with 95% CI for every model comparison | P1_HIGH | PASS |  |
| STAT-AUC-002 | Remove equivalence/'matches' claims | P1_HIGH | PASS |  |
| STAT-CAL-001 | Calibration fitting/selection protocol and test-set lock | P0_CRITICAL | PASS |  |
| STAT-RISK-001 | Empty Low tier: explain and replace data-driven tiers with pre-specified cut-points | P1_HIGH | PASS |  |
| STAT-RISK-002 | Utility claims: decision curves as exploratory; tiers not recommended; pathway as hypothesis | P1_HIGH | PASS |  |
| MODEL-IMP-001 | Imputation description must match code: deterministic IterativeImputer (single-split) and median imputation (nested CV) are not MICE | P1_HIGH | PASS |  |
| MODEL-IMP-002 | Missingness mechanism discussion and sensitivity for all materially incomplete predictors | P1_HIGH | PASS |  |
| MODEL-LIST-001 | XGBoost reported but absent from nested CV | P1_HIGH | PASS |  |
| MODEL-COMP-001 | Full specification of the clinical-reference comparator | P1_HIGH | PASS |  |
| MODEL-LEAK-001 | Exclude post-baseline fields from predictors; splits at the patient level | P0_CRITICAL | PASS |  |
| MODEL-LEAK-002 | Feature selection, scaling, imputation and tuning inside training folds only | P0_CRITICAL | PASS |  |
| XAI-001 | Treat the GCS/NIHSS ratio as exploratory; test whether it adds information | P2_MEDIUM | PASS |  |
| XAI-002 | Characterise rank concordance as moderate with an interval | P2_MEDIUM | PASS |  |
| XAI-003 | LIME cases: illustrative only or removed | P2_MEDIUM | PASS |  |
| CLAIM-001 | Separate the ascertainment finding from the modelling contribution | P1_HIGH | PASS |  |
| CLAIM-002 | Narrow the contribution statements | P1_HIGH | PASS |  |
| CLAIM-003 | Remove the 'first … model' priority claim | P1_HIGH | PASS |  |
| CLAIM-004 | State single-centre retrospective design and absence of external/prospective validation as limitations | P1_HIGH | PASS |  |
| REPRO-001 | Fresh end-to-end rerun in a pinned environment; stale joblib artefacts not evidence | P0_CRITICAL | PASS |  |
| REPRO-002 | Complete methodological reporting (TRIPOD+AI; RECORD for the registry component) | P1_HIGH | PASS |  |
| REPRO-003 | Row-level data and raw workbook present in stroke_project (data/raw, interim, processed, joblib, outputs.zip) | P0_CRITICAL | PASS |  |
| REPRO-004 | CITATION.cff has placeholder authors and DOI | P3_LOW | PASS |  |
| SUBM-001 | Editable LaTeX source set for Editorial Manager (flat, compilable) | P0_CRITICAL | HUMAN | corresponding author at upload (portal item types) |
| SUBM-002 | main.bbl absent although CORRECTIONS.md says it is bundled | P1_HIGH | PASS |  |
| SUBM-003 | main_no_title.tex references \input{macros} (root) while the file is tables/macros.tex; identify the authoritative master | P1_HIGH | PASS |  |
| SUBM-004 | Journal format: structured abstract ≤ 250 words, ≤ 7 keywords, highlights, declarations, graphical abstract/word-limit check | P1_HIGH | PASS |  |
| DECL-001 | IRB reference/date in main.tex vs CORRECTIONS.md placeholder | P0_CRITICAL | HUMAN | corresponding author (IRB letter) |
| DECL-002 | CRediT roles populated in main.tex vs 'individual CRediT roles' pending in CORRECTIONS.md | P1_HIGH | HUMAN | all co-authors |
| DECL-003 | Generative-AI declaration says no AI was used; revision was prepared with AI assistance | P0_CRITICAL | HUMAN | all co-authors |
| DECL-004 | Data/code availability statement contradictory (openly released vs on request vs future deposit); no repository exists | P1_HIGH | PASS |  |
| DECL-005 | Funding, competing interests and co-author approval of the final manuscript | P1_HIGH | HUMAN | all co-authors |
| STAT-SIZE-001 | Sample-size justification (EPV reported on selected features) | P2_MEDIUM | PASS |  |
| ADMIN-001 | Manuscript title vs repository/README titles mismatch | P3_LOW | PASS |  |
