# Statistical verification

| Item | Method | Result | Verified by |
|---|---|---|---|
| Paired AUROC differences | DeLong covariance of paired AUCs; CI = diff ± 1.96·SE | CV: LR − ClinRef 0.024 (0.010–0.038); temporal 0.022 (-0.027 to 0.070) | test_paired_auc_difference_interval_matches_paired_bootstrap (paired bootstrap within 0.03 of DeLong limits) |
| No equivalence claim | Text check | 'equivalent'/'matches' absent | verify.py |
| Calibration protocol | Primary uncalibrated; Platt/isotonic by `CalibratedClassifierCV(cv=StratifiedKFold(3))` inside each outer training fold | OOF slope 1.14, intercept -0.01; Platt slope 1.06, isotonic 0.84 | test_recalibration_and_tiers_never_use_test_data; code inspection |
| Risk tiers | Pre-specified < 10% / ≥ 40%; Wilson CIs; empty tiers reported | Low tier 158 patients OOF, 26 temporal | test_empty_risk_tier_is_reported_not_hidden |
| Temporal validation | One cut-off (2018-11-20) from all eligible admission dates, applied to primary/strict/observed-only | LR 0.833 (0.764–0.902), n = 136, 55 events; observed-only test has 4 events | verify.py (same cut-off in every table) |
| IPW | Logistic observation model; positivity restriction (recorded disposition); truncation p99; 1,000 bootstrap re-estimating weights | 27.5% (25.0–30.1); ESS 830 | stage 2 outputs |
| Delta-adjustment | Pattern-mixture, δ 0.25–8 | 26.6–41.7%; labelled-subset rate reached at δ 2–4 | verify.py fact check |
| Bounds | Deterministic (all unresolved alive/dead) | 21.4–59.2% | arithmetic check in verify.py |
| Multiple imputation | m = 5 posterior draws, pooled predictions | AUROC 0.864; between-draw SD 0.010 | stage 3 |
| Sample size | Riley et al. 2020 criteria, post hoc | required 2,100 / 592; available 982 | tools/riley_samplesize.py |
| Rank concordance | Spearman ρ with feature bootstrap | 0.56 (0.17–0.80), moderate | stage 3 |
| Selection comparison | SMDs | Table selbias | stage 2 |

All 99 verification checks passed (99/99): cohort arithmetic, leakage controls, hard-coded statements vs outputs, LaTeX build, letter integrity, dictionary checks, journal format, citation integrity.
