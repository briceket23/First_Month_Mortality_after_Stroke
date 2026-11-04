# Data quality report (generated)

Source: `database_stroke_copy.xlsx` (MD5 checked)

## Cohort flow

| Step | n |
|---|---|
| source_rows | 1653 |
| after_reconciliation | 1618 |
| excluded_blank_records | 6 |
| excluded_no_valid_admission_date | 6 |
| excluded_age_lt18 | 3 |
| excluded_tia | 24 |
| eligible | 1579 |
| labelled | 982 |
| deaths | 338 |
| unresolved | 597 |
| mortality_labelled_pct | 34.4 |

## Outcome classes (primary definition)

| Class | n |
|---|---|
| E1_inhosp_death_le30 | 305 |
| E2_month1_death_postdischarge | 33 |
| N1_inhosp_death_gt30 | 2 |
| N2_month1_alive | 617 |
| N3_discharged_alive_gt30 | 5 |
| N4_alive_later_contact | 20 |
| U_contradictory_status | 10 |
| U_discharged_alive_no_followup | 349 |
| U_disposition_missing_no_followup | 120 |
| U_duplicate_outcome_conflict | 7 |
| U_inhosp_death_timing_unknown | 2 |
| U_later_death_timing_unknown | 1 |
| U_los_conflict_at_boundary | 8 |
| U_other_disposition_no_followup | 90 |
| U_record_misaligned | 10 |

## Duplicate identifiers

Groups: 38; decisions: {'D2_same_encounter_compatible': 26, 'D3_same_encounter_outcome_conflict': 7, 'D1_identifier_collision': 4, 'D0_non_record': 1}

## Date / LOS parser reconciliation

pandas 3.1.0: {'complete_pairs': 1488, 'equal': 821, 'differ': 667, 'negative_in_pairs': 23, 'negative_all_date_pairs': 24, 'pandas_version': '3.1.0'}

openpyxl raw cells: pairs 1488, equal 821, differ 667, negative 23; reconciled = True

All date cells are Excel datetimes. pandas < 3.0 stores timestamps in nanoseconds and converts years > 2262 to NaT silently; the two rows with such years (entry 3016; release 2916) account for the earlier 1,486/665/22 figures. Both rows are flagged as invalid dates (never corrected) by the integrity rules.

## Dictionary conformance

256 variables; 242 labels match; 94 without type; value codes in descriptions: 0

## Cleaning and integrity log

| Step | Item | Records | Detail |
|---|---|---|---|
| integrity | column_shift | 14 | >= 3 numeric codes in Yes/No fields (misaligned row) |
| integrity | blank_record | 9 | no admission date, age or sex |
| dates_los | flag_entry_missing | 14 | flagged; raw value preserved |
| dates_los | flag_entry_impossible_year | 1 | flagged; raw value preserved |
| dates_los | flag_release_impossible_year | 2 | flagged; raw value preserved |
| dates_los | flag_release_before_entry | 22 | flagged; raw value preserved |
| dates_los | flag_date_stay_implausible | 9 | flagged; raw value preserved |
| dates_los | flag_los_missing_code | 1 | flagged; raw value preserved |
| dates_los | flag_los_implausible | 0 | flagged; raw value preserved |
| dates_los | flag_los_disagree | 84 | flagged; raw value preserved |
| outcome_fields | death1_invalid_code | 1 | non Yes/No code (undocumented, e.g. 9/3) -> treated as unknown |
| outcome_fields | death3_invalid_code | 3 | non Yes/No code (undocumented, e.g. 9/3) -> treated as unknown |
| outcome_fields | death6_invalid_code | 0 | non Yes/No code (undocumented, e.g. 9/3) -> treated as unknown |
| outcome_fields | death9_invalid_code | 0 | non Yes/No code (undocumented, e.g. 9/3) -> treated as unknown |
| population | age_outside_18_110 | 3 | set to NA |
| range_to_NA | gcs | 15 | outside [3, 15] |
| range_to_NA | mrs | 2 | outside [0, 5] |
| range_to_NA | sbp | 2 | outside [50, 300] |
| range_to_NA | dbp | 17 | outside [30, 200] |
| range_to_NA | heart_rate | 5 | outside [20, 220] |
| range_to_NA | resp_rate | 10 | outside [5, 60] |
| unit_fix | temperature_x10 | 13 | values > 50 divided by 10 |
| range_to_NA | temperature | 22 | outside [30, 43] |
| range_to_NA | spo2 | 15 | outside [50, 100] |
| range_to_NA | bmi | 9 | outside [10, 80] |
| range_to_NA | glucose_cap (g/L) | 13 | outside [0.2, 8] |
| range_to_NA | creatinine (mg/L -> mg/dL) | 12 | outside [0.1, 25] |
| unit_convert | creatinine | 1298 | mg/L -> mg/dL (/10) |
| range_to_NA | urea (g/L) | 20 | outside [0, 6] |
| range_to_NA | total_cholesterol | 46 | outside [0.3, 15] |
| range_to_NA | hemoglobin | 2 | outside [3, 22] |
| unit_harmonise | wbc | 310 | absolute counts /1000 -> x10^3/uL |
| range_to_NA | wbc | 5 | outside [0.5, 60] |
| unit_harmonise | platelets | 305 | absolute counts /1000 -> x10^3/uL |
| range_to_NA | platelets | 2 | outside [5, 1200] |
| range_to_NA | sodium | 10 | outside [100, 180] |
| range_to_NA | potassium | 8 | outside [1.5, 9] |
| integrity | column_shift_predictors_blanked | 14 | clinical predictors set to NA in misaligned rows (raw kept) |

## CSV export supplied on 3 November 2026 (`database_stroke.csv`)

- 1655 rows × 256 columns; 2 extra rows (blank (no identifier content beyond code)).
- Contains directly identifying columns (patients name, Follow-up location/hospital, Number tél 1, Number tél 2); never copied into this project.
- Dates: dd/mm/yyyy; all 1,639 entry and 1,513 release dates identical to the workbook.
- Numeric precision: laboratory and vital-sign values rounded to integers and thousands separated by spaces (e.g. 'GB blood' 31 500; K+ 4 vs 3.66 in the workbook).
- `Release date.1`: Excel serial number of the release date (identical date).
- **Decision:** The workbook (xlsx, MD5 08541ef1…) remains the analysed source: higher precision, no direct identifiers. The CSV export is not used and must not enter any project folder or archive.
