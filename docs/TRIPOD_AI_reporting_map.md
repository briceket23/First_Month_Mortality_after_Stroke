# TRIPOD+AI and RECORD reporting map — NEURI-D-26-00184 (revision 1)

Locations are read from the compiled revised manuscript. Topic wording is abbreviated; transfer to the official TRIPOD+AI checklist form (Collins et al. 2024, tripod-statement.org) before upload.

| Topic | What is expected | Where reported | Status |
|---|---|---|---|
| Title | Identifies the study as developing/evaluating a prediction model; population, outcome | Title page (revised: names population, outcome and model development) | Reported |
| Abstract | Structured summary with objectives, data, outcome, predictors, methods, results, conclusions | Abstract | Reported |
| Background | Healthcare context, rationale, intended use and users of the model | Introduction (paragraph 1, intended use); Section 2.1 (study design) | Reported; intended use stated as hypothetical and not evaluated |
| Objectives | Objectives, including whether development and/or evaluation | Introduction, p. 2, line 18 | Reported |
| Data source | Source, setting, dates of data collection, registry description | Section 2.2 (p. 2) (setting) and Section 2.2 (p. 2) | Reported |
| Participants / eligibility | Eligibility criteria, exclusions, flow of participants | Eligibility paragraph after Section 2.2 (p. 2); Figure 1 (p. 8) | Reported |
| Data preparation | Cleaning, unit harmonisation, integrity flags, duplicate handling | Section 2.2 (p. 2); Section 2.6 (p. 5); Table A.4 (p. 22) | Reported |
| Outcome | Definition, time origin, window, provenance, assumptions, blinding | Section 2.4 (p. 3); Table 1 (p. 4) | Reported; definition conditional on registry confirmation (stated) |
| Predictors | Definition, timing (admission), measurement, exclusion of post-admission variables | Section 2.6 (p. 5) | Reported |
| Sample size | Events, candidate predictors, events per predictor, justification | p. 6, line 197 (post hoc Riley criteria); Table 5 (p. 11) | Reported (no a priori calculation; post hoc check met only under the AUROC-based assumption; stated) |
| Missing data | Amount, mechanism discussion, imputation method, variables, iterations, fold-wise fitting, sensitivity | Section 2.6 (p. 5); Table A.7 (p. 23); Table 10 (p. 16) | Reported |
| Analytical methods: model types | Primary model, challengers, comparator with full specification | Section 2.7 (p. 5) | Reported |
| Analytical methods: tuning and selection | Hyperparameter grids, inner CV, no data-driven feature selection | Section 2.7 (p. 5); Section 2.8 (p. 6) | Reported |
| Analytical methods: validation | Nested CV; temporal split with pre-fixed cut-off; separation of development and evaluation | Section 2.8 (p. 6) | Reported |
| Analytical methods: performance measures | Discrimination, calibration, clinical utility, paired comparison, uncertainty | Section 2.9 (p. 6) | Reported |
| Class imbalance | Outcome prevalence and handling (no class weighting; reasons) | Section 2.7 (p. 5) | Reported |
| Fairness / subgroups | Subgroup performance (sex, subtype, period, NIHSS recorded) | Section 3.12 (p. 15); Table A.10 (p. 23) | Reported |
| Model output and intended use | Probability output; pre-specified risk tiers; no clinical deployment claimed | Section 2.9 (p. 6); Section 3.10 (p. 13) | Reported |
| Ethical approval | IRB reference and consent waiver | Ethics approval statement | Reported (date to be verified against IRB letter) |
| Protocol / registration | Analysis protocol and pre-fixed design; no registration | Supplementary: 00_reanalysis_protocol.md; not registered (stated here) | Partly: protocol supplied; not registered |
| Data sharing | Availability and access conditions | Data and code availability statement | Reported |
| Code sharing | Complete code supplied; repository status | Data and code availability statement, p. 18, line 454 | Reported (not yet deposited; stated) |
| Public involvement | Patient and public involvement | Not undertaken | Not applicable / not done (state in manuscript if required) |
| Results: participants | Flow, numbers, characteristics, outcome distribution, unresolved outcomes | Figure 1 (p. 8); Table 4 (p. 11); Table 3 (p. 10) | Reported |
| Results: model development | Selected hyperparameters, final specification, coefficients | Section 3.11 (p. 13); Table 9 (p. 15) | Reported |
| Results: model performance | Discrimination, calibration, utility with uncertainty; paired comparison; temporal | Table 5 (p. 11); Table 6 (p. 12); Table 7 (p. 12); Figure 5 (p. 13) | Reported |
| Results: sensitivity analyses | Endpoint variants, duplicates, imputation, era, IPW | Table 10 (p. 16) | Reported |
| Discussion: interpretation | Main findings for each question; comparison with literature | p. 16, line 365; p. 16, line 378 | Reported |
| Discussion: limitations | Specific limitations and what would resolve them | Section 4.3 (p. 17) | Reported |
| Discussion: usability and next steps | External validation, prospective ascertainment, no clinical use yet | p. 17, line 428; Conclusion | Reported |

## RECORD (extension of STROBE) items specific to routinely collected data

Item numbers follow Benchimol et al., PLoS Med 2015;12:e1001885. STROBE core items overlap with the TRIPOD+AI topics above and are not repeated.

| RECORD item | What is expected | Where reported | Status |
|---|---|---|---|
| 1.1-1.2 | Type of data, region and time frame in title/abstract | Title; Abstract (Methods) | Reported |
| 1.3 | Linkage between databases stated | Not applicable: single registry, no linkage | Not applicable |
| 6.1 | Methods of population selection (codes/algorithms) listed | Eligibility subsection; Figure 1 (p. 8) | Reported |
| 6.2 | Validation studies of codes or algorithms | Section 2.4 (p. 3) (data dictionary definitions; evidence grades); supplementary dictionary audit | Reported; dictionary gives definitions but no value codes or explicit time origin (stated) |
| 6.3 | Linkage methods and quality | Not applicable; repeat admissions cannot be linked (study design subsection) | Stated |
| 7.1 | Complete list of codes/algorithms for outcome, predictors, covariates | Section 2.4 (p. 3); Section 2.6 (p. 5); supplementary code | Reported |
| 12.1 | Extent of investigators' access to the database | Data and code availability statement | Partly: access route stated; extent of access to source records [AUTHOR VERIFICATION] |
| 12.2 | Data cleaning methods | Section 2.2 (p. 2); Table A.4 (p. 22) | Reported |
| 12.3 | Linkage | Not applicable | Not applicable |
| 13.1 | Selection of persons, with flow diagram | Figure 1 (p. 8) | Reported |
| 19.1 | Implications of data not created for the research question (misclassification, missing data, changing recording) | Section 4.3 (p. 17); p. 16, line 365 | Reported |
| 22.1 | Access to protocol, raw data and programming code | Data and code availability statement; supplementary protocol | Reported |
