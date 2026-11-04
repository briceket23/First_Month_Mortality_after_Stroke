"""Write docs/data_quality_report.md from the audit outputs of the current run (aggregate only)."""
import json, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from stroke_repro import config as C

def main():
    A = C.AUDIT; CO = C.COHORT
    flows = json.loads((CO / "cohort_flows.json").read_text(encoding="utf-8"))["primary"]
    pr = json.loads((A / "date_los_parser_reconciliation.json").read_text(encoding="utf-8"))
    da = json.loads((A / "dictionary_audit.json").read_text(encoding="utf-8"))
    log = pd.read_csv(A / "cleaning_and_integrity_log.csv") if (A / "cleaning_and_integrity_log.csv").exists() else pd.DataFrame()
    dl = pd.read_csv(CO / "duplicate_decision_log.csv")
    md = ["# Data quality report (generated)", "", f"Source: `{C.RAW_XLSX.name}`" + (" — **SYNTHETIC FIXTURE, no registry data**" if C.SYNTHETIC else " (MD5 checked)"), "",
          "## Cohort flow", "", "| Step | n |", "|---|---|"] + [f"| {k} | {v} |" for k, v in flows.items() if k != "class_counts"] + ["",
          "## Outcome classes (primary definition)", "", "| Class | n |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(flows["class_counts"].items())] + ["",
          "## Duplicate identifiers", "", f"Groups: {dl.dup_group.nunique() if 'dup_group' in dl else len(dl)}; decisions: {dl.decision.value_counts().to_dict() if 'decision' in dl else 'n/a'}", "",
          "## Date / LOS parser reconciliation", "", f"pandas {pr['pandas_current']['pandas_version']}: {pr['pandas_current']}", "", f"openpyxl raw cells: pairs {pr['openpyxl_raw_cells']['complete_pairs']}, equal {pr['openpyxl_raw_cells']['equal']}, differ {pr['openpyxl_raw_cells']['differ']}, negative {pr['openpyxl_raw_cells']['negative_in_pairs']}; reconciled = {pr['reconciled']}", "", pr["explanation"], "",
          "## Dictionary conformance", "", f"{da['conformance']['dictionary_rows']} variables; {da['conformance']['dictionary_labels_matched_exactly']} labels match; {da['conformance']['variables_without_type']} without type; value codes in descriptions: {da['conformance']['descriptions_with_value_codes']}", ""]
    if len(log):
        md += ["## Cleaning and integrity log", "", "| Step | Item | Records | Detail |", "|---|---|---|---|"] + [f"| {r.step} | {r.item} | {r.n_records} | {r.detail} |" for r in log.itertuples()]
    csvcmp = ROOT / "docs" / "csv_export_comparison.json"
    if csvcmp.exists():
        c = json.loads(csvcmp.read_text(encoding="utf-8"))
        md += ["", "## CSV export supplied on 3 November 2026 (`database_stroke.csv`)", "", f"- {c['csv_rows']} rows × {c['csv_columns']} columns; {c['extra_rows_vs_workbook']} extra rows ({c['extra_rows_content']}).", f"- Contains directly identifying columns ({', '.join(c['identifying_columns_present'])}); never copied into this project.",
               f"- Dates: {c['date_format']}.", f"- Numeric precision: {c['numeric_precision']}.", f"- `Release date.1`: {c['release_date_1']}.", f"- **Decision:** {c['decision']}"]
    (ROOT / "docs" / "data_quality_report.md").write_text("\n".join(md) + "\n", encoding="utf-8"); print("wrote docs/data_quality_report.md")

if __name__ == "__main__":
    main()
