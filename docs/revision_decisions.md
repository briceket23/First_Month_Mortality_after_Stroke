# Revision change log — NEURI-D-26-00184

Status key: **Reproduced** = same value from independent code; **Corrected** = changed because the original was wrong or not defensible; **New** = analysis not previously reported; **Withdrawn** = claim removed; **Unresolved** = cannot be settled from the available evidence. Reviewer items use the IDs of the authors' execution tracker (R1-1…R1-5, A-1…A-12), as in the response letter. Locations refer to the revised `main.pdf` (sections; the response letter gives page and line).

| # | Change | Status | Reviewer comment | Manuscript location |
|---|---|---|---|---|
| 1 | Title changed from "Reconstructing Under-Ascertained 30-Day Stroke Mortality…" to "Ascertainment of First-Month Mortality and Interpretable Risk Prediction after Stroke…" | Corrected | R1-1, R1-2 | Title |
| 2 | Abstract rewritten: endpoint with stated assumption, ascertainment findings, non-identified mortality, nested-CV and temporal results with paired difference; equivalence and 14-point claims removed | Corrected | R1-1, R1-2, R1-4, A-3 | Abstract |
| 3 | Introduction separates the ascertainment question from the prediction question; novelty claims qualified (no systematic search) | Corrected | A-2, A-3 | Introduction, final paragraph |
| 4 | Explicit endpoint specification (index date, window, A1/A2, evidence hierarchy, unresolved rules, strict and observed-only variants); unit-tested | New | R1-1 | §2.4, Table 1 |
| 5 | Time-varying recording of `death1`, disposition and follow-up coding documented | New | R1-1, A-1 | §3.2, Fig. 2, Table A.1 |
| 6 | Duplicate identifiers: rule-based, logged reconciliation across all fields; outcome conflicts unresolved; two alternative rules | Corrected (was keep-first) | A-11 | §2.2, §3.1, Tables A.3–A.4 |
| 7 | Record-integrity flags (misaligned rows, impossible dates, stay disagreements); raw values never altered | New | A-11 | §2.2, §3.1 |
| 8 | Transient ischaemic attacks (n = 24) excluded | Corrected | — | §2.3 |
| 9 | Submitted reconstruction counts 803 / 218 / 594 and 345 deaths re-derived | Reproduced | A-11 | §2.12, Table B.1 |
| 10 | Labelled cohort 982 (338 deaths, 34.4%); 597 unresolved | Corrected | R1-1, R1-2 | §3.3, Table 1 |
| 11 | "33.8% = true registry mortality" and "~14 percentage-point under-ascertainment" | Withdrawn | R1-2 | §3.3, §4 |
| 12 | Registry-wide mortality: bounds, in-hospital 30-day mortality, IPW estimate, delta-adjustment | New | R1-2, R1-3 | §2.5, §3.3, Table 2, Fig. 3, Table A.2 |
| 13 | Labelled vs unresolved comparison with SMDs, period and disposition | Corrected (was included vs excluded, partial) | R1-3 | §3.4, Table 3 |
| 14 | Window sweep (21–35 days) removed — not informative for labels mostly from `death1` | Withdrawn | A-1 | — |
| 15 | Predictors limited to admission-time variables; SpO₂ excluded (> 60% missing); engineered features removed; LASSO selection removed | Corrected | A-5, A-8 | §2.6 |
| 16 | Missingness recalculated; MCAR/MAR/MNAR discussion; MICE inside every training fold (same imputation in all analyses) | Corrected | A-5 | §2.6, Table A.7 |
| 17 | Clinical-reference model fully specified; explicitly not iScore/PLAN | Corrected | A-6 | §2.7 |
| 18 | Validation: nested CV (5×5, inner 3-fold) replaces the 70/15/15 split | Corrected | R1-4, R1-5, A-7 | §2.8, Table 5, Fig. 4 |
| 19 | Paired AUROC difference with 95% CI (nested CV and temporal); equivalence wording removed | New / Withdrawn | R1-4 | §3.7, Table 6 |
| 20 | Temporal validation: single outcome-independent cut-off (2018-11-20) for all endpoints; shift table; membership AUROC; "not external validation" | Corrected | A-3 | §2.8, §3.8, Table 7, Table A.8 |
| 21 | "Observed-only temporal collapse proves ascertainment artefact, not dataset shift" | Withdrawn | A-1, A-3 | §3.8, §4 |
| 22 | Calibration: primary model unweighted and not recalibrated; Platt/isotonic fitted in-fold as sensitivity; IPW-weighted calibration | Corrected | R1-5 | §2.9, §3.9, Table A.9, Fig. 5 |
| 23 | Risk tiers at pre-specified absolute-risk cut-points; OOF and temporal reported separately; DCA exploratory, also weighted | Corrected | A-7 | §2.9, §3.10, Table 8, Figs. 6–7 |
| 24 | Interpretation: bootstrap ORs, top-5 frequency, permutation importance on temporal test, SHAP for LR and XGBoost, ρ = 0.58 described as moderate | Corrected | A-8 | §2.10, §3.11, Table 9, Fig. 8 |
| 25 | LIME four-case figure removed | Withdrawn | A-8 | — |
| 26 | Glasgow-to-NIHSS ratio: tested as added feature (no gain); causal/mechanistic reading removed | Corrected | A-8 | §3.11, §4 |
| 27 | Sensitivity analyses (10) and subgroup analyses from OOF predictions | New | A-1, R1-3, A-5 | §3.12, Table 10, Table A.10 |
| 28 | Learning curve, PDPs, confusion matrix, EDA overview, lab-distribution and correlation figures removed | Withdrawn | — | — |
| 29 | Software/reproducibility statement: new tested pipeline; original results not reproduced | Corrected | A-11 | §2.12, Appendix B |
| 30 | Data and code availability: code supplied with the submission | Corrected | A-11 | Back matter |
| 31 | Generative-AI declaration updated to disclose AI-assisted analysis and drafting (authors must confirm) | Corrected | — | Back matter |
| 32 | Bibliography: 19 DOIs were being dropped by a syntax error (fixed); 8 PubMed/IEEE/NeurIPS-verified references added | Corrected / New | — | References |
| 33 | Line numbers added for review | New | — | Whole manuscript |
| 34 | Response letter re-keyed to the authors' tracker items (R1-1…R1-5, A-1…A-12); new responses to A-4, A-9, A-10, A-12; day-40 example (R1-1) answered | Corrected | all | Response letter |
| 35 | Evidence grades E1/E0/R/I/U/X attached to every label (tracker Endpoint Rules); no label reaches E1/E0 | New | R1-1, A-4 | §2.4, Table 1 |
| 36 | Statement that the clarification request "has been sent" corrected to "prepared" (no evidence it was sent) | Corrected | R1-1 | §2.4 |
| 37 | Date-derived stays > 120 days (9 records) no longer used; recorded LOS used instead; full clean re-run (labelled 982, deaths 338) | Corrected | A-4 | §2.2, Table A.5 |
| 38 | Stay-by-disposition table, label-transition table and audit-count reconciliation table added | New | A-4, A-11 | Tables A.4–A.6 |
| 39 | Code-availability statement gives actual status (supplementary; not yet in a repository) | Corrected | A-10 | Back matter |
| 40 | Decision letter and reviewer comments received verbatim; every sentence mapped to a tracker item; items A-13 (reproducibility reporting) and E-1 (editor: source files) added; A-10–A-12 marked internal | New | all | Response letter; tracker |
| 41 | Later-follow-up completeness by period (705 patients, 44.6%; 87% in 2010–12, ≤16% from 2017) and sensitivity removing the 20 later-contact labels | New | A-4 | §2.4, §3.2, Table A.1, Table 10 |
| 42 | Imputation model fully specified (conditional model, iterations, auxiliary variables, outcome excluded, number of imputations); multiple imputation m = 5 with between-draw SD; missingness indicators for all 9 predictors > 20% missing; 17-predictor low-missing model | New | A-5 | §2.6, §3.12, Table 10 |
| 43 | "Why 30 days" justification and late in-hospital deaths as non-events stated explicitly | Corrected | A-4 | §2.4 |
| 44 | Tier table reports patients per death captured as the follow-up-effort illustration; stated not to be a resource consequence in the registry population | New | A-7 | §2.9, §3.10, Table 8 |
| 45 | Discussion restructured into four subsections (Principal findings; Comparison; Limitations; Implications); modelling contribution described as modest; hospital-record completeness over time addressed | Corrected | A-1, A-2, A-3 | §4 |
| 46 | Language pass: sentences split (none over 42 words in prose), one term per concept ("labelled" defined once), verbs over nouns, no coloured links; each limitation names the evidence that would resolve it | Corrected | — | Whole manuscript |
| 47 | High-level re-analysis protocol (v1.1) and TRIPOD+AI reporting map with verified locations added to the package | New | A-13 | Supplementary |
| 48 | Response letter rebuilt with verbatim quotations and old→new table/figure mapping (Tables 15, 16, 20; Figures 15, 17) | Corrected | all | Response letter |
| 49 | Title revised to "First-Month Mortality after Stroke in a Cameroonian Registry: Outcome Ascertainment and Development of an Admission-Time Prediction Model" (names population, outcome and model development per TRIPOD+AI item 1; drops model-centric "Interpretable") | Corrected | A-2, A-3 | Title |
| 50 | Abstract shortened from 314 to ≤250 words (journal limit, ScienceDirect Guide for Authors accessed 2 Nov 2026); no number changed | Corrected | E-1 | Abstract |
| 51 | Introduction: regional case-fatality sentence replaced (the cited meta-analysis reports a pooled one-month case-fatality of 24.1%, not a 20–40% in-hospital range; the cited Tanzanian cohort reports 50% at 90 days); bib key `kingston2019opportunities` renamed `regenhardt2019opportunities` and author list completed | Corrected (citation integrity) | — | Introduction ¶1 |
| 52 | Introduction: Cameroonian readmission figures corrected to match Nkoke et al. 2024 (15.2% readmitted within a year, not "roughly a third"; 30% of readmissions in month 1; 53.3% of readmitted died) | Corrected (citation integrity) | — | Introduction ¶1 |
| 53 | Introduction: citation to Ashu et al. 2022 (dialysis access, off-topic) removed; claim narrowed to health-system constraints (Oleribe et al. 2019) | Corrected (citation integrity) | — | Introduction ¶1 |
| 54 | Introduction: iScore and PLAN now cited to their derivation papers (Saposnik 2011; O'Donnell 2012, both verified in PubMed); the unsupported claim about "many African registries" replaced by a verifiable statement about this registry's fields; Mansour 2015 no longer cited for it | Corrected (citation integrity) | — | Introduction ¶2 |
| 55 | Intended use and users stated (prioritising post-discharge follow-up; hypothetical, not evaluated) | New | A-3, A-7 | Introduction ¶1; §2.1 |
| 56 | RECORD and STROBE cited as complementary reporting guidelines for the registry component; RECORD items added to the reporting map | New | A-13 | §2.1; `TRIPOD_AI_reporting_map.md` |
| 57 | Unit of analysis (admission) and inability to link repeat admissions stated in Methods and Limitations | New | A-13 | §2.1; §4.3 |
| 58 | Post hoc minimum sample size check (Riley et al. 2020): 27 candidate parameters; required n = 2,100 (conservative R²cs 0.11) or 592 (R²cs 0.35 implied by observed AUROC); 982 available. Code `tools/riley_samplesize.py`, output `riley_samplesize_posthoc.json` | New (post hoc, labelled as such) | A-13 | §2.8 (Sample size) |
| 59 | Wording inconsistency fixed: "three imputation sensitivity analyses" → "four" (Methods §2.6 lists four) | Corrected (consistency) | A-5 | §2.11 |
| 60 | Highlights file (5 bullets, ≤85 characters) prepared | New | E-1 | `highlights.txt` |
| 61 | Response letter: opening to the handling editor, explicit position per item (Agree / Partially agree), response matrix; statement that only one reviewer report was received | Corrected | All | Response letter |
| 62 | Registry data dictionary (received 2 Nov; 256 variables) audited against the workbook (new stage `stage1e_dictionary_audit.py`): 242 labels match exactly, most others differ only in spelling; patient name, two phone numbers, follow-up location and a first release date are not in the workbook; no value codes; 94 variables without type | New | R1-1, A-4 | Supplementary dictionary audit |
| 63 | Methods §2.4: `death1` now defined from the dictionary ("Death at Month 1, recording if the patient passed away within the first month"); follow-up assessments dated "after the stroke"; follow-up duration values (1 vs 30; 3 vs 90) interpreted as months vs days; statement "the available material does not define their time origin" replaced | Corrected | R1-1 | §2.4 |
| 64 | A1 and A2 now supported by the dictionary (A2: a death within one month of the stroke falls within 30 days of admission); still not verifiable against dates; evidence grades unchanged under the pre-specified rule | Corrected | R1-1, A-4 | §2.4; Table 1 |
| 65 | New sensitivity analyses for a stroke-anchored month-1 window: `death1` = No labels with onset-to-arrival delay > 72 h (unit inferred as hours; 109 of 617) treated as unresolved, AUROC 0.856 (n = 873); also unknown delay, 0.855 (n = 806) | New | R1-1 | §2.4, §2.11, §3.11, Table A (sensitivity) |
| 66 | Abstract, Discussion, Limitations, Implications and Conclusion updated for the dictionary (completion, not definition, changed; residual uncertainty: implicit time origin, no codes, no dates of death) | Corrected | R1-1, A-3 | Abstract; §4 |
| 67 | Provenance table timing labels: E2 "Assumption A2 (dictionary-supported)"; N2 "Established to month 1 after stroke" | Corrected | R1-1 | Table 1 |
| 68 | Response letter: R1-1 rewritten from the dictionary; status changed from CONDITIONAL to final draft for author approval, with residual uncertainty stated | Corrected | R1-1 | Letter |
| 69 | Tracker: R1-1, A-1, A-4 → Addressed; gate G1 → Complete (residual uncertainty stated); T2 → Complete | Corrected | — | Tracker |
| 70 | Clarification request: status section added (Q1, Q2, Q4, Q6 partly settled by the dictionary; remaining questions no longer blocking) | Corrected | R1-1 | Registry request |
| 71 | Stopping-criteria checker (`tools/loop_criteria.py`, C1–C12) and 8 new verifier checks for the dictionary (98 checks) | New | A-13 | Code |
| 72 | Loop iteration 3: duration-field wording made precise ("mostly"); arrival-delay heaping metric redefined as all positive multiples of 24 (42% of recorded values); C7 wording fixed in two documents | Corrected (consistency) | R1-1 | §2.4; `08_iteration_log` |
| 73 | Conclusion: hard-coded observed-only mortality (20.2%, June cohort) replaced by the generated figure for the revised cohort (20.4%, 160 of 784 with a recorded month-1 status); verifier check added | Corrected (consistency) | R1-2 | Conclusion |
| 74 | Methods 2.12: AI-assisted code development disclosed in Methods (Elsevier policy, checked 3 Nov 2026) in addition to the declaration; wording pending author approval | New | DECL-003 | §2.12 |
| 75 | Phase 2 rebuild: run modes with fail-safe on the outcome-definition approval state; SHA-256 run manifest; parser reconciliation tool; privacy check; 13 new tests; requirements traceability matrix; survival feasibility report | New | A-13 | Code and docs |

## Findings that remain unresolved

1. Meaning and time origin of `death1`; meaning of `death1 = No`; whether recording changed in 2014–15 by design (registry Q1–Q3, Q7).
2. Meaning of disposition "death" (A1) and "Other" (Q4–Q5); units of `duration followed` and codes 9/3 (Q6).
3. Dates of death of the 33 post-discharge events (Q12) — the single item that would resolve A2.
4. Missing dispositions in 2020 (Q8); pre-stroke vs admission Rankin score; timing of laboratory values (Q9).
5. Source adjudication of 38 duplicate groups and 25 date anomalies (Q10–Q11).
6. The submitted model results cannot be reproduced (final training code unavailable).
7. (Resolved 19 Oct) Verbatim reviewer comments were received and are quoted in the response letter.
9. Tracker A-11: the 194-row flag total and 28 clinical-difference groups of the preliminary audit cannot be reproduced without its build script.
10. Tracker A-12: overlap with the earlier post-discharge draft and any prior dissemination must be checked and disclosed by the authors.
8. Ethics approval date not verified against the IRB letter.
