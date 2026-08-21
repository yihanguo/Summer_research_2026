"""Deterministic positive-evidence fixtures and validators."""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Set


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    claim_text: str
    holder: str
    source_type: str
    truth_value: bool
    target_hypothesis: str
    direction: int
    strength: float
    directness: str

    def to_prompt_dict(self) -> Dict[str, object]:
        """Return only fields that a player is allowed to see."""
        return {
            "evidence_id": self.evidence_id,
            "claim_text": self.claim_text,
            "source_type": self.source_type,
            "directness": self.directness,
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "evidence_id": self.evidence_id,
            "claim_text": self.claim_text,
            "holder": self.holder,
            "source_type": self.source_type,
            "truth_value": self.truth_value,
            "target_hypothesis": self.target_hypothesis,
            "direction": self.direction,
            "strength": self.strength,
            "directness": self.directness,
        }


def generate_positive_evidence(target: str, holders: Sequence[str]) -> List[EvidenceItem]:
    """Create a small deterministic fixture with complementary weak clues."""
    if len(holders) < 3:
        raise ValueError("At least three good-agent holders are required.")
    claims = [
        ("E01", "The night-event timing conflicts with one candidate's reported account."),
        ("E02", "The vote pattern contains a reversal immediately after a challenge."),
        ("E03", "Role constraints leave one candidate consistent with the observed event sequence."),
        ("E04", "Two independent observations agree about the same candidate's timeline."),
    ]
    return [
        EvidenceItem(
            evidence_id=evidence_id,
            claim_text=claim_text,
            holder=holders[index % len(holders)],
            source_type=("night-event", "vote-pattern", "role-constraint", "observation")[index],
            truth_value=True,
            target_hypothesis=target,
            direction=1,
            strength=0.5 + 0.1 * index,
            directness="direct" if index != 2 else "derived",
        )
        for index, (evidence_id, claim_text) in enumerate(claims)
    ]


def validate_evidence(evidence: Iterable[EvidenceItem], target: str) -> None:
    items = list(evidence)
    if not items:
        raise ValueError("Evidence fixture cannot be empty.")
    ids: Set[str] = set()
    for item in items:
        if item.evidence_id in ids:
            raise ValueError(f"Duplicate evidence ID: {item.evidence_id}")
        ids.add(item.evidence_id)
        if not item.truth_value or item.direction != 1 or item.strength <= 0:
            raise ValueError(f"Evidence item is not truthful and positive: {item.evidence_id}")
        if item.target_hypothesis != target:
            raise ValueError(f"Evidence points to the wrong target: {item.evidence_id}")


def assign_complementary_evidence(
    evidence: Sequence[EvidenceItem], good_players: Sequence[str]
) -> Dict[str, List[EvidenceItem]]:
    """Partition evidence deterministically while preserving the union."""
    if not good_players:
        raise ValueError("Cannot assign evidence without good players.")
    assignments = {name: [] for name in good_players}
    for index, item in enumerate(evidence):
        assignments[good_players[index % len(good_players)]].append(item)
    return assignments


def evidence_sufficiency(
    evidence: Iterable[EvidenceItem], target: str, available_ids: Iterable[str] | None = None
) -> bool:
    """Fixture oracle: all positive clues must support the target."""
    items = list(evidence)
    validate_evidence(items, target)
    if available_ids is None:
        return bool(items)
    available = set(available_ids)
    return {item.evidence_id for item in items}.issubset(available)


def evidence_by_id(evidence: Iterable[EvidenceItem]) -> Mapping[str, EvidenceItem]:
    return {item.evidence_id: item for item in evidence}
