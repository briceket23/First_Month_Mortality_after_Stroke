# Registry questions unresolved at submission

Sent list: `review_audit/04_REGISTRY_CLARIFICATION_QUESTIONS.md`. Whether the registry team has been contacted and replied is for the corresponding author to record here [AUTHOR VERIFICATION]. None of these blocks the analysis as submitted; each is disclosed as a limitation in the manuscript (Methods 2.4, Limitations) and in the response letter.

| Question | Field | Tickets still BLOCKED | Where disclosed | What would change if answered |
|---|---|---|---|---|
| Q1/Q2 explicit time origin of death1 and follow-up procedure | death1, follow-up | OUTCOME-TIME-001 | Methods 2.4; Limitations; R1-1 | If admission- or stroke-anchored: no change (A2 holds). If discharge-anchored: strict endpoint becomes primary (already computed, AUROC 0.872) |
| Q3 meaning of death1 = No | death1 | OUTCOME-TIME-002 | Methods 2.4 (grade R) | If 'No' may mean not reached: N2 labels downgraded; bounds widen |
| Q4/Q12 dates of death | — | OUTCOME-TIME-003 | Methods 2.4; R1-1 | 33 post-discharge events re-timed; A2 no longer needed |
| Q5 release date for deceased | Release date | OUTCOME-TIME-004 | Methods 2.4 (A1) | If not the death date: in-hospital event timing re-derived |
| Q6/Q7 LOS units and authoritative field | LOS | DATA-DATE-002 | Methods 2.2 | Boundary labels (≤ 11 patients at days 28–32) could change |
| Q8 reconciliation of 38 repeated identifiers | unique_code | DATA-DUP-001 | Methods 2.2; Limitations | Cohort ±3 patients; AUROC change < 0.01 under the tested rules |
| Q9 cumulative vs visit-specific death3/6/9 | death3/6/9 | OUTCOME-REC-003 | Methods 2.4 | 20 N4 labels; sensitivity without them already reported (0.859) |
| Q10 units of follow-up durations | duration followed* | OUTCOME-REC-004 | Methods 2.5 | Enables interval-censored analysis if contact dates exist |
| Q11 codes (9, 3, 99, 0, 'Other', 6) | several | DATA-DICT-002 | Methods 2.4 (grade X) | Few labels; 'Other' disposition could supply up to 90 labels |
| Q12 (dispositions 2020) | disposition | EPI-SEL-002 | Methods 2.5 (positivity restriction) | IPW target population could include 2020 admissions |
