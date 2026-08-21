"""Metrics for evidence, communication, extraction, and task utility."""

from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set

from .events import PublicMessageEvent, RoundExtractionEvent
from .evidence import EvidenceItem


def evidence_coverage(
    messages: Iterable[PublicMessageEvent], evidence: Sequence[EvidenceItem]
) -> float:
    gold = {item.evidence_id for item in evidence}
    surfaced = {ref for message in messages for ref in message.evidence_refs}
    return len(gold & surfaced) / len(gold) if gold else 0.0


def evidence_correctness(
    messages: Iterable[PublicMessageEvent], evidence: Sequence[EvidenceItem]
) -> float:
    gold = {item.evidence_id for item in evidence}
    refs = [ref for message in messages for ref in message.evidence_refs]
    return sum(ref in gold for ref in refs) / len(refs) if refs else 1.0


def echo_rate(messages: Iterable[PublicMessageEvent]) -> float:
    seen: Set[str] = set()
    refs: List[str] = []
    repeated: List[str] = []
    for message in messages:
        for ref in message.evidence_refs:
            refs.append(ref)
            if ref in seen:
                repeated.append(ref)
            seen.add(ref)
    return len(repeated) / len(refs) if refs else 0.0


def extraction_metrics(
    extractions: Iterable[RoundExtractionEvent],
    message_ids_available: Mapping[str, Set[str]],
) -> Dict[str, float]:
    events = list(extractions)
    available = sum(len(ids) for ids in message_ids_available.values())
    carried = sum(
        len(set(event.source_message_ids) & message_ids_available.get(event.player, set()))
        for event in events
    )
    claims = [claim for event in events for claim in event.extracted_claims]
    return {
        "extraction_coverage": carried / available if available else 0.0,
        "extraction_fidelity": 1.0 if claims else 0.0,
        "cross_round_reuse": 0.0,
    }


def day_utility(correct_wolf_exile: bool, wrong_good_exile: bool) -> int:
    if correct_wolf_exile:
        return 1
    if wrong_good_exile:
        return -1
    return 0


def episode_metrics(
    *,
    messages: Sequence[PublicMessageEvent],
    extractions: Sequence[RoundExtractionEvent],
    evidence: Sequence[EvidenceItem],
    votes: Mapping[str, str],
    wolves: Set[str],
    exiled: str | None,
    available_message_ids: Mapping[str, Set[str]] | None = None,
) -> Dict[str, Any]:
    good_votes = [target for player, target in votes.items() if player not in wolves]
    counts = Counter(good_votes)
    first_target = good_votes[0] if good_votes else None
    anchoring = (
        counts[first_target] / len(good_votes)
        if first_target and good_votes
        else 0.0
    )
    correct = exiled in wolves if exiled else False
    wrong = exiled is not None and exiled not in wolves
    extraction = extraction_metrics(
        extractions,
        available_message_ids or {},
    )
    return {
        "good_team_win": int(correct),
        "correct_wolf_exile": int(correct),
        "wrong_good_exile": int(wrong),
        "u_day": day_utility(correct, wrong),
        "evidence_coverage": evidence_coverage(messages, evidence),
        "evidence_correctness": evidence_correctness(messages, evidence),
        "echo_rate": echo_rate(messages),
        "anchoring_index": anchoring,
        **extraction,
    }
