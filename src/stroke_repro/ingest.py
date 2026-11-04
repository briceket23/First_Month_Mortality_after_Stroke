"""Ingestion: read the registry workbook without altering it; attach stable source-row ids; derive separate cleaned fields.
Implementation: registry.load_raw, registry.build_records, registry.md5."""
from .registry import RAW_FIELDS, load_raw, build_records, md5  # noqa: F401
