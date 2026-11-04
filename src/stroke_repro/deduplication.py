"""Duplicate-identifier reconciliation: rule-based, logged per group; conflicting outcomes never forced; keep-first and exclude-conflicts only as labelled sensitivity rules. Implementation: reconcile.reconcile."""
from .reconcile import reconcile, OUTCOME_FIELDS, PRED_FIELDS  # noqa: F401
