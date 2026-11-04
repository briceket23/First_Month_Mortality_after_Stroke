"""Restricted annex for the registry team (row-level; never part of the public package)."""
import pandas as pd

from . import config as C


def main():
    rec = pd.read_pickle(C.RESTRICTED / "records.pkl")
    pts = pd.read_pickle(C.RESTRICTED / "cohort_primary.pkl")
    dl = pd.read_csv(C.RESTRICTED / "duplicate_decision_log_with_codes.csv")
    with pd.ExcelWriter(C.RESTRICTED / "RESTRICTED_registry_annex.xlsx") as xw:
        dl[["dup_group", "unique_code", "src_ids", "decision", "reason", "applied"]].to_excel(xw, sheet_name="Q10_duplicates", index=False)
        bad = rec[rec.flag_release_before_entry | rec.flag_entry_impossible_year | rec.flag_release_impossible_year]
        bad[["src_id", "src_row", "unique_code", "entry_date_raw", "release_date_raw", "los_raw"]].to_excel(xw, sheet_name="Q11_dates", index=False)
        e2 = pts[pts.y_class == "E2_month1_death_postdischarge"]
        e2[["patient_key", "src_ids", "unique_code", "entry_date", "release_date", "disp", "los_days", "death1", "death3"]].to_excel(xw, sheet_name="Q12_postdischarge_deaths", index=False)
        conf = pts[pts.y_class.isin(["U_contradictory_status", "U_duplicate_outcome_conflict", "U_record_misaligned", "U_los_conflict_at_boundary"])]
        conf[["patient_key", "src_ids", "unique_code", "y_class", "y_reason"]].to_excel(xw, sheet_name="conflicts", index=False)
    print("restricted annex written:", len(dl), len(bad), len(e2), len(conf))


if __name__ == "__main__":
    main()
