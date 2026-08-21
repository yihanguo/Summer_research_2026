"""Outcome-aligned coordination experiments for Werewolf Arena."""

from .conditions import Condition, get_condition, primary_conditions
from .evidence import EvidenceItem, assign_complementary_evidence

__all__ = [
    "Condition",
    "EvidenceItem",
    "assign_complementary_evidence",
    "get_condition",
    "primary_conditions",
]
