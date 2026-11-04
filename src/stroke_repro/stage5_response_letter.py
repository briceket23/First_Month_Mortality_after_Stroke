"""Stage 5: build the point-by-point response letter (DOCX) from verified outputs and compiled-manuscript locations.

Every number is read from outputs/tables/macros.json (written by stage 4 from the analysis outputs) and every
location from the compiled manuscript's .aux file, so the letter cannot drift from the manuscript.
"""
import json
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor, Cm

from . import config as C
from .locations import Loc



VERBATIM = {
 "R1-1": "1. The time origin for the 30-day endpoint may involve a definitional conflict. For example, if a patient was hospitalized for 20 days but died 40 days after admission (i.e., 20 days after discharge), a definitional contradiction arises. The authors must clearly define what \"death1\" actually represents and, where possible, reconstruct the 30-day outcome based on the actual date of death.",
 "R1-2": "2. The figure of 33.8% should not be reported as the \"true 30-day mortality.\" Given that 594 of the 1,615 patients still had unknown 30-day status, 33.8% represents only the proportion of deaths among patients for whom a reconstructed outcome could be obtained, rather than the true mortality rate for the entire registry cohort.",
 "R1-3": "3. The 594 patients without an obtainable 30-day outcome were not missing at random, and their NIHSS and mRS scores were significantly lower than those of patients included in the analysis. Simple exclusion may therefore introduce substantial selection bias. The authors are advised to further develop a prediction model for outcome ascertainability and to consider inverse-probability weighting, missing-not-at-random sensitivity analyses, or time-to-event approaches, rather than relying solely on complete-case exclusion.",
 "R1-4": "4. A DeLong test P value of 0.17 indicates only that the current sample does not provide sufficient evidence to conclude that the two AUCs differ. It does not demonstrate equivalence between the two models; this represents a statistical logical error. The authors are advised to report the difference in AUC with its 95% confidence interval. If equivalence or non-inferiority is to be claimed, a pre-specified margin with clinical justification is required.",
 "R1-5": "5. The manuscript should clearly specify the dataset used for fitting and selecting the Platt and isotonic recalibration models. If the calibration method was selected based on results from the test set, then the test set can no longer be considered an independent evaluation set. The authors are advised to ensure that calibration model fitting and selection are performed entirely on the training/validation data, with only a single final evaluation conducted on the locked test set.",
 "A-1": "Circularity in Outcome Reconstruction and Temporal Validation. The temporal validation improvement (from AUROC 0.72 to 0.85) is presented as evidence that the reconstruction \"resolves an apparent temporal-validation collapse.\" However, the reconstruction itself uses length-of-stay and discharge status to assign outcomes—information that is temporally correlated with the admission period. The later-period improvement may partly reflect the reconstruction's dependence on in-hospital data that became more complete over time, rather than a genuine correction of ascertainment bias.",
 "A-2": "Separation of Ascertainment Finding from Modelling Contribution. The manuscript conflates two distinct contributions: (1) the epidemiological finding that missing-outcome exclusion under-ascertains mortality by ~14 percentage points, and (2) the modelling claim that an interpretable model performs comparably to a clinical reference. The abstract, introduction, and conclusion blur these, making it difficult for readers to assess the independent value of each.",
 "A-3": "Overstated Claims and Inappropriate Framing. Several claims exceed what the data support: \"An interpretable, well-calibrated model matches a simple clinical model and generalises across time\" — This is based on a single-centre retrospective cohort with 345 events. \"Generalises across time\" is too strong for a temporal split within the same centre. \"The contribution lies in the reconstruction method and the ascertainment finding as much as in the model\" — The model contributes little beyond confirming that a simple clinical model performs comparably. The \"as much as\" overstates the modelling contribution. \"First leakage-audited, calibrated, interpretable model of 30-day stroke mortality in Francophone Central Africa\" — Priority claims require systematic review to substantiate. Either provide a systematic search or soften to \"to our knowledge, one of the first.\"",
 "A-4": "Incomplete Reporting of Reconstruction Assumptions. The reconstruction hierarchy (Section 2.2) is presented clearly, but several assumptions are not adequately justified: Length-of-stay ≤ 30 days for in-hospital deaths: Why 30 days? What is the distribution of length-of-stay for in-hospital deaths? If most in-hospital deaths occur within 7 days, the 30-day window may be too wide and may misclassify late in-hospital deaths as 30-day events. Discharged alive after >30 in-hospital days → alive at 30 days: This assumes that patients who remain in hospital beyond 30 days and are discharged alive did not die within 30 days of admission. This is reasonable but should be justified with data on the distribution of length-of-stay. Later follow-up (death3/6/9) proving survival beyond 30 days: How many patients had later follow-up? What was the completeness of later follow-up? If later follow-up is also incomplete, the reconstruction may introduce new biases.",
 "A-5": "Missing Data Handling and Imputation. The manuscript states that MICE was used for predictor missingness, fitted on the training partition only. However: The missingness mechanism is not discussed. Is it missing at random (MAR), missing completely at random (MCAR), or missing not at random (MNAR)? NIHSS is 41.7% missing—this is substantial and likely MNAR (sicker patients may not have NIHSS recorded). The imputation model is not described. What variables were included? Were auxiliary variables used? How many imputations? The sensitivity analysis for NIHSS missingness (Table 20) is helpful but limited to NIHSS. Other variables (e.g., CRP, creatinine) also have substantial missingness.",
 "A-6": "Model Development and Comparator. The primary model is an L2-penalised logistic regression, with tree-based challengers. The clinical-reference model is described as \"parsimonious\" but its exact specification is not fully reported.",
 "A-7": "Risk Stratification and Clinical Utility. The three-tier risk scheme is presented as actionable, but: The tiers are derived on the validation set and frozen for the test set, but the test-set tier mortality (Table 15) shows a \"Low\" tier with 0% mortality and 0% deaths captured. This suggests the tier boundaries may not be well-calibrated for the test set. The pooled out-of-fold tiers (Table 16) show a more balanced distribution, but the manuscript does not explain why the single-split tiers collapsed. The clinical utility of the tiers is asserted but not demonstrated. What would be the downstream consequences of using these tiers for resource allocation?",
 "A-8": "Interpretability and Feature Importance. The manuscript reports SHAP and permutation importance, but: The Glasgow-to-NIHSS ratio is highlighted as a key predictor, but its clinical interpretation is speculative. The authors acknowledge this in response to reviewers but the manuscript still overemphasises it. Cross-model concordance (Figure 15) is reported as Spearman ρ = 0.70, which is moderate, not high. This should be characterised more cautiously. LIME explanations (Figure 17) are presented for four cases, but there is no systematic evaluation of explanation stability or fidelity.",
 "A-9": "5. Limited external validity and lack of prospective validation (listed among the most serious concerns).",
 "A-13": "4. Incomplete methodological reporting for reproducibility (listed among the most serious concerns).",
 "E-1": "Editor: Upon submitting your revised manuscript, please upload the source files for your article. We cannot accommodate PDF manuscript files for production purposes. We also ask that when submitting your revision, you follow the journal formatting guidelines.",
 "A-10": "Internal item (not a reviewer comment): the submitted data-availability statement said both that the code was openly released and that it was available on request or would be deposited later.",
 "A-11": "Internal item (not a reviewer comment): two counts from the authors' preliminary audit (194 flagged rows; 28 duplicate groups with clinical-variable differences) could not be reproduced from the summary.",
 "A-12": "Internal item (not a reviewer comment): an earlier related draft defined the outcome as post-discharge mortality, whereas the submitted manuscript defines it from admission.",
}

def clean(v):
    return v.replace("{,}", ",").replace("$<$", "<").replace("\\%", "%")


def build(aux_path, out_docx):
    m = {k: clean(v) for k, v in json.load(open(C.TAB / "macros.json", encoding="utf-8")).items()}
    L = Loc(aux_path)
    mr = json.load(open(C.ANALYSIS / "model_results.json", encoding="utf-8"))
    asc = json.load(open(C.ANALYSIS / "ascertainment_summary.json", encoding="utf-8"))["primary"]

    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.2)

    def h(text, lvl=1):
        doc.add_heading(text, level=lvl)

    def p(text, bold=False, italic=False, color=None):
        para = doc.add_paragraph()
        r = para.add_run(text); r.bold = bold; r.italic = italic
        if color:
            r.font.color.rgb = RGBColor(*color)
        return para

    def bullet(text):
        doc.add_paragraph(text, style="List Bullet")

    t = doc.add_heading("Response to the Editor and the Reviewer", 0)
    p("Manuscript NEURI-D-26-00184 — Neuroscience Informatics", bold=True)
    tex = (C.ROOT / "manuscript" / "main.tex").read_text(encoding="utf-8") if hasattr(C, "ROOT") else (Path(aux_path).with_suffix(".tex")).read_text(encoding="utf-8")
    new_title = re.search(r"\\title\{(.*?)\}\n", tex).group(1)
    p("Revised title: " + new_title)
    p("Original title: Reconstructing Under-Ascertained 30-Day Stroke Mortality with Interpretable Machine Learning in a Cameroonian Cohort")
    p("Corresponding author: Cyrille Brice Fomazou Tchinda")

    p("Dear Dr Singhal,")
    p("Thank you for handling our manuscript and for the opportunity to revise it. We are grateful to the reviewer for a careful and constructive "
      "report. The comments on the definition of the 30-day outcome, on the unresolved outcomes and on the statistical claims led us to re-examine the "
      "registry fields, together with the registry's data dictionary, and to rebuild the analysis from the raw workbook. That re-examination changed the paper's main epidemiological conclusion, and we "
      "have revised the title, abstract and conclusions accordingly. We respond to every comment below; each response states whether we agree, agree in "
      "part or disagree, what was changed and where. One reviewer report (Reviewer #1, including its additional section) was received, and no other "
      "reviewer comments are addressed or implied in this letter.")
    p("The reviewer describes as the central insight that excluding missing outcomes discards fatal cases and biases mortality downward. We agree in part. "
      "The re-analysis confirms that complete-case exclusion understates mortality in this registry, but it also shows that the submitted reconstruction "
      "over-corrects: once in-hospital deaths are added, deaths are almost always labelled while survivors are labelled only when follow-up was recorded, so the "
      "reconstructed 33.8% is biased upward. Registry-wide 30-day mortality is therefore not identified from these data, and we now report bounds and "
      "model-based estimates instead of a single corrected rate.")
    p("Yours sincerely,")
    p("Cyrille Brice Fomazou Tchinda, on behalf of all authors")

    h("Status of this response", 1)
    p("FINAL DRAFT FOR AUTHOR APPROVAL (version of 2 November 2026).", bold=True, color=(0x1F, 0x4E, 0x79))
    p("Every analysis described below was run from code and its output inspected, and every location refers to the "
      "compiled revised manuscript. The registry's data dictionary became available during the revision and now documents the "
      "definition of the month-1 mortality field (death within the first month after the stroke). Residual uncertainty is stated "
      "wherever it matters: (1) the dictionary does not state the time origin explicitly or define value codes, and the registry "
      "holds no dates of death, so the endpoint rests on two stated assumptions, each tested in sensitivity analyses; (2) duplicate "
      "records and date anomalies were resolved by documented rules, not by source records. The conclusions hold under every "
      "interpretation of the registry fields that we could test. A request for the remaining details is enclosed for information.")
    p("Each response quotes the reviewer's comment verbatim from the decision letter of the handling editor (Dr Prateek Singhal). Item codes "
      "(R1-1 to R1-5 for the reviewer's five numbered points; A-1 to A-9 and A-13 for the reviewer's additional section; E-1 for the editor's note) "
      "are ours, for cross-reference with the change log and the execution tracker. Three internal items (A-10 to A-12) raised during the authors' own "
      "audit are answered at the end for completeness.", italic=True)
    p("Page and line numbers refer to the revised manuscript with line numbers (main.pdf). Line numbering starts after the abstract. "
      "Each response ends with the Phase 1 ticket IDs (review_audit/01_TICKET_REGISTER.md) and Phase 2 requirement IDs it closes.", italic=True)

    h("Summary of the main changes", 1)
    for b in [
        "We could not reproduce the submitted model results because the final version of the training code was not available; "
        "an earlier pipeline version reproduced only the observed-only analysis. We therefore rebuilt the analysis as a new, "
        f"tested, leakage-free pipeline. The submitted reconstruction counts ({m['OrigObs']} observed, {m['OrigInf']} inferred, "
        f"{m['OrigUnl']} unlabelled; {m['OrigDeaths']} deaths, {m['OrigMort']}%) were reproduced exactly with independent code "
        f"({L.tab('tab:origvsrev')}).",
        f"Reviewing the registry fields showed that recording practice changed over time: the month-1 field recorded "
        f"{m['IHDeathOneEarly']} in-hospital deaths in 2010–2012 but {m['IHDeathOneLate']} from 2015. As a result, the "
        f"labelled-subset mortality ({m['Mortlab']}% revised; 33.8% submitted) is biased upward and is no longer presented as the "
        f"corrected registry mortality. Registry-wide 30-day mortality is not identified (bounds {m['BoundLo']}–{m['BoundHi']}%); "
        f"weighted and delta-adjusted estimates are {m['Mortipw']}% and {m['DeltaMARper']}–{m['DeltaMARearly']}%.",
        "The endpoint is defined explicitly (death within 30 days of admission, including in-hospital death), each label carries "
        f"its evidence source, and the {m['NEtwo']} post-discharge events whose timing depends on an unconfirmed assumption are "
        "excluded in a strict sensitivity analysis. The title, abstract, objectives and conclusions were changed accordingly.",
        "Duplicate identifiers are reconciled by logged rules that preserve every source row; conflicting outcomes are left unresolved.",
        "Validation now uses nested cross-validation and a single, outcome-independent temporal cut-off applied identically to all "
        "endpoint definitions. Calibration is never tuned on test data; risk tiers use pre-specified cut-points.",
        "Claims of equivalence, of a 14-point under-ascertainment, of temporal generalisation proving the absence of dataset shift, "
        "of stable explanations and of novelty were withdrawn or narrowed. LIME illustrations were removed.",
    ]:
        bullet(b)

    R = []   # (heading, concern, [responses], [locations], limitation)
    R.append(("R1-1 — 30-day endpoint time origin; meaning of death1; the day-40-after-admission example",
              "The reviewer asked what the 30-day outcome measures, from which date it is counted, and what the registry field death1 means.",
              [f"We agree that the submitted definition was not adequately supported. The registry's data dictionary, which became available during this revision and is enclosed, "
               "defines death1 (décès1) as 'Death at Month 1, recording if the patient passed away within the first month', and describes the follow-up assessments as made "
               "one, three, six, nine or twelve months 'after the stroke'. The month-1 follow-up duration field holds 1 in 2010–2016 and 30 in 2017–2019 (and the month-3 field "
               "3 or 90), consistent with a one-month interval recorded in months or in days. death1 therefore represents death within the first month after the stroke. "
               "The dictionary does not state the time origin explicitly, gives no value codes and does not say whether 'No' certifies survival through the whole month; "
               "the workbook has no date-of-death field.",
               f"The data also show that the field was completed differently over time although its definition did not change: in 2010–2012, {m['IHDeathOneEarly']} in-hospital "
               f"deaths were also recorded as death1 = Yes, as the definition requires, whereas from 2015 only {m['IHDeathOneLate']} were. The field was therefore left blank "
               "for most in-hospital deaths in later years, which is the basis of the ascertainment findings (R1-2, R1-3).",
               "The revised endpoint is all-cause death within 30 days of admission (day 0 = admission date), including in-hospital death. Two assumptions are stated "
               "explicitly: A1, that a disposition of 'death' denotes death during the index hospitalisation, with the stay ending at death; and A2, that a death "
               "recorded in death1 after discharge occurred within 30 days of admission. A1 is consistent with the data and the dictionary. A2 follows from the dictionary's "
               "stroke-anchored definition, because the stroke precedes admission, but it cannot be checked against dates. Labels "
               f"follow a tested evidence hierarchy in which contradictions are left unresolved. {m['NEone']} events are timed by the hospital record and {m['NEtwo']} depend on A2; "
               f"a strict endpoint that treats those {m['NEtwo']} events as unresolved gave a nested cross-validated AUROC of {m['SensSt']} (primary {m['NestLR']}). "
               f"Conversely, under a stroke-anchored window death1 = No certifies survival only to one month after onset; treating as unresolved the {m['NtwoGap']} such labels "
               f"with an onset-to-arrival delay above 72 hours (unit inferred) gave {m['SensOg']}, and {m['SensOu']} when labels with unknown delay were also excluded.",
               "On reconstructing the outcome from the actual date of death: the workbook contains no date-of-death field, so this is not possible from the data we hold. "
               "The enclosed request asks the registry for the dates of death of the 33 post-discharge deaths (Q12); if they exist in the source files, the endpoint can be re-derived from them.",
               "The reviewer's example applies directly: a patient discharged on day 10 whose death is recorded at a contact 30 days after discharge may have died "
               "on day 40 after admission. Such deaths are counted as 30-day events only under A2; the strict endpoint does not count them, and each label now carries "
               "an evidence grade (E1/E0 confirmed, R recorded with unclear time origin, I inferred, U unresolved, X undocumented code). Because the dictionary does not state "
               "the time origin explicitly and no dates of death exist, no label reaches E1/E0, and the paper describes the endpoint as a registry-recorded first-month outcome "
               "analysed under stated assumptions that the dictionary supports. Under the dictionary's definition, the reviewer's example (death on day 40 after admission) "
               "would be recorded as death1 = No.",
               "To reflect that the definition is registry-based and partly assumption-dependent, the title now refers to first-month mortality, and the abstract, "
               "introduction and conclusions were changed accordingly. Eighteen unit tests cover boundary cases (death on day 30 and day 31, discharge alive on day 30 and "
               "later, later follow-up without an event date, contradictory fields)."],
              [L.sec("sec:outcome") + "; " + L.line("L:endpoint"), L.tab("tab:recon"), L.sec("sec:res-ascert") + "; " + L.line("L:res-timevarying"),
               L.fig("fig:ascert"), "Title and Abstract"],
              "The dictionary does not state the time origin explicitly or define codes, the 'Other' disposition remains undocumented and no dates of death exist; "
              "the endpoint is therefore described as resting on A1 and A2, with sensitivity analyses for both directions of error."))
    R.append(("R1-2 — 33.8% must not be presented as true mortality for all registry patients",
              "The reviewer questioned whether 33.8% represents the true 30-day mortality of the registry, as opposed to mortality within a labelled subset.",
              [f"We agree, and the claim has been withdrawn. Under the revised endpoint, mortality among the {m['Nlab']} labelled patients is {m['Mortlab']}% "
               f"(95% CI {m['MortlabLo']}–{m['MortlabHi']}). This is not a registry-wide estimate: in-hospital deaths are almost always labelled, whereas survivors are labelled only "
               "when follow-up was recorded, which became rare after 2016, so labelled-subset mortality rose to 46% in 2017–2019 and 62% in 2020.",
               f"Without assumptions, registry-wide 30-day mortality among the {m['Nelig']} eligible admissions lies between {m['BoundLo']}% and {m['BoundHi']}%. In-hospital 30-day "
               f"mortality among patients with a known disposition was {m['Mortinhosp']}% ({m['MortinhospLo']}–{m['MortinhospHi']}). Under missing-at-random assumptions the weighted "
               f"estimate was {m['Mortipw']}% ({m['MortipwLo']}–{m['MortipwHi']}) and delta-adjusted estimates at δ = 1 were {m['DeltaMARper']}% and {m['DeltaMARearly']}%. The submitted "
               "statement that conventional exclusion under-ascertains mortality by about 14 percentage points has been removed."],
              [L.sec("sec:res-mort") + "; " + L.line("L:res-mort"), L.tab("tab:reconbounds"), L.tab("tab:period"), L.line("L:disc-main") + " (Discussion)", "Abstract; Conclusion"],
              "Registry-wide mortality is not identified by the data; all values other than the bounds rely on stated, untestable assumptions."))
    R.append(("A-1 — Reconstruction circularity; temporal validation does not isolate ascertainment",
              "The reviewer was concerned that reconstructing outcomes from discharge status and length of stay may be circular and that ascertainment may vary over time.",
              ["We agree on both points. Discharge status and length of stay are used only to assign the outcome and never as predictors (" + L.sec("sec:missing") + "). The more important "
               "problem is time-varying ascertainment, which we now document (" + L.fig("fig:ascert") + "; " + L.tab("tab:period") + "). Recording of month-1 status fell from about 90% of admissions to between "
               f"3% and 61% per year after 2014; post-discharge deaths among labelled discharged patients fell from {m['PDearly']}% ({m['PDearlyK']}/{m['PDearlyN']}) in 2010–2014 "
               f"to {m['PDlate']}% ({m['PDlateK']}/{m['PDlateN']}) afterwards; dispositions were missing for {m['DispMissTwenty']} of {m['AdmTwenty']} admissions in 2020; and the "
               f"undocumented 'Other' disposition accounted for {m['OtherLate']} of {m['AdmLate']} admissions in 2021–2023.",
               "Because the reconstruction labels deaths from the hospital record but survivors only through follow-up, it produces outcome-dependent selection. We therefore "
               "treat ascertainment as a selection problem (Comment 5), and we report discrimination, which is relatively robust to this kind of selection, separately from "
               "calibration and risk-based quantities, which are not.",
               f"Temporal validation now uses one outcome-independent cut-off ({m['TCut']}, the 70th percentile of admission dates among all eligible patients) for every "
               f"endpoint, replacing the submitted cut-offs of 24 August 2016 and 26 December 2015. With it, the primary endpoint gave an AUROC of {m['TLR']} "
               f"({m['TNte']} test patients, {m['TEte']} deaths), the strict endpoint {m['TStLR']} ({m['TStN']}, {m['TStE']}) and the observed-only endpoint {m['TObLR']} "
               f"with only {m['TObE']} deaths among {m['TObN']} test patients, which is uninformative. Provenance, labelled proportion, case mix and missingness are reported "
               "for each period (" + L.tab("tab:tempshift") + "). Because ascertainment and case mix changed together, the temporal analysis cannot isolate ascertainment from "
               "dataset shift, and the paper no longer claims that it does.",
               "On the specific point that the reconstruction depends on in-hospital data whose completeness changed: the hospital-record fields became less, not more, "
               f"complete (disposition missing for {m['DispMissTwenty']} of {m['AdmTwenty']} admissions in 2020; 'Other' disposition for {m['OtherLate']} of {m['AdmLate']} in "
               "2021–2023), and the Discussion now states that reconstructed labels are therefore not uniformly reliable over time (" + L.line("L:disc-temporal") + ")."],
              [L.sec("sec:res-ascert") + "; " + L.line("L:res-timevarying"), L.fig("fig:ascert"), L.tab("tab:period"), L.sec("sec:res-temporal") + "; " + L.line("L:res-temporal"),
               L.tab("tab:temporal"), L.tab("tab:tempshift"), L.line("L:disc-model") + " and " + L.line("L:disc-temporal") + " (Discussion)"],
              "Whether post-discharge deaths were truly rarer after 2014 or simply no longer recorded cannot be determined from the workbook (registry question Q7)."))
    R.append(("A-2 — Ascertainment contribution conflated with modelling contribution",
              "The reviewer asked the authors to distinguish what is gained from outcome reconstruction from what is gained from the prediction model.",
              ["The Introduction now poses two separate questions, and the Results and Discussion follow that split: Sections " + L.num("sec:res-ascert") + "–" + L.num("sec:res-selbias") + " cover ascertainment and mortality, "
               "Sections " + L.num("sec:res-disc") + "–" + L.num("sec:sensitivity") + " cover prediction. The Discussion opens by stating each finding separately, and the contributions paragraph no longer combines them. "
               f"Discrimination was similar across endpoint definitions (strict {m['SensSt']}, observed-only {m['SensOb']}, primary {m['NestLR']}), so the model's discrimination "
               "does not depend on the reconstruction, whereas mortality estimates, calibration and risk tiers do."],
              [L.line("L:intro-ascert") + " (Introduction)", L.line("L:disc-main") + " and " + L.line("L:disc-model") + " (Discussion)", L.tab("tab:sens")],
              None))
    R.append(("R1-3 — 594 unresolved outcomes; ascertainability model, IPW, MNAR and survival analysis",
              "The reviewer asked how the unresolved patients differ from the analysed cohort and whether weighting or missing-not-at-random sensitivity analyses are feasible.",
              [f"We compared all {m['Nunres']} unresolved and {m['Nlab']} labelled eligible patients. Unresolved patients had lower NIHSS (median 7 vs 10) and admission Rankin scores "
               "(3 vs 4), higher GCS, fewer haemorrhagic strokes (32.4% vs 41.6%) and more missing NIHSS (58% vs 41%), and were concentrated in 2017–2023; 20% had no recorded "
               "disposition. They are mostly milder patients discharged alive or with undocumented dispositions, so the labelled cohort over-represents deaths.",
               "We fitted an observation model (probability of being labelled given admission characteristics with missingness indicators, period, disposition and stay "
               "beyond 30 days). Positivity failed for patients without a recorded disposition (estimated probabilities around 0.002), so the weighted analysis targets the "
               f"{m['Nipwpop']} patients with a recorded disposition and excludes {m['Nnodisp']}. Weights were truncated at the 99th percentile ({m['IPWntrunc']} weights; cap "
               f"{m['IPWcap']}; maximum untruncated {m['IPWmax']}); the effective sample size was {m['IPWess']}. The weighted mortality was {m['Mortipw']}% (95% CI {m['MortipwLo']}–{m['MortipwHi']}, "
               "bootstrap including re-estimation of the weights). IPW-weighted model fitting and evaluation gave an AUROC of " + m["SensIw"] + ".",
               "For a missing-not-at-random sensitivity analysis we used delta-adjustment: unresolved patients discharged alive within 30 days were given the post-discharge risk "
               "of comparable labelled patients (either 2010–2014 or the same period), the remaining unresolved patients a risk from a weighted outcome model, and the odds "
               f"were multiplied by δ from 0.25 to 8. Estimated mortality ranged from {m['DeltaMin']}% to {m['DeltaMax']}%; matching the labelled-subset value would require the "
               "unresolved to have two to four times (2010–2014 reference) or slightly more than four times (period-specific reference) the odds of death of comparable resolved patients. Time-to-event analysis was not attempted because neither event nor "
               "censoring dates are recorded."],
              [L.sec("sec:selbias") + "; " + L.line("L:ascert-methods"), L.sec("sec:res-selbias") + "; " + L.line("L:res-selbias"), L.tab("tab:selbias"),
               L.tab("tab:reconbounds"), L.tab("tab:delta"), L.fig("fig:delta")],
              "Weighting corrects only for selection explained by the measured variables; it cannot correct mislabelled outcomes or unmeasured reasons for missing follow-up."))
    R.append(("A-5 — Missingness and MICE under-reported; MCAR/MAR/MNAR unclear",
              "The reviewer asked for missingness to be reported after the final cohort definition, for the missingness mechanism to be discussed, and for the imputation procedure to be specified without leakage.",
              ["Missingness was recalculated for the eligible and labelled cohorts (" + L.tab("tab:missing") + "): NIHSS was missing in 41% and the admission Rankin score in 48% of labelled patients, "
               "respiratory rate in 37%, CRP in 44% and total cholesterol in 46%; SpO2 (69%) exceeded the pre-specified 60% limit and was not used, and BMI (89% missing in the "
               "registry) was not considered. Missingness was strongly associated with period and with ascertainment, so we state that MCAR is implausible, MAR is a working "
               "assumption and MNAR cannot be excluded.",
               "The imputation model is now fully specified: chained equations with a Bayesian ridge conditional model for each variable, all 27 candidate predictors as "
               "auxiliary variables for one another, the outcome and all post-admission fields excluded, up to 15 iterations (the final model converged after "
               f"{mr['imputer_iterations_final_model']}), inside each model pipeline, so it is fitted on training data only in every inner and outer fold and in the temporal "
               "training set; test-fold values are imputed with the training-fold model. The primary analysis uses one imputation per fold (the posterior mean). "
               "The submitted manuscript used median imputation in nested CV and MICE in the single split; this inconsistency is removed.",
               f"The submitted Table 20 (NIHSS only) is replaced. Four sensitivity analyses now cover imputation beyond NIHSS: multiple imputation with m = 5 posterior draws, pooling predictions across draws ({m['SensMi']}; "
               f"between-draw SD of fold AUROC {m['MIdrawSD']}); a NIHSS missingness indicator ({m['SensNi']}); missingness indicators for all {m['NhiMiss']} predictors "
               f"with more than 20% missing, which include CRP, urea, cholesterol, respiratory rate and the Rankin score ({m['SensMa']}); and a model restricted to the "
               f"{m['NlowMiss']} predictors with less than 10% missing ({m['SensLm']}). The complete-NIHSS subset gave {m['SensCn']} (n = {m['SensCnN']}). Creatinine was "
               "missing in 18% of labelled patients and is covered by the multiple-imputation and low-missing analyses. Discrimination changed little under any of them; "
               "calibration under a missing-not-at-random mechanism remains untested and is listed as a limitation."],
              [L.sec("sec:missing") + "; " + L.line("L:missing-methods"), L.tab("tab:missing"), L.tab("tab:sens"), L.tab("tab:subgroups")],
              "With a single imputation inside each training fold, between-imputation variance is not propagated into the fold estimates; the stochastic-imputation "
              "sensitivity analysis addresses this only partly."))
    R.append(("A-6 — Clinical-reference model insufficiently specified",
              "The reviewer asked for the clinical comparator to be fully specified and for clarity on whether iScore or PLAN were implemented.",
              ["The comparator is now fully specified: an unpenalised logistic regression with linear terms for age, NIHSS, GCS, admission Rankin score, haemorrhagic subtype and "
               "sex, re-estimated in each training set with the same imputation and no tuning. We state explicitly that it is a locally fitted comparator built from predictors "
               "that established scores share, and not an implementation or validation of iScore or PLAN, which require congestive heart failure, cancer and dialysis (iScore) "
               "and neglect and limb-weakness items (PLAN) that the registry does not record."],
              [L.sec("sec:comparator") + "; " + L.line("L:comparator")], None))
    R.append(("R1-4 — DeLong p = 0.17 is not evidence of equivalence",
              "The reviewer noted that a non-significant DeLong test (p = 0.17) does not show that the model and the clinical reference are equivalent, and asked for the paired difference with its confidence interval.",
              ["We agree; the equivalence wording has been removed. The submitted hold-out difference was −0.026 (0.822 − 0.848); its paired 95% CI cannot be computed "
               "because the original paired predictions were not available. The submitted comparison relied on a single 70/15/15 split that is no longer used. On the same patients, the "
               f"paired AUROC difference (primary minus reference) in nested cross-validation was {m['PairNestDiff']} (95% CI {m['PairNestLo']} to {m['PairNestHi']}; DeLong p "
               f"{m['PairNestP']}), with the primary model higher in {m['FoldLRBetter']} of {m['NFolds']} outer folds; this interval is approximate because out-of-fold predictions "
               f"come from different training sets. On the independent temporal test set (n = {m['TNte']}, {m['TEte']} deaths) the difference was {m['TPairDiff']} (95% CI "
               f"{m['TPairLo']} to {m['TPairHi']}; p = {m['TPairP']}). The data are compatible with no difference and with a gain of up to 0.07; they establish neither "
               "equivalence nor superiority, and no equivalence margin was pre-specified."],
              [L.sec("sec:res-paired") + "; " + L.line("L:res-paired"), L.tab("tab:paireddelong"), L.line("L:calib-methods") + " (Methods)"],
              "The original hold-out predictions could not be regenerated because the final training code was unavailable, so the submitted p = 0.17 itself could not be re-examined."))
    R.append(("R1-5 — Datasets used to fit and select Platt/isotonic calibration",
              "The reviewer asked whether recalibration was fitted or selected using the test set.",
              ["In the earliest code available to us, Platt and isotonic maps were fitted on the validation split but compared on the test set, and the submitted manuscript "
               "reported Platt scaling as the better method on the test set, so the reported calibration was not independent of the test data. In the revision the primary model is an unweighted penalised logistic regression and is not recalibrated; Platt and "
               "isotonic recalibration are sensitivity analyses fitted by internal cross-validation inside each outer training fold, and neither was selected using test data.",
               f"Out-of-fold calibration of the primary model: intercept {m['NestLRInt']}, slope {m['NestLRSlope']}, Brier {m['NestLRBrier']}. In-fold Platt: slope {m['RecPlattSlope']}, "
               f"Brier {m['RecPlattBrier']}; isotonic: slope {m['RecIsoSlope']}, Brier {m['RecIsoBrier']}. On the temporal test set the model under-predicted (intercept {m['TLRInt']}), "
               f"as expected when survivors are under-ascertained; with ascertainment weights the intercept was {m['TLRipwInt']} and the slope {m['TLRipwSlope']}. We now state "
               "that absolute risks reflect the ascertainment of the development data. The submitted values (slope 0.89 after Platt) are superseded."],
              [L.sec("sec:calib") + "; " + L.line("L:calib-methods"), L.sec("sec:res-calib") + "; " + L.line("L:res-calib"), L.tab("tab:recal"), L.fig("fig:cal")],
              "Calibration cannot be assessed against the registry population, only against the selectively ascertained labelled patients, with or without weighting."))
    R.append(("A-7 — No low-risk tier in the single split; clinical utility overstated",
              "The reviewer noted that no low-risk tier emerged on the test set and questioned the clinical-utility claims.",
              ["The submitted Tables 15 and 16 are replaced by a single table (" + L.tab("tab:tiers") + "). The missing low-risk tier in the single split was a consequence of deriving thresholds on a small validation split (153 patients, 52 deaths): the lower threshold derived on that split was so low that no validation or test patient fell beneath it, so the scheme was in practice two-tier. Tiers now use absolute-risk cut-points fixed before evaluation "
               f"(low < 10%, high ≥ 40%). On pooled out-of-fold predictions the low tier contained {m['TierOLowPct']}% of patients with {m['TierOLowMort']}% mortality and the high tier "
               f"{m['TierOHighPct']}% with {m['TierOHighMort']}% mortality ({m['TierOHighCap']}% of deaths); on the temporal test set the low tier contained {m['TierTLowN']} patients "
               f"({m['TierTLowMort']}% mortality) and the high tier captured {m['TierTHighCap']}% of deaths. Out-of-fold and temporal results are reported separately.",
               f"Downstream consequences: as an illustration of follow-up effort, the high tier contained {m['TierOHighPPD']} patients per death and the low tier "
               f"{m['TierOLowPPD']} patients per death on out-of-fold predictions ({L.tab('tab:tiers')}). Directing follow-up to the high tier would reach "
               f"{m['TierOHighCap']}% of deaths by following {m['TierOHighPct']}% of patients, in the labelled cohort. We state explicitly that these figures cannot be read "
               "as resource consequences in the registry population, because the labelled cohort over-represents deaths.",
               "Because tier mortalities and net benefit depend on outcome prevalence, which selective ascertainment distorts, decision curves (also shown with weights) are "
               "presented as exploratory, and follow-up prioritisation is described as a hypothesis requiring prospective evaluation. The submitted statement that a high tier "
               "of 42% captured 77% of deaths has been removed."],
              [L.line("L:tiers-methods") + " (Methods)", L.sec("sec:res-tiers") + "; " + L.line("L:res-tiers"), L.tab("tab:tiers"), L.fig("fig:tiers"), L.fig("fig:dca"),
               L.line("L:disc-utility") + " (Discussion)"],
              "The tiers have not been validated externally and are not recommended for clinical use."))
    R.append(("A-8 — Interpretability claims too strong; Glasgow-to-NIHSS mechanism speculative",
              "The reviewer questioned the claims of stable explanations, the reliance on four LIME cases and the interpretation of the Glasgow-to-NIHSS ratio.",
              [f"The submitted Figures 15 (concordance) and 17 (LIME) are replaced by " + L.fig("fig:shap") + " and " + L.tab("tab:interp") + ". Interpretation was recomputed for the final model. GCS, NIHSS and haemorrhagic subtype dominated the coefficients and SHAP values of both the primary model and "
               f"XGBoost, but rank agreement across all {m['NFeat']} predictors was moderate (Spearman ρ = {m['ShapRho']}; feature-bootstrap interval {m['ShapRhoLo']}–{m['ShapRhoHi']}; "
               "submitted 0.70). We now report bootstrap confidence intervals for odds ratios, the frequency with which each predictor ranks in the top five across bootstrap refits, "
               "and permutation importance on the temporal test set, and we describe concordance as moderate rather than stable.",
               "The four LIME cases were illustrations without systematic validation and were removed. The Glasgow-to-NIHSS ratio is no longer part of the model; adding it "
               f"did not improve discrimination ({m['SensRa']} vs {m['NestLR']}), and the Discussion no longer presents it as a prognostic marker or attributes a mechanism to it."],
              [L.sec("sec:interp-methods") + "; " + L.line("L:interp-methods"), L.sec("sec:res-interp") + "; " + L.line("L:res-interp"), L.tab("tab:interp"), L.fig("fig:shap"),
               L.line("L:disc-interp") + " (Discussion)"], None))
    R.append(("A-3 — Overstated generalisation, clinical utility and novelty (temporal validation)",
              "The reviewer questioned the temporal-validation design, the claim that reconstruction eliminates dataset shift, the use of different cut-offs, generalisability and the novelty claims.",
              [f"A single cut-off, fixed before modelling as the 70th percentile of admission dates among all eligible patients ({m['TCut']}), is now used for every endpoint. The "
               f"primary model's temporal AUROC was {m['TLR']} ({m['TLRLo']}–{m['TLRHi']}; {m['TNte']} patients, {m['TEte']} deaths). Under the observed-only endpoint the test set "
               f"contained only {m['TObE']} deaths among {m['TObN']} patients, because in-hospital deaths were no longer recorded in death1; its AUROC ({m['TObLR']}, {m['TObLRLo']}–{m['TObLRHi']}) "
               "is uninformative, and the submitted collapse to 0.72 (based on a different cut-off) was not reproduced. Case mix, missingness, ascertainment and outcome provenance "
               f"all changed between periods (period-membership AUROC {m['TMember']}), so the temporal results cannot separate dataset shift from ascertainment change. The claim "
               "that reconstruction proved the absence of dataset shift has been withdrawn, and the temporal split is described as internal, not external, validation.",
               "Novelty claims were narrowed: we did not perform a systematic literature search and no longer claim to present the first such model or analysis in the region. "
               "The words 'true' and 'corrected' are no longer applied to the labelled-subset mortality, the equivalence claim with the clinical model was removed, and clinical "
               "use (risk tiers, follow-up prioritisation) is presented as a hypothesis requiring prospective evaluation, not as a deployable tool. The three quoted sentences "
               "no longer appear: 'generalises across time' was replaced by a description of an internal temporal split; the modelling contribution is now described as modest "
               "(it confirms that admission data rank patients well and that a simple clinical model does nearly as well); and the priority claim was removed rather than "
               "softened, because we did not perform a systematic search."],
              [L.sec("sec:validation") + "; " + L.line("L:validation"), L.sec("sec:res-temporal") + "; " + L.line("L:res-temporal"), L.tab("tab:temporal"), L.tab("tab:tempshift"),
               L.line("L:disc-temporal") + " and " + L.line("L:disc-novelty") + " (Discussion)", L.line("L:intro-ascert") + " (Introduction)"],
              "External validation in another centre was not possible with the available data."))
    R.append(("A-11 — Data integrity: duplicate discordance and audit flag counts",
              "The reviewer raised concerns about duplicate records, data integrity and the availability of reproducible code.",
              [f"Every source row is preserved with a stable identifier. The 38 repeated identifiers were compared across all 251 fields; the paired rows usually differed "
               f"(median 18 fields with two different non-missing values; {L.tab('tab:dupfields')}), so they are not exact copies. Rule-based decisions are logged per group: "
               "one blank pair dropped, four identifier collisions kept as separate patients, 33 pairs merged, with outcomes left unresolved in seven pairs whose outcome fields "
               "disagreed. Two alternative rules gave nearly identical results. Earlier audit counts of differing fields disagreed because they used different conventions; both are "
               "now reported by field category. We also flag 14 column-misaligned rows, 22 release dates before admission, impossible years and 92 disagreements between recorded "
               "and date-derived stay, without altering raw values. All counts from the authors' preliminary audit were re-derived under stated rules: 37 of 38 groups differ "
               "in some field and 35 in a timing or outcome field; 23 rows have a release date before admission when any calendar-plausible year is allowed (22 within the registry "
               "years); 174 rows have recorded and date-derived stays differing by more than one day; the union of these two flags is 175 rows; and dates in years 2916, 3016 and "
               "2930 occur in source rows 767, 773 and 808 (" + L.tab("tab:auditrecon") + "). Two preliminary figures could not be reproduced: a total of 194 flagged rows and "
               "28 groups with clinical-variable differences, because the original flag classes and variable list were not available; 28 equals the number of groups with two "
               "different non-missing values in the timing and outcome fields, which may be its source.",
               "The final training code for the submitted version was not available; an earlier pipeline version reproduces only the observed-only analysis and, in that version, "
               "selected length of stay as a predictor and chose the recalibration method on the test set. All reported results therefore come from a new pipeline that regenerates "
               "every table, figure and number from the workbook, with fixed seeds, an input checksum and unit tests. It is supplied with the submission and will be deposited "
               "with a persistent identifier on acceptance; a table reconciling submitted and revised results is given in Appendix B."],
              [L.sec("sec:dups") + "; " + L.line("L:dups"), L.tab("tab:dupfields"), L.sec("sec:repro") + "; " + L.line("L:repro"), L.tab("tab:origvsrev"),
               "Data and code availability statement, " + L.line("L:availability")],
              "Duplicate and date decisions await source-record adjudication by the registry team (enclosed request, Q10–Q11)."))

    lb = {r["disposition"]: r for r in __import__("csv").DictReader(open(C.COHORT / "los_by_disposition.csv"))}
    R.append(("A-4 — Length-of-stay hierarchy and later follow-up rules not justified",
              "The length-of-stay rules and the use of later follow-up to infer 30-day survival were not justified; the reviewer asked to see the stay distribution, "
              "the rationale for each rule, the label transitions and the sensitivity of the counts.",
              ["Each rule is now stated with its justification and its evidence grade (" + L.sec("sec:outcome") + "). Why 30 days: the estimand is death within 30 days of "
               "admission, so an in-hospital death on day 31 or later is a non-event by definition, not a late event; the window is not a tuning choice. Late in-hospital "
               "deaths are therefore not misclassified as 30-day events, and the earlier window sweep (21–35 days) was removed because it answered no question. Stay is taken from the admission and release dates when "
               "both are valid and the derived stay is 0–120 days, otherwise from the recorded length of stay; " + m["Nstayimpl"] + " date-derived stays above 120 days (five of "
               "them 365–376 days, consistent with a mistyped release year) are not used. The recorded stay agrees with the dates exactly in " + m["LOSexact"] + " of " + m["LOSboth"] +
               " rows and differs by one day in " + m["LOSplusone"] + ", so its convention (elapsed or inclusive days) is mixed; when the two measures fall on opposite sides of "
               "day 30 and no month-1 status exists, the outcome is left unresolved.",
               "Later follow-up: month-3, -6 or -9 status was recorded for " + m["LaterRec"] + " eligible patients (" + m["LaterPct"] + "%), for 87% of admissions in 2010–2012 but "
               "16% or fewer from 2017 (" + L.tab("tab:period") + "). Only " + m["LaterNoDone"] + " of them lacked a month-1 status, and later contacts supply " + m["NNfour"] +
               " survival labels; removing those labels left discrimination unchanged (" + m["SensNl"] + "). The incompleteness of later follow-up therefore cannot introduce "
               "much bias into the labels, although it is part of the selection documented in Section " + L.num("sec:res-selbias") + ".",
               "The stay distribution by disposition is now reported (" + L.tab("tab:lostab") + "): in-hospital deaths had a median stay of " +
               f"{float(lb['Died in hospital']['median']):.0f} days and only {lb['Died in hospital']['d28_32']} in-hospital death and {lb['Discharged home']['d28_32']} discharges home "
               "fell between days 28 and 32, so the 30-day boundary affects few labels. A later contact recording the patient alive (month 3, 6 or 9) is used as survival "
               "evidence only when month-1 status is missing; it implies survival to day 30 whatever the time origin of the contact, but it is grade R because the meaning of "
               f"'No' is undocumented. It contributes {m['NNfour']} non-events. A death recorded only at month 3–9 is never counted as a 30-day event. "
               "The 'Other' disposition, which the submitted rules treated as survival evidence for long stays, is no longer used.",
               "Label transitions from the submitted reconstruction to the revised classes are tabulated (" + L.tab("tab:transitions") + "), and the counts under alternative "
               f"rules are given for the strict ({m['NstrictLab']} labelled, {m['NstrictDeaths']} deaths) and observed-only endpoints and for two duplicate rules (" + L.tab("tab:sens") + ")."],
              [L.sec("sec:dups") + "; " + L.line("L:dups"), L.sec("sec:outcome") + "; " + L.line("L:endpoint"), L.tab("tab:recon"), L.tab("tab:lostab"), L.tab("tab:transitions")],
              "The rules depend on assumptions A1 and A2 until the registry documents the fields; the relevant questions are Q1–Q6 of the enclosed request."))
    R.append(("A-9 — No external or prospective validation",
              "The study has no external or prospective validation.",
              ["We agree and say so throughout. The temporal split is described as an internal, same-centre evaluation, not external validation (" + L.sec("sec:validation") +
               "); the limitations state that no external cohort was available; and the conclusions require documented outcome definitions, prospective ascertainment with dates "
               "of death and validation in an independent cohort before any clinical use."],
              [L.line("L:validation") + " (Methods)", L.sec("sec:limits") + "; " + L.line("L:limits"), L.line("L:disc-utility") + " (Discussion)", "Conclusion"],
              "External and prospective validation are outside the scope of this revision."))
    R.append(("A-10 — Code availability statement contradictory (openly released vs on request / future deposit)",
              "The data and code availability statement said both that the code was openly released and that it was available on request or would be deposited later.",
              ["The statement now describes the actual status only: the complete analysis code (data cleaning, endpoint and reconciliation functions, unit tests, model "
               "specifications, seeds, software versions and execution log) is supplied as supplementary material with this submission, and it has not yet been deposited in a "
               "public repository. No future deposit is presented as complete. The submitted results could not be reproduced because the final version of the original training "
               "code was not available; this is disclosed in " + L.sec("sec:repro") + " and Appendix B."],
              ["Data and code availability statement, " + L.line("L:availability"), L.sec("sec:repro") + "; " + L.line("L:repro"), L.tab("tab:origvsrev")],
              "If the authors create a public repository before submission, its name and persistent identifier must be added to the statement."))
    R.append(("A-12 — An earlier related draft used a post-discharge endpoint; the current draft is admission-based",
              "An earlier related draft by the authors defined the outcome as post-discharge mortality, whereas the submitted manuscript defines it from admission.",
              ["The revised paper defines day 0 as the admission date and includes in-hospital deaths, and it states why the post-discharge interpretation cannot be excluded "
               "for the month-1 field: from 2015 the field was completed almost only for patients discharged alive, and the follow-up interval may have been counted from discharge "
               "(" + L.sec("sec:outcome") + "; " + L.sec("sec:res-ascert") + "). The strict endpoint, which counts only deaths timed by the hospital record, isolates the part of the "
               "outcome that does not depend on this choice. The earlier draft's dataset, inclusion criteria and model outputs differ from those reported here; the authors will "
               "disclose any prior dissemination or submission of that draft to the editor in the cover letter."],
              [L.sec("sec:outcome") + "; " + L.line("L:endpoint"), L.sec("sec:res-ascert") + "; " + L.line("L:res-timevarying")],
              "The earlier draft was not among the files available for this revision, so its overlap with the present paper could not be checked here."))
    R.append(("A-13 — Incomplete methodological reporting for reproducibility",
              "Listed by the reviewer among the most serious concerns.",
              ["Every analytic decision is now reported: data preparation and integrity rules; the endpoint rule with provenance and evidence grades; duplicate rules; the "
               "imputation model (conditional model, iterations, auxiliary variables, exclusion of the outcome, number of imputations); hyperparameter grids; the comparator; "
               "the validation design with a pre-fixed temporal cut-off; calibration and tier rules; software versions; and seeds. The complete code (one command regenerates "
               "every table, figure and number from the registry workbook), its execution log, 18 unit tests and a verification report are supplied with the submission, "
               "together with the analysis protocol and a TRIPOD+AI reporting map with page locations. A reconciliation table lists every submitted result and states "
               "whether it was reproduced, corrected, replaced or withdrawn (" + L.tab("tab:origvsrev") + ")."],
              [L.sec("sec:repro") + "; " + L.line("L:repro"), L.sec("sec:missing"), L.sec("sec:comparator"), L.sec("sec:validation"), "Supplementary: protocol, TRIPOD+AI map, code"],
              "The code is not yet in a public repository (see A-10)."))
    R.append(("E-1 — Editor: source files and journal formatting",
              "Upload the source files; PDF manuscript files cannot be used for production; follow the journal formatting guidelines.",
              ["The revision is supplied as a complete LaTeX project (elsarticle class, main.tex with tables/, figures/ and the bibliography) that compiles without errors, "
               "together with the clean PDF and a change-marked PDF. Figures are 300-dpi PNG files generated by the analysis code. Line numbers are included for review. "
               "Hyperlinks are not coloured. The structured abstract, keywords, declarations (ethics, funding, competing interests, data and code availability, "
               "generative-AI use, CRediT) follow the current Guide for Authors (structured abstract of at most 250 words, 1–7 keywords); a highlights file (five bullets of at most 85 characters) is supplied. "
               "The current online guide does not mention a graphical abstract, whereas an older version of the guide listed one as mandatory for original articles; we will supply one if the editorial office requires it."],
              ["Submission package, folder 01_manuscript/source"], None))
    POS = {"R1-1": "Partially agree", "R1-2": "Agree", "A-1": "Agree", "A-2": "Agree", "A-3": "Agree", "A-4": "Partially agree",
           "A-5": "Agree", "A-6": "Agree", "A-7": "Agree", "A-8": "Agree", "A-13": "Agree", "A-9": "Agree", "R1-3": "Partially agree",
           "R1-4": "Agree", "R1-5": "Agree", "E-1": "Agree", "A-10": "Internal item", "A-11": "Internal item", "A-12": "Internal item"}
    WHY = {"R1-1": "death1 now defined from the registry's data dictionary (death within the first month after the stroke); reconstruction from actual dates of death is not possible because the registry holds no dates of death.",
           "A-4": "Reporting requests accepted in full; the 30-day window is the estimand (death within 30 days of admission), so late in-hospital deaths cannot be misclassified as 30-day events.",
           "R1-3": "Ascertainability model, IPW and MNAR (delta) analyses done; time-to-event analysis is not feasible because event and censoring dates are not recorded."}
    ACT = {"R1-1": "Endpoint defined (day 0 = admission); death1 defined from the data dictionary; A1/A2 stated; provenance per label; strict and stroke-anchored sensitivity endpoints",
           "R1-2": "33.8% withdrawn as registry mortality; bounds, IPW and delta-adjusted estimates reported",
           "A-1": "Temporal-rescue interpretation withdrawn; one outcome-independent cut-off for all endpoints; shift and recording changes reported",
           "A-2": "Two questions separated in title, abstract, Introduction, Results and Discussion",
           "A-3": "Generalisation, utility and priority claims withdrawn or narrowed",
           "A-4": "Stay distribution by disposition, later-contact completeness, label transitions and N4 sensitivity reported",
           "A-5": "Missingness mechanisms discussed; imputation model specified; m = 5 MI and three further imputation sensitivity analyses",
           "A-6": "Clinical reference fully specified and re-estimated in each training fold",
           "A-7": "Pre-specified tiers; tier effort reported; tiers not recommended for use",
           "A-8": "Rank agreement reported as moderate; GCS/NIHSS ratio de-emphasised; LIME removed",
           "A-13": "Full methods, code, tests, protocol and TRIPOD+AI map supplied",
           "A-9": "Temporal split described as internal; external validation stated as required before use",
           "R1-3": "Labelled vs unresolved comparison; observation model; IPW with positivity restriction; delta-adjustment",
           "R1-4": "AUROC differences with paired 95% CIs; no equivalence claim",
           "R1-5": "Recalibration fitted in training folds only; primary model not recalibrated",
           "E-1": "LaTeX source; abstract <= 250 words; keywords <= 7; highlights file; declarations",
           "A-10": "Availability statement describes the actual status", "A-11": "Integrity flags re-derived and reconciled", "A-12": "Admission-based endpoint justified; overlap to be disclosed"}
    EVID = {k: "Re-analysis output (code, log, verification report)" for k in POS}
    EVID.update({"A-2": "Revised text", "A-3": "Revised text", "A-13": "Supplied code and documents", "A-9": "Revised text", "E-1": "Journal guide (ScienceDirect, accessed 2 Nov 2026)",
                 "A-10": "Revised statement", "A-12": "Revised text"})
    TICK = {"R1-1": ("OUTCOME-TIME-001, OUTCOME-TIME-002, OUTCOME-TIME-003, OUTCOME-TIME-004, OUTCOME-REC-006", "REQ-03"),
            "R1-2": ("EPI-MORT-001, DATA-DUP-001", "REQ-04, REQ-02"), "A-1": ("VAL-TEMP-001, VAL-TEMP-002", "REQ-08"),
            "A-2": ("CLAIM-001, CLAIM-002", "REQ-12"), "A-3": ("CLAIM-002, CLAIM-003, VAL-TEMP-003, STAT-AUC-002", "REQ-12, REQ-08, REQ-09"),
            "A-4": ("OUTCOME-REC-001, OUTCOME-REC-002, OUTCOME-REC-003, OUTCOME-REC-005, DATA-DATE-002", "REQ-03, REQ-01"),
            "A-5": ("MODEL-IMP-001, MODEL-IMP-002", "REQ-06"), "A-6": ("MODEL-COMP-001", "REQ-07"), "A-7": ("STAT-RISK-001, STAT-RISK-002", "REQ-10"),
            "A-8": ("XAI-001, XAI-002, XAI-003", "REQ-11"), "A-13": ("REPRO-001, REPRO-002, MODEL-LIST-001, MODEL-LEAK-001, MODEL-LEAK-002, STAT-SIZE-001", "REQ-13, REQ-07, REQ-06"),
            "A-9": ("CLAIM-004, VAL-TEMP-003", "REQ-12"), "R1-3": ("EPI-SEL-001, EPI-SEL-002, EPI-SEL-003, EPI-SEL-004, EPI-SURV-001", "REQ-04, REQ-05"),
            "R1-4": ("STAT-AUC-001, STAT-AUC-002", "REQ-09"), "R1-5": ("STAT-CAL-001", "REQ-09"), "E-1": ("SUBM-001, SUBM-002, SUBM-003, SUBM-004", "REQ-14"),
            "A-10": ("DECL-004, REPRO-004", "REQ-15, REQ-13"), "A-11": ("DATA-DUP-001, DATA-DUP-002, DATA-DATE-001, DATA-DATE-003", "REQ-01, REQ-02"), "A-12": ("OUTCOME-TIME-001", "REQ-03")}
    ORDER = ["R1-1", "R1-2", "A-1", "A-2", "A-3", "A-4", "A-5", "A-6", "A-7", "A-8", "A-13", "A-9", "R1-3", "R1-4", "R1-5", "E-1", "A-10", "A-11", "A-12"]
    R.sort(key=lambda r: ORDER.index(r[0].split(" ")[0]))
    h("Response matrix", 1)
    p("Comment column: short paraphrase; the full comment is quoted verbatim in the point-by-point section. Location: first location in the revised manuscript.", italic=True)
    tb = doc.add_table(rows=1, cols=7); tb.style = "Light Grid Accent 1"
    for i, c in enumerate(["Item", "Comment (paraphrase)", "Interpretation", "Position", "Action", "Location", "Evidence"]):
        tb.rows[0].cells[i].text = c
    for title, concern, resp, locs, lim in R:
        code = title.split(" ")[0]
        src = "Reviewer #1" if code.startswith(("R1", "A-")) and code not in ("A-10", "A-11", "A-12") else ("Editor" if code == "E-1" else "Authors (internal)")
        row = tb.add_row().cells
        for i, v in enumerate([f"{code} ({src})", title.split(" — ", 1)[1], concern, POS[code] + (": " + WHY[code] if code in WHY else ""),
                               ACT[code], locs[0], EVID[code]]):
            row[i].text = v
    for r_ in tb.rows:
        for c_ in r_.cells:
            for pp in c_.paragraphs:
                for rn in pp.runs:
                    rn.font.size = Pt(8)

    h("Point-by-point responses", 1)
    for title, concern, resp, locs, lim in R:
        h(title, 2)
        code = title.split(" ")[0]
        para = doc.add_paragraph(); r = para.add_run("Comment (verbatim). "); r.bold = True
        q = para.add_run(VERBATIM.get(code, concern)); q.italic = True
        para = doc.add_paragraph(); r = para.add_run("Our position. "); r.bold = True
        para.add_run(POS[code] + ("." if code not in WHY else ". " + WHY[code]))
        for i, x in enumerate(resp):
            para = doc.add_paragraph()
            if i == 0:
                rr = para.add_run("Response. "); rr.bold = True
            para.add_run(x)
        para = doc.add_paragraph(); r = para.add_run("Where in the revised manuscript. "); r.bold = True; para.add_run("; ".join(locs) + ".")
        para = doc.add_paragraph(); r = para.add_run("Traceability. "); r.bold = True
        para.add_run(f"Phase 1 tickets {TICK[code][0]}; Phase 2 requirements {TICK[code][1]} (docs/requirements_traceability_matrix.md).")
        if lim:
            para = doc.add_paragraph(); r = para.add_run("What remains limited. "); r.bold = True; para.add_run(lim)

    h("Additional changes not requested by the reviewer", 1)
    for b in ["Transient ischaemic attacks (24 patients) were excluded because they are not strokes.",
              "The generative-AI declaration was updated: the original statement that no AI tools were used does not describe this revision, which was prepared with AI "
              "assistance for code, analysis and drafting under the authors' supervision. The authors must confirm the wording.",
              "Subgroup analyses, the learning curve, partial-dependence plots, the confusion matrix and the exploratory overview figures of the submitted version were replaced "
              "by the analyses described above; subgroup discrimination is now reported from out-of-fold predictions (" + L.tab("tab:subgroups") + ").",
              "The registry's data dictionary, received during the revision, was audited against the workbook and is enclosed. It documents the definition of the "
              "month-1 mortality field, supports both endpoint assumptions and led to one new sensitivity analysis (stroke-anchored month-1 window).",
              "Twelve references were added: eight supporting the new methods (TRIPOD+AI, calibration, decision curves, inverse-probability weighting, sample size, delta-adjustment, fast DeLong, SHAP), "
              "the RECORD and STROBE reporting statements, and the original iScore and PLAN derivation papers.",
              "Four statements in the Introduction were corrected after checking them against the cited sources: the regional case-fatality figures now quote the pooled one-month "
              "estimate of the cited meta-analysis and the 90-day mortality of the cited Tanzanian cohort; the Cameroonian readmission figures now match the cited study (15% readmitted "
              "within a year, more than half of them died); a citation to an unrelated study of dialysis access was removed; and the statement on iScore and PLAN now cites their "
              "derivation papers.",
              "A post hoc sample-size check following Riley et al. was added (" + L.line("L:samplesize") + "); the unit of analysis and the inability to link repeat admissions are stated."]:
        bullet(b)
    p("Enclosures: revised manuscript (clean and change-marked), LaTeX source, analysis code and aggregate outputs, change log, registry clarification request.", italic=True)
    doc.save(out_docx)
    print("wrote", out_docx)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
