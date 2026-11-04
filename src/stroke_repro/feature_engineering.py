"""Admission-time candidate predictors (config.NUMERIC + config.BINARY); unit harmonisation in ingest; no engineered features in the primary model (the Glasgow-to-NIHSS ratio is a sensitivity feature only)."""
from . import config as C
CANDIDATES = C.NUMERIC + C.BINARY
CLINICAL_REFERENCE = C.CLINICAL_REFERENCE
