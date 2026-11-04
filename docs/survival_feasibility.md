# Survival / interval-censored analysis feasibility (REQ-05; tickets EPI-SURV-001, OUTCOME-REC-004)

Reviewer #1 suggested "time-to-event approaches" for the 594 (now 597) patients without a determinable outcome. The conditions below were checked against the workbook and the data dictionary.

| Condition | Required | Status in the registry | Evidence |
|---|---|---|---|
| Time origin | Known index date per patient | Admission date available (1,639 valid); stroke onset only as an onset-to-arrival delay field with undocumented unit | `Date of entry`; `HGD arrival time` (values heap at multiples of 24; unit assumed hours) |
| Event time | Date of death or a bounded interval | No date-of-death field; cause of death is a category; release date = death date only under A1 for in-hospital deaths | dictionary audit |
| Censoring time | Date of last contact alive | Not recorded; follow-up durations are nominal schedule values (1/30 at M1, 3/90 at M3, 6/180, 9/270; 0 in 2021–23) | `duration followed*` value counts |
| Interval knowledge | Event known to lie between two dated visits | Visit dates not recorded; whether `death3 = No` certifies an alive contact (vs no death reported) is undocumented | Q3/Q9 of the registry request |
| Completeness of intervals | Follow-up recorded for most patients | Month-1 status recorded for 62%; later contacts for 45% (87% in 2010–12, ≤ 16% from 2017) | ascertainment tables |
| Loss to follow-up | Censoring plausibly non-informative given covariates | Labelling strongly associated with disposition, period and severity | labelled-vs-unresolved comparison |

**Conclusion.** A standard, discrete-time or interval-censored time-to-event analysis would require assigning every death and every censoring to a time that the registry does not record; converting scheduled visit months into event or censoring times would invent data. The analysis is therefore not implemented. What the data do support — and what the revision reports — is (i) a binary first-month outcome with explicit provenance, (ii) selection modelling of who has a determinable outcome, (iii) IPW and delta-adjusted estimates, and (iv) deterministic bounds. If the registry supplies contact dates and the meaning of a "No" status (Q3, Q9, Q10), an interval-censored analysis with admission as time origin becomes feasible and should be pre-specified before implementation.
