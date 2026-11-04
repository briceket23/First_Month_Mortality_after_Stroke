"""Cleaning rules (unit harmonisation, plausibility ranges, date/LOS flags) are applied in registry.build_records and logged."""
from .registry import build_records  # noqa: F401


def cleaning_log(raw):
    return build_records(raw)[1]
