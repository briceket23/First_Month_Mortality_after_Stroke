"""Schema, dictionary and configuration consistency."""
import yaml
from conftest import ROOT
from stroke_repro import config as C
from stroke_repro.ingest import RAW_FIELDS


def test_yaml_configs_load_and_match_constants():
    y = C.YAML
    assert y["registry_schema"]["source"]["worksheet"] == "Feuil1" and y["registry_schema"]["source"]["expected_columns"] == 251
    assert sorted(y["preprocessing"]["candidate_predictors"]) == sorted(C.NUMERIC + C.BINARY)
    assert y["outcome_definition"]["approval_state"] in y["outcome_definition"]["approval_state_values"]


def test_all_required_workbook_columns_declared():
    cols = [c.strip() for c in (ROOT / "config" / "workbook_columns.txt").read_text(encoding="utf-8").splitlines() if c.strip()]
    assert len(cols) == 251 and set(RAW_FIELDS) <= set(cols)


def test_dictionary_csv_declared_encoding():
    assert C.YAML["registry_schema"]["source"]["dictionary_csv_encoding"] == "cp1252"
