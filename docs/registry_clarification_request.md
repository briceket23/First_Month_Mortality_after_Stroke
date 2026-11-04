---
title: "Registry clarification request — NEURI-D-26-00184"
subtitle: "Outcome definitions, follow-up coding and duplicate records in the Douala General Hospital stroke registry"
date: "16 October 2026 (status updated 2 November 2026)"
---

**To:** Registry custodian / Neurology Unit data team, Douala General Hospital (to be addressed by the corresponding author)
**From:** C.B. Fomazou Tchinda, on behalf of the authors of NEURI-D-26-00184
**Reply needed by:** 30 October 2026 (revision due 6 November 2026)

## Update of 2 November 2026 — after receipt of the data dictionary

The registry's data dictionary (256 variables) was received on 2 November 2026 and audited against the workbook (`dictionary_audit.json`, `clarification_questions_vs_dictionary.csv`). It defines `death1` (décès1) as "Death at Month 1, recording if the patient passed away within the first month" and describes the follow-up assessments as made one to twelve months "after the stroke". This partly answers Q1, Q2, Q4 and Q6, and the revision now uses these definitions. The dictionary gives no value codes, no explicit time origin and no date of death. **The questions below remain useful but no longer block the resubmission.** In order of value: Q12 (dates of death), Q3 (meaning of `death1 = No`), Q2 (explicit time origin and follow-up procedure), Q5 ("Other" disposition), Q6 (codes 0/3/9/99), Q9 (admission Rankin timing), Q7, Q8, Q10, Q11.

## Why we are asking

The reviewers of our manuscript asked what the month-1 mortality field means and from which date it is counted. The workbook we analysed (`database_stroke_copy.xlsx`, 1,653 rows, MD5 `08541ef199c1656c184291f24b4cc3e3`) does not contain a date of death, and when this request was first written (16 October) we had neither a data dictionary nor a follow-up form; the dictionary has since been received (see the update above). The data themselves suggest that the recording procedure changed during 2010–2023. We cannot state the endpoint definition in the paper until you confirm it. Short written answers (one line per question is enough) and copies of any forms are what we need.

## Evidence from the workbook that prompted each question

| Observation (aggregate counts) | 2010–2012 | 2015–2023 |
|---|---|---|
| In-hospital deaths (disposition "death") also recorded as `death1 = Yes` | 80 of 83 | 3 of 172 |
| Admissions with `death1` recorded (Yes or No) | about 90% | 3–61% by year |
| Patients discharged home with `death1 = Yes` (post-discharge death) | 8 of 198 with `death1` recorded | 5 of 249 with `death1` recorded |
| `duration followed1` coding | almost always 1 | mostly 1 (2015–16), 30 (2017–19), 0 (2021–23) |

Also: 107 of 191 admissions in 2020 have no disposition; 132 of 205 admissions in 2021–2023 have disposition "Other".

## Questions (smallest set that would let us finalise the endpoint)

**Q1. Meaning of `death1`.** Does `death1` record (a) death at any time from stroke onset/admission up to the month-1 contact, (b) death after discharge only, up to a contact about 30 days after discharge, or (c) something else? Did this change around 2014–2015? If so, what changed and when?

**Q2. Time origin.** From which date is the month-1 contact counted: stroke onset, admission (`Date of entry`), discharge (`Release date`), or another date? The submitted manuscript says vital status was ascertained "by structured telephone follow-up at days 7, 14 and 30 after discharge". Is this correct, and for which years?

**Q3. Meaning of `death1 = No`.** Does it mean the patient was confirmed alive at the contact, or could it also be entered when the patient was not reached?

**Q4. Disposition "death" (`Become after leaving UNV`).** Does it mean death before leaving the neurology unit (UNV)? Is `Release date` the date of death for these patients? Could it include deaths elsewhere in the hospital after transfer out of the unit?

**Q5. Disposition "Other".** What does "Other" mean, particularly in 2021–2023, when it is the most frequent value? Does it include discharge home, discharge against medical advice, or death?

**Q6. Units and codes of `duration followed1/3/6/9`.** Are the values in months (1, 3, 6, 9) or days (30, 90, 180, 270)? What does 0 mean? What do the values 9, 3 and 99 mean in the `death1`/`death3` fields?

**Q7. Post-discharge deaths from 2015 onwards.** From 2015, almost no post-discharge deaths are recorded. Were post-discharge deaths still captured (for example in another register or file), or did follow-up of discharged patients stop or change?

**Q8. Missing dispositions in 2020.** Are discharge records available for the 107 admissions of 2020 with no disposition? Were they affected by COVID-19 service changes?

**Q9. Modified Rankin score and laboratory values.** Is `Modified Rankin score` the pre-stroke score or the score at admission? Were the laboratory values (creatinine, urea, CRP, blood count, electrolytes) taken at admission?

**Q10. Repeated identifiers.** The code `unique_code` (initials and admission date) appears twice for 38 groups (listed by source-row number in the restricted annex, which is shared only with the registry team). For each pair, please tell us whether it is (a) the same admission entered twice, (b) a corrected re-entry (if so, which row is correct), or (c) two different patients.

**Q11. Date anomalies.** Twenty-two rows have a release date before the admission date, one has admission year 3016 and two have impossible release years. Can these be checked against the source files? (Rows are listed in the restricted annex.)

**Q12. Source dates of death for 33 post-discharge deaths.** The single most useful item: for the 33 patients with `death1 = Yes` who were not recorded as in-hospital deaths with a usable length of stay (listed in the restricted annex), the date of death, or failing that the date of the contact at which the death was reported. With these dates we can confirm or correct the 30-day classification directly.

## What happens with your answers

- If Q1, Q2 and Q4 confirm that `death1` counts from admission (or onset) and includes in-hospital deaths, the 33 post-discharge events become timing-established and the "strict" sensitivity analysis becomes secondary.
- If the month-1 window is anchored at discharge, the endpoint will be renamed "in-hospital or early post-discharge mortality" and the strict analysis becomes primary for the 30-day claim.
- Your answers to Q10 and Q11 will replace our rule-based decisions in the duplicate and date logs, and the whole analysis will be re-run from code.

Thank you. Every answer will be recorded, with your name and the date, in the decision log that accompanies the revised manuscript.
