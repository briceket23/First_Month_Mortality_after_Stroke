# Reproducibility report

- Clean run from an empty `outputs/` and `restricted/` on 3 November 2026 (execution_log.txt); 31 synthetic tests passed first; stage 3 took 2066s.
- Environment: Python 3.13.16; pandas 3.0.5, numpy 2.5.3, scipy 1.18.1, sklearn 1.9.1, xgboost 3.4.1, shap 0.54.1, statsmodels 0.15.0, openpyxl 3.1.5, matplotlib 3.11.2. Pinned in requirements.lock.txt. No artefact from the June project (scikit-learn 1.6.1 joblib bundles) was loaded.
- Determinism: macros of this run are byte-identical to the independent clean run of 2 November 2026 in the revision workspace (same seed, same versions).
- Provenance: `outputs/run_manifest.json` lists SHA-256 of the workbook, dictionary, every config file, every source file and every output file (53 outputs); analysis mode `reconstructed_provisional`; duplicate policy and outcome approval state recorded.
- Privacy: `tools/privacy_check.py outputs` PASS; row-level files confined to `restricted/` (git-ignored, excluded from the archive by allowlist; inspection in submission_package/stroke_reproducibility_rebuilt_ZIP_INVENTORY.md).
- Limitations: the submitted June model results remain not reproducible (final training code unavailable) and are superseded; the environment-specific speed of stage 3 (~35 min) is the only practical obstacle to re-running.
- Warnings: scikit-learn/xgboost deprecation warnings are suppressed with `-W ignore` in the runner; none affects results (tests run without suppression pass).
