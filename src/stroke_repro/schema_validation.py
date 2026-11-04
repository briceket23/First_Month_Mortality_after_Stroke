"""Schema and dictionary validation: expected worksheet/shape (config/registry_schema.yaml), dictionary audit (stage 1e), parser reconciliation (scripts/date_parser_reconciliation.py)."""
from . import config as C
from .stage1e_dictionary_audit import main as audit_dictionary  # noqa: F401


def validate_columns(raw):
    """Return (missing_required_columns, shape_mismatch) for a raw frame read by ingest.load_raw."""
    from .registry import RAW_FIELDS
    sch = C.YAML["registry_schema"]["source"]
    missing = [k for k in RAW_FIELDS if k not in raw.columns]
    shape_ok = C.SYNTHETIC or (len(raw) == sch["expected_rows"] and raw.shape[1] - 2 == sch["expected_columns"])
    return missing, not shape_ok
