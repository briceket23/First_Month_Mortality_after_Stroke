# Registry semantics (what each outcome-defining field means, and on what evidence)

Sources: the registry data dictionary (`dictionary/stroke_data_dictionary.xlsx`, 256 variables, supplied 2 Nov 2026; identical content to `database_stroke_dict.csv`), the workbook value patterns, and the registry clarification request (`docs/registry_clarification_request.md`). Evidence levels: **documented** (dictionary text), **inferred** (from sibling fields or value patterns), **unknown**.

| Field (dictionary name) | Dictionary text (verbatim) | Time origin | Codes | Evidence | Use in the analysis |
|---|---|---|---|---|---|
| `death1` (décès1) | "Death at Month 1, recording if the patient passed away within the first month." | implicit: sibling month-1…12 items are "after the stroke" | Yes/No; one '9' | definition documented; origin inferred; 'No' semantics unknown (Q3) | E2 (Yes after discharge, assumption A2); N2 (No); grade R |
| `death3/6/9` | "… passed away within three/six/nine months." | as above | Yes/No; '3', '9' | cumulative wording documented; visit-specific vs cumulative not stated (Q9) | N4 (alive at a later contact) only when month-1 status is missing; a later death is never a 30-day event |
| `duration followed1/3/6/9` | "Duration of follow-up at Month n …" | — | 1/30 at M1; 3/90 at M3; 6/180; 9/270; 0 in 2021–23 | nominal schedule values (inferred); unit unknown (Q10) | not used as time; documents the change in recording practice |
| `Become after leaving UNV` (devenir) | "Outcome after leaving the UNV, describing the patient's condition after discharge." | — | RAD, death, Other, transfer…, '6' | documented label; 'Other' unknown (Q5) | A1: death = in-hospital death; 'Other' never survival evidence |
| `Release date` / `Length of hospitalization` | "The date when the patient was discharged or released" / "Length of hospitalization, measuring the total time…" (typed 'date') | admission | integer days; 99 missing code | release = date of death for the deceased is inferred (217/219 causes of death belong to disposition 'death'; Q5); LOS convention mixed (Q6) | stay = date-derived elapsed days when valid (0–120), else recorded LOS; boundary conflicts unresolved |
| `Cause of death` | "Cause of death, recording the cause if the patient passed away." | — | 5 categories; '0', '9', '99' | documented | never used as a date; supports A1 |
| `Date of entry` | "The date when the patient was first admitted or registered." | — | Excel datetime | documented | day 0 of the endpoint |
| `HGD arrival time` | "The time the patient arrived at the hospital" (onset-to-arrival) | — | values heap at multiples of 24 | unit inferred as hours | stroke-anchored sensitivity only |
| `unique_code` | "A unique alphanumeric identifier assigned to each patient" | — | initials + admission date | repeated in 38 pairs; readmissions cannot be linked | rule-based reconciliation (docs/outcome_reconstruction_protocol.md) |

Dictionary conformance (stage 1e): 256 variables; 242 labels match the workbook exactly; 94 variables without a type; value codes in descriptions: 0; hedged descriptions: age, CatAge, typprofe, délainew, traithab.
