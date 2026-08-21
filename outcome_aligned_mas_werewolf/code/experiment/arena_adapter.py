"""Small adapter layer for the existing ``werewolf`` package.

The adapter keeps the base Arena classes usable without an experiment. Pass an
``ExperimentEventSink`` to ``werewolf.game.GameMaster`` and call
``configure_players`` before the first model call.
"""

import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

from .conditions import Condition
from .events import BeliefSnapshotEvent, PublicMessageEvent, RoundExtractionEvent
from .evidence import EvidenceItem
from .policies import policy_text


class ExperimentEventSink:
    def __init__(self, condition: Condition):
        self.condition = condition
        self.events: List[object] = []

    def record_public_message(self, **kwargs) -> PublicMessageEvent:
        event = PublicMessageEvent(
            event_id=kwargs["event_id"],
            round=kwargs["round_number"],
            turn=kwargs["turn_number"],
            speaker=kwargs["speaker"],
            recipients=list(kwargs["recipients"]),
            dialogue=kwargs["dialogue"],
            evidence_refs=list(kwargs.get("evidence_refs", [])),
            confidence=kwargs.get("confidence"),
            public_suspect_levels=[
                dict(item) for item in kwargs.get("public_suspect_levels", [])
            ],
            structured_repair=bool(kwargs.get("structured_repair", False)),
            structured_repair_reason=kwargs.get("structured_repair_reason", ""),
            prompt_policy=kwargs.get("prompt_policy", ""),
            condition_id=self.condition.condition_id,
        )
        self.events.append(event)
        return event

    def record_round_extraction(self, **kwargs) -> RoundExtractionEvent:
        event = RoundExtractionEvent(
            event_id=kwargs["event_id"],
            round=kwargs["round_number"],
            player=kwargs["player"],
            source_message_ids=list(kwargs.get("source_message_ids", [])),
            extracted_claims=list(kwargs.get("extracted_claims", [])),
            summary=kwargs.get("summary", ""),
            confidence=kwargs.get("confidence"),
            visible_to=[kwargs["player"]],
            condition_id=self.condition.condition_id,
        )
        self.events.append(event)
        return event

    def record_belief_snapshot(self, **kwargs) -> BeliefSnapshotEvent:
        event = BeliefSnapshotEvent(
            event_id=kwargs["event_id"],
            round=kwargs["round_number"],
            turn=kwargs["turn_number"],
            player=kwargs["player"],
            living_players=list(kwargs["living_players"]),
            source_message_ids=list(kwargs.get("source_message_ids", [])),
            bid=int(kwargs["bid"]),
            speaker_eligible=bool(kwargs.get("speaker_eligible", True)),
            top_suspect=kwargs["top_suspect"],
            suspect_confidence_bin=int(kwargs["suspect_confidence_bin"]),
            intended_vote=kwargs["intended_vote"],
            evidence_state=kwargs["evidence_state"],
            suspect_levels=[dict(item) for item in kwargs["suspect_levels"]],
            structured_repair=bool(kwargs.get("structured_repair", False)),
            structured_repair_reason=kwargs.get("structured_repair_reason", ""),
            prompt_policy=kwargs.get("prompt_policy", ""),
            condition_id=self.condition.condition_id,
        )
        self.events.append(event)
        return event

    def write_jsonl(self, path: str | Path) -> None:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as handle:
            for event in self.events:
                handle.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")


def configure_players(
    players: Mapping[str, object],
    condition: Condition,
    evidence_by_player: Mapping[str, Sequence[EvidenceItem]],
    max_debate_turns: int | None = None,
) -> None:
    """Inject only holder-visible evidence and the condition policy."""
    for name, player in players.items():
        is_wolf = getattr(player, "role", "") == "Werewolf"
        policy_name = condition.wolf_policy if is_wolf else condition.good_policy
        player.coordination_policy_name = policy_name
        player.coordination_policy = policy_text(policy_name)
        player.private_evidence = [
            item.to_prompt_dict() for item in evidence_by_player.get(name, [])
        ]
        player.private_round_memory = []
        player.max_debate_turns = max_debate_turns or condition.max_debate_turns


def validate_open_broadcast(
    events: Iterable[PublicMessageEvent], living_players: Sequence[str]
) -> None:
    for event in events:
        if set(event.recipients) != set(living_players):
            raise AssertionError(
                f"Message {event.event_id} did not reach every living player."
            )
