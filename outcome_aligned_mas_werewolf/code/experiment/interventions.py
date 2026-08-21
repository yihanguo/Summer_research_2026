"""Replay helpers for message-level counterfactual interventions."""

from dataclasses import replace
from typing import Iterable, List, Sequence

from .events import PublicMessageEvent


def remove_first_target_message(
    messages: Sequence[PublicMessageEvent], target: str
) -> List[PublicMessageEvent]:
    """Replace the first target-bearing message with a length-matched marker."""
    changed = False
    result: List[PublicMessageEvent] = []
    for message in messages:
        if not changed and target.lower() in message.dialogue.lower():
            changed = True
            result.append(replace(message, dialogue="[message withheld by M1]"))
        else:
            result.append(message)
    return result


def remove_repeated_evidence(
    messages: Iterable[PublicMessageEvent],
) -> List[PublicMessageEvent]:
    seen = set()
    result = []
    for message in messages:
        new_refs = [ref for ref in message.evidence_refs if ref not in seen]
        seen.update(new_refs)
        result.append(replace(message, evidence_refs=new_refs))
    return result
