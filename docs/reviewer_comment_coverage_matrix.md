# 10 — Reviewer and editor comment coverage matrix

Every sentence, numbered point, narrative paragraph and bullet of `reviewer_comments.txt` is mapped to at least one ticket. Extracts are verbatim and shortened with ellipses only.

| Source | Extract | Ticket IDs |
|---|---|---|
| Editor | “please upload the source files for your article. We cannot accommodate PDF manuscript files” | SUBM-001, SUBM-002, SUBM-003 |
| Editor | “follow the journal formatting guidelines … Guide for Authors” | SUBM-004 |
| Editor | “your revised submission may need to be re-reviewed” | CLAIM-001, REPRO-002 |
| R1 preamble | “single-center stroke registry cohort” | CLAIM-004, VAL-TEMP-003 |
| R1 preamble | “attempt to reconstruct missing 30-day mortality outcomes using in-hospital death, length of stay, and subsequent follow-up information” | OUTCOME-TIME-001, OUTCOME-REC-001, OUTCOME-REC-003, DATA-DATE-002 |
| R1 preamble | “demonstrates innovation and clinical value … regions with relatively limited medical resources” | CLAIM-001, STAT-RISK-002 |
| R1 point 1 | “time origin for the 30-day endpoint may involve a definitional conflict” | OUTCOME-TIME-001 |
| R1 point 1 | “hospitalized for 20 days but died 40 days after admission (i.e., 20 days after discharge)” | OUTCOME-TIME-001, OUTCOME-TIME-002 |
| R1 point 1 | “clearly define what "death1" actually represents” | OUTCOME-TIME-001, OUTCOME-TIME-002, DATA-DICT-002 |
| R1 point 1 | “reconstruct the 30-day outcome based on the actual date of death” | OUTCOME-TIME-003, OUTCOME-TIME-004 |
| R1 point 2 | “33.8% should not be reported as the "true 30-day mortality"” | EPI-MORT-001 |
| R1 point 2 | “594 of the 1,615 patients still had unknown 30-day status” | DATA-DUP-001, EPI-SEL-001, OUTCOME-REC-005 |
| R1 point 2 | “only the proportion of deaths among patients for whom a reconstructed outcome could be obtained” | EPI-MORT-001, EPI-MORT-002 |
| Additional, para 1 | “central insight—that conventional missing-outcome exclusion preferentially discards fatal cases and biases mortality downward—is both correct” | EPI-MORT-001, EPI-MORT-002, VAL-TEMP-001 |
| Additional, para 1 | “transparent, provenance-tagged outcome reconstruction represents a real contribution” | OUTCOME-REC-005 |
| Additional, concern 1 | “The circularity of the reconstruction-validation relationship” | VAL-TEMP-001, VAL-TEMP-002 |
| Additional, concern 2 | “Insufficient separation between the ascertainment finding and the modelling contribution” | CLAIM-001, CLAIM-002 |
| Additional, concern 3 | “Overstated claims relative to the evidence” | CLAIM-002, CLAIM-003, VAL-TEMP-003, STAT-AUC-002, STAT-RISK-002 |
| Additional, concern 4 | “Incomplete methodological reporting for reproducibility” | REPRO-001, REPRO-002, MODEL-IMP-001, MODEL-LIST-001, MODEL-COMP-001, MODEL-LEAK-001, STAT-SIZE-001 |
| Additional, concern 5 | “Limited external validity and lack of prospective validation” | CLAIM-004, VAL-TEMP-003 |
| Circularity section | “temporal validation improvement (from AUROC 0.72 to 0.85) is presented as evidence that the reconstruction "resolves an apparent temporal-validation collapse"” | VAL-TEMP-001, VAL-TEMP-002 |
| Circularity section | “reconstruction itself uses length-of-stay and discharge status … temporally correlated with the admission period” | VAL-TEMP-001, OUTCOME-REC-005 |
| Circularity section | “may partly reflect the reconstruction's dependence on in-hospital data that became more complete over time” | VAL-TEMP-001 |
| Separation section | “(1) the epidemiological finding that missing-outcome exclusion under-ascertains mortality by ~14 percentage points” | EPI-MORT-002 |
| Separation section | “(2) the modelling claim that an interpretable model performs comparably to a clinical reference” | STAT-AUC-001, STAT-AUC-002, CLAIM-002 |
| Separation section | “The abstract, introduction, and conclusion blur these” | CLAIM-001 |
| Overstated claims, bullet 1 | “"An interpretable, well-calibrated model matches a simple clinical model and generalises across time"” | VAL-TEMP-003, STAT-AUC-002, STAT-CAL-001 |
| Overstated claims, bullet 1 | “single-centre retrospective cohort with 345 events” | CLAIM-004, STAT-SIZE-001 |
| Overstated claims, bullet 2 | “"The contribution lies in the reconstruction method and the ascertainment finding as much as in the model"” | CLAIM-002 |
| Overstated claims, bullet 3 | “"First leakage-audited, calibrated, interpretable model … Francophone Central Africa"” | CLAIM-003 |
| Reconstruction assumptions, intro | “The reconstruction hierarchy (Section 2.2) is presented clearly, but several assumptions are not adequately justified” | OUTCOME-REC-005 |
| Reconstruction assumptions, bullet 1 | “Length-of-stay ≤ 30 days for in-hospital deaths: Why 30 days? … may misclassify late in-hospital deaths as 30-day events” | OUTCOME-REC-001, DATA-DATE-002 |
| Reconstruction assumptions, bullet 2 | “Discharged alive after >30 in-hospital days → alive at 30 days” | OUTCOME-REC-002 |
| Reconstruction assumptions, bullet 3 | “Later follow-up (death3/6/9) proving survival beyond 30 days: How many patients had later follow-up? What was the completeness” | OUTCOME-REC-003 |
| Missing data, intro | “The manuscript states that MICE was used for predictor missingness, fitted on the training partition only” | MODEL-IMP-001 |
| Missing data, bullet 1 | “Is it missing at random (MAR), missing completely at random (MCAR), or missing not at random (MNAR)? NIHSS is 41.7% missing” | MODEL-IMP-002, EPI-SEL-001 |
| Missing data, bullet 2 | “What variables were included? Were auxiliary variables used? How many imputations?” | MODEL-IMP-001 |
| Missing data, bullet 3 | “limited to NIHSS. Other variables (e.g., CRP, creatinine) also have substantial missingness” | MODEL-IMP-002 |
| Model development | “The clinical-reference model is described as "parsimonious" but its exact specification is not fully reported” | MODEL-COMP-001 |
| Model development | “L2-penalised logistic regression, with tree-based challengers” | MODEL-LIST-001, MODEL-LEAK-002 |
| Risk stratification, bullet 1 | “"Low" tier with 0% mortality and 0% deaths captured … boundaries may not be well-calibrated for the test set” | STAT-RISK-001 |
| Risk stratification, bullet 2 | “pooled out-of-fold tiers (Table 16) show a more balanced distribution, but the manuscript does not explain why the single-split tiers collapsed” | STAT-RISK-001 |
| Risk stratification, bullet 3 | “clinical utility of the tiers is asserted but not demonstrated. What would be the downstream consequences” | STAT-RISK-002 |
| Interpretability, bullet 1 | “Glasgow-to-NIHSS ratio … clinical interpretation is speculative” | XAI-001 |
| Interpretability, bullet 2 | “Spearman ρ = 0.70, which is moderate, not high” | XAI-002 |
| Interpretability, bullet 3 | “LIME explanations (Figure 17) … no systematic evaluation of explanation stability or fidelity” | XAI-003 |
| R1 point 3 | “594 patients without an obtainable 30-day outcome were not missing at random” | EPI-SEL-001, MODEL-IMP-002 |
| R1 point 3 | “NIHSS and mRS scores were significantly lower than those of patients included” | EPI-SEL-001 |
| R1 point 3 | “Simple exclusion may therefore introduce substantial selection bias” | EPI-MORT-001, EPI-SEL-003 |
| R1 point 3 | “develop a prediction model for outcome ascertainability” | EPI-SEL-002 |
| R1 point 3 | “inverse-probability weighting” | EPI-SEL-003 |
| R1 point 3 | “missing-not-at-random sensitivity analyses” | EPI-SEL-004 |
| R1 point 3 | “time-to-event approaches” | EPI-SURV-001, OUTCOME-REC-004 |
| R1 point 4 | “DeLong test P value of 0.17 indicates only that the current sample does not provide sufficient evidence” | STAT-AUC-001 |
| R1 point 4 | “It does not demonstrate equivalence … statistical logical error” | STAT-AUC-002 |
| R1 point 4 | “report the difference in AUC with its 95% confidence interval” | STAT-AUC-001 |
| R1 point 4 | “If equivalence or non-inferiority is to be claimed, a pre-specified margin with clinical justification is required” | STAT-AUC-002 |
| R1 point 5 | “specify the dataset used for fitting and selecting the Platt and isotonic recalibration models” | STAT-CAL-001 |
| R1 point 5 | “If the calibration method was selected based on results from the test set …” | STAT-CAL-001 |
| R1 point 5 | “calibration model fitting and selection are performed entirely on the training/validation data, with only a single final evaluation conducted on the locked test set” | STAT-CAL-001, STAT-RISK-001 |

Tickets referenced by at least one reviewer/editor statement: 47 of 60. Tickets not referenced arise from the package audit (data, code, declarations, submission mechanics) and are listed below.

| Package-audit-only tickets |
|---|
| DATA-DUP-002 — Replace keep="first" deduplication in all four pipeline stages |
| DATA-DATE-001 — Reconcile the Pandas vs openpyxl LOS/date diagnostic counts |
| DATA-DATE-003 — Negative intervals and impossible years must be flagged, never corrected |
| DATA-DICT-001 — Parse the dictionary correctly (cp1252, ';') and record dictionary–workbook mismatches |
| OUTCOME-REC-006 — Manuscript statement of telephone follow-up at days 7, 14 and 30 after discharge is unsupported |
| REPRO-003 — Row-level data and raw workbook present in stroke_project (data/raw, interim, processed, joblib, outputs.zip) |
| REPRO-004 — CITATION.cff has placeholder authors and DOI |
| DECL-001 — IRB reference/date in main.tex vs CORRECTIONS.md placeholder |
| DECL-002 — CRediT roles populated in main.tex vs 'individual CRediT roles' pending in CORRECTIONS.md |
| DECL-003 — Generative-AI declaration says no AI was used; revision was prepared with AI assistance |
| DECL-004 — Data/code availability statement contradictory (openly released vs on request vs future deposit); no repository exists |
| DECL-005 — Funding, competing interests and co-author approval of the final manuscript |
| ADMIN-001 — Manuscript title vs repository/README titles mismatch |