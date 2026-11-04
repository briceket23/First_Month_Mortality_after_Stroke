# Endpoint specification (revision 1, 16 October 2026)

Implemented in `strokerev/endpoint.py` (function `assign`), tested in `tests/test_endpoint_and_reconcile.py`.

| Element | Specification |
|---|---|
| Name | First-month mortality: all-cause death within 30 days of hospital admission, including in-hospital death |
| Index date (day 0) | Registry `Date of entry` (admission). Records without a valid admission date (outside 2010–2023 or missing) are ineligible |
| Window | Elapsed days ≤ 30 (death on day 30 is an event; on day 31 it is not) |
| Target population | Adults (≥ 18 y) admitted to the Douala General Hospital neurology unit with stroke (ischaemic, haemorrhagic, subarachnoid haemorrhage, cerebral venous thrombosis); transient ischaemic attack excluded |
| Elapsed stay | Release date minus admission date when both are valid and release ≥ admission; otherwise recorded length of stay (code 99 = missing). Convention of the recorded stay (elapsed vs inclusive days) is undocumented |
| Assumption A1 | Disposition "death" = death before leaving the unit; stay ends at death |
| Assumption A2 | `death1 = Yes` after discharge = death within 30 days of admission (unverified; strict variant removes it) |

## Evidence hierarchy (applied after duplicate reconciliation)

Conflicts are evaluated first; any of the following makes the record **unresolved (contradictory)**:
in-hospital death within 30 d with `death1 = No`; in-hospital death with a later contact recording the patient alive; `death1 = Yes` with in-hospital death after day 30; `death1 = Yes` with a later contact recording the patient alive. Duplicate groups whose rows disagree on outcome fields, and column-misaligned rows, are also unresolved.

| Class | Rule | Label | Timing |
|---|---|---|---|
| E1 | Disposition death, elapsed stay ≤ 30 d | 1 | Established under A1 |
| N1 | Disposition death, elapsed stay > 30 d | 0 | Established under A1 |
| E2 | `death1 = Yes`, not an in-hospital death (or in-hospital death with unknown stay) | 1 | Conditional on A2 |
| N2 | `death1 = No` | 0 | Established (alive at the month-1 contact, which is at least 30 days after admission under any plausible origin except onset; onset precedes admission by hours to days) |
| N3 | No `death1`; discharged home or transferred after > 30 d | 0 | Established |
| N4 | No `death1`; `death3/6/9 = No` | 0 | Established (alive later implies alive on day 30) |
| U | Anything else: discharged alive ≤ 30 d without follow-up; missing or "Other" disposition without follow-up; death recorded only at month 3–9; recorded and date-derived stays on opposite sides of day 30 (when `death1` is absent); in-hospital death with no usable stay and no `death1`; undocumented codes (9, 3) | NA | Never forced |

Never used: cause of death as a date; length of stay for patients not recorded as dying in hospital; month-3/6/9 deaths as 30-day events.

## Variants

| Variant | Difference |
|---|---|
| Strict | E2 → unresolved (all events timed by hospital record) |
| Observed-only | `death1` Yes/No only (the conventional complete-case rule) |
| Submitted reconstruction (audit only) | Keep-first de-duplication; `death1` used whenever present (even if contradicted); in-hospital death by stay; long stay with any non-death disposition (including "Other") = alive; later "No" = alive |

## Counts (primary, eligible n = 1,579)

E1 305; E2 33; N1 2; N2 617; N3 5; N4 20 → labelled 982, deaths 338 (34.4%). Unresolved 597: discharged alive without follow-up 349; missing disposition 120; "Other" disposition 90; contradictory 10; misaligned 10; stay boundary conflict 8; duplicate outcome conflict 7; in-hospital death without stay 2; later death only 1. Strict: labelled 949, deaths 305 (32.1%). (Counts updated 2 Nov 2026 from `outputs/cohort/cohort_flows.json`; the earlier figures predated the exclusion of date-derived stays above 120 days.)

## Boundary unit tests (all pass)

Death on day 30 → event; day 31 → alive on day 30; discharge alive after day 30 → non-event; discharge alive on day 30 without follow-up → unresolved; later follow-up alive without event date → non-event; later death without date → unresolved; in-hospital death ≤ 30 d with `death1 = No` → contradiction; in-hospital death after 30 d with `death1 = No` → consistent non-event; `death1 = Yes` but alive later → contradiction; post-discharge `death1 = Yes` → conditional event, unresolved under strict; code 9 → unknown; "Other" disposition with long stay → unresolved; stay measures straddling day 30 → unresolved; cause of death not used.


## Data dictionary (received 2 November 2026)

The registry's data dictionary (`dictionary/stroke_data_dictionary.xlsx`, MD5 `be778aa0…`, 256 variables) was audited against the workbook by `strokerev/stage1e_dictionary_audit.py`.

| Field | Dictionary text (verbatim) | Consequence for the endpoint |
|---|---|---|
| `death1` (décès1) | "Death at Month 1, recording if the patient passed away within the first month." | Event = death within month 1. In-hospital deaths within month 1 should be recorded as Yes; from 2015 they mostly were not (completion, not definition, changed). |
| Month-1 to month-12 assessments | e.g. `barthel1`: "… one month after the stroke"; month 3–12 items "… months after the stroke" | Time origin of follow-up = the stroke (implicit for `death1`). Supports A2: a death within one month of the stroke falls within 30 days of admission. |
| `duration followed1` (dursuiv1) | "Duration of follow-up at Month 1 …" | Values 1 (2010–16) and 30 (2017–19) consistent with one month in months/days; 0 (2021–23) unexplained. |
| `Become after leaving UNV` (devenir) | "Outcome after leaving the UNV …" | Supports A1. |
| Codes, date of death | none | Codes 3/9 remain undocumented (grade X); no date of death exists. |

**Grades.** The dictionary defines the fields but not their time origin or codes, and no dates of death exist, so the pre-specified rule (E1/E0 requires documented dates or an unequivocal definition) still assigns grade R to month-1 to month-9 statuses and grade I to in-hospital events. No label changed.

**New sensitivity endpoint (stroke-anchored window).** If month 1 starts at the stroke, `death1 = No` certifies survival only to onset + 1 month, which ends before admission + 30 days by the onset-to-arrival delay (`HGD arrival time`; unit undocumented, read as hours because values heap at multiples of 24). N2 labels with delay > 72 h are treated as unresolved (variant `onset_anchor_gap`), and additionally those with unknown delay (`onset_anchor_gap_unknown_excluded`).
