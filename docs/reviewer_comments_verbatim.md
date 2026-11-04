# Decision letter and reviewer comments — NEURI-D-26-00184 (verbatim, as supplied by the corresponding author on 19 October 2026)

**Decision:** reconsideration following major revision. **Resubmit by:** 6 November 2026. **Handling editor:** Prateek Singhal, PhD (Scientific Handling Editor, ext).

**Editor's notes:** upload the source files for the article (PDF manuscript files cannot be accommodated for production); follow the journal formatting guidelines (Guide for Authors: https://www.elsevier.com/journals/neuroscience-informatics/2772-5286/guide-for-authors); the revised submission may be re-reviewed.

## Reviewer #1

> This study is based on a single-center stroke registry cohort. Its core contribution is not simply the construction of a machine learning model, but rather the attempt to reconstruct missing 30-day mortality outcomes using in-hospital death, length of stay, and subsequent follow-up information, followed by mortality risk prediction. The article demonstrates innovation and clinical value, and is particularly applicable in regions with relatively limited medical resources. However, the following issues remain:

**[R1-1]** 1. The time origin for the 30-day endpoint may involve a definitional conflict. For example, if a patient was hospitalized for 20 days but died 40 days after admission (i.e., 20 days after discharge), a definitional contradiction arises. The authors must clearly define what "death1" actually represents and, where possible, reconstruct the 30-day outcome based on the actual date of death.

**[R1-2]** 2. The figure of 33.8% should not be reported as the "true 30-day mortality." Given that 594 of the 1,615 patients still had unknown 30-day status, 33.8% represents only the proportion of deaths among patients for whom a reconstructed outcome could be obtained, rather than the true mortality rate for the entire registry cohort.

### Additional

> Manuscript addresses a genuinely important methodological problem in stroke prognostication: the under-ascertainment of 30-day mortality in African stroke registries due to incomplete follow-up. The authors' central insight—that conventional missing-outcome exclusion preferentially discards fatal cases and biases mortality downward—is both correct and clinically significant. The transparent, provenance-tagged outcome reconstruction represents a real contribution to the literature on prognostic modelling in resource-limited settings.
> However, the manuscript has several structural, methodological, and reporting weaknesses that must be addressed before it can be considered for publication. The most serious concerns relate to:
> 1. The circularity of the reconstruction-validation relationship **[A-1]**
> 2. Insufficient separation between the ascertainment finding and the modelling contribution **[A-2]**
> 3. Overstated claims relative to the evidence **[A-3]**
> 4. Incomplete methodological reporting for reproducibility **[A-13]**
> 5. Limited external validity and lack of prospective validation **[A-9]**
> Below, I provide a detailed, section-by-section major revision.

**[A-1] Circularity in Outcome Reconstruction and Temporal Validation.** The temporal validation improvement (from AUROC 0.72 to 0.85) is presented as evidence that the reconstruction "resolves an apparent temporal-validation collapse." However, the reconstruction itself uses length-of-stay and discharge status to assign outcomes—information that is temporally correlated with the admission period. The later-period improvement may partly reflect the reconstruction's dependence on in-hospital data that became more complete over time, rather than a genuine correction of ascertainment bias.

**[A-2] Separation of Ascertainment Finding from Modelling Contribution.** The manuscript conflates two distinct contributions: (1) the epidemiological finding that missing-outcome exclusion under-ascertains mortality by ~14 percentage points, and (2) the modelling claim that an interpretable model performs comparably to a clinical reference. The abstract, introduction, and conclusion blur these, making it difficult for readers to assess the independent value of each.

**[A-3] Overstated Claims and Inappropriate Framing.** Several claims exceed what the data support:
- "An interpretable, well-calibrated model matches a simple clinical model and generalises across time" — This is based on a single-centre retrospective cohort with 345 events. "Generalises across time" is too strong for a temporal split within the same centre.
- "The contribution lies in the reconstruction method and the ascertainment finding as much as in the model" — The model contributes little beyond confirming that a simple clinical model performs comparably. The "as much as" overstates the modelling contribution.
- "First leakage-audited, calibrated, interpretable model of 30-day stroke mortality in Francophone Central Africa" — Priority claims require systematic review to substantiate. Either provide a systematic search or soften to "to our knowledge, one of the first."

**[A-4] Incomplete Reporting of Reconstruction Assumptions.** The reconstruction hierarchy (Section 2.2) is presented clearly, but several assumptions are not adequately justified:
- Length-of-stay ≤ 30 days for in-hospital deaths: Why 30 days? What is the distribution of length-of-stay for in-hospital deaths? If most in-hospital deaths occur within 7 days, the 30-day window may be too wide and may misclassify late in-hospital deaths as 30-day events.
- Discharged alive after >30 in-hospital days → alive at 30 days: This assumes that patients who remain in hospital beyond 30 days and are discharged alive did not die within 30 days of admission. This is reasonable but should be justified with data on the distribution of length-of-stay.
- Later follow-up (death3/6/9) proving survival beyond 30 days: How many patients had later follow-up? What was the completeness of later follow-up? If later follow-up is also incomplete, the reconstruction may introduce new biases.

**[A-5] Missing Data Handling and Imputation.** The manuscript states that MICE was used for predictor missingness, fitted on the training partition only. However:
- The missingness mechanism is not discussed. Is it missing at random (MAR), missing completely at random (MCAR), or missing not at random (MNAR)? NIHSS is 41.7% missing—this is substantial and likely MNAR (sicker patients may not have NIHSS recorded).
- The imputation model is not described. What variables were included? Were auxiliary variables used? How many imputations?
- The sensitivity analysis for NIHSS missingness (Table 20) is helpful but limited to NIHSS. Other variables (e.g., CRP, creatinine) also have substantial missingness.

**[A-6] Model Development and Comparator.** The primary model is an L2-penalised logistic regression, with tree-based challengers. The clinical-reference model is described as "parsimonious" but its exact specification is not fully reported.

**[A-7] Risk Stratification and Clinical Utility.** The three-tier risk scheme is presented as actionable, but:
- The tiers are derived on the validation set and frozen for the test set, but the test-set tier mortality (Table 15) shows a "Low" tier with 0% mortality and 0% deaths captured. This suggests the tier boundaries may not be well-calibrated for the test set.
- The pooled out-of-fold tiers (Table 16) show a more balanced distribution, but the manuscript does not explain why the single-split tiers collapsed.
- The clinical utility of the tiers is asserted but not demonstrated. What would be the downstream consequences of using these tiers for resource allocation?

**[A-8] Interpretability and Feature Importance.** The manuscript reports SHAP and permutation importance, but:
- The Glasgow-to-NIHSS ratio is highlighted as a key predictor, but its clinical interpretation is speculative. The authors acknowledge this in response to reviewers but the manuscript still overemphasises it.
- Cross-model concordance (Figure 15) is reported as Spearman ρ = 0.70, which is moderate, not high. This should be characterised more cautiously.
- LIME explanations (Figure 17) are presented for four cases, but there is no systematic evaluation of explanation stability or fidelity.

**[R1-3]** 3. The 594 patients without an obtainable 30-day outcome were not missing at random, and their NIHSS and mRS scores were significantly lower than those of patients included in the analysis. Simple exclusion may therefore introduce substantial selection bias. The authors are advised to further develop a prediction model for outcome ascertainability and to consider inverse-probability weighting, missing-not-at-random sensitivity analyses, or time-to-event approaches, rather than relying solely on complete-case exclusion.

**[R1-4]** 4. A DeLong test P value of 0.17 indicates only that the current sample does not provide sufficient evidence to conclude that the two AUCs differ. It does not demonstrate equivalence between the two models; this represents a statistical logical error. The authors are advised to report the difference in AUC with its 95% confidence interval. If equivalence or non-inferiority is to be claimed, a pre-specified margin with clinical justification is required.

**[R1-5]** 5. The manuscript should clearly specify the dataset used for fitting and selecting the Platt and isotonic recalibration models. If the calibration method was selected based on results from the test set, then the test set can no longer be considered an independent evaluation set. The authors are advised to ensure that calibration model fitting and selection are performed entirely on the training/validation data, with only a single final evaluation conducted on the locked test set.

---
Bracketed codes are the tracker item IDs. A-13 (methodological reporting for reproducibility) and E-1 (editor: source files and formatting) were added on 19 October because the tracker had no row for them; A-10 (code-availability statement), A-11 (audit flag counts) and A-12 (earlier draft) are internal items, not reviewer comments.
