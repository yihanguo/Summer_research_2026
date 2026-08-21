"""Serializable event contracts for the experiment."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional


class Event:
    event_type: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PublicMessageEvent(Event):
    event_type: str = field(init=False, default="public_message")
    event_id: str = ""
    round: int = 0
    turn: int = 0
    speaker: str = ""
    recipients: List[str] = field(default_factory=list)
    dialogue: str = ""
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
    public_suspect_levels: List[Dict[str, Any]] = field(default_factory=list)
    structured_repair: bool = False
    structured_repair_reason: str = ""
    prompt_policy: str = ""
    condition_id: str = ""


@dataclass
class RoundExtractionEvent(Event):
    event_type: str = field(init=False, default="round_extraction")
    event_id: str = ""
    round: int = 0
    player: str = ""
    source_message_ids: List[str] = field(default_factory=list)
    extracted_claims: List[str] = field(default_factory=list)
    summary: str = ""
    confidence: Optional[float] = None
    visible_to: List[str] = field(default_factory=list)
    condition_id: str = ""


@dataclass
class BeliefSnapshotEvent(Event):
    """A private pre-speech state measurement for one living agent."""

    event_type: str = field(init=False, default="belief_snapshot")
    event_id: str = ""
    round: int = 0
    turn: int = 0
    player: str = ""
    living_players: List[str] = field(default_factory=list)
    source_message_ids: List[str] = field(default_factory=list)
    bid: int = 0
    speaker_eligible: bool = True
    top_suspect: str = ""
    suspect_confidence_bin: int = 0
    intended_vote: str = ""
    evidence_state: str = "none"
    suspect_levels: List[Dict[str, Any]] = field(default_factory=list)
    structured_repair: bool = False
    structured_repair_reason: str = ""
    prompt_policy: str = ""
    condition_id: str = ""


@dataclass
class EpisodeManifest:
    condition_id: str
    seed: int
    role_assignment: Dict[str, str]
    player_names: List[str]
    evidence_mode: str
    good_policy: str
    wolf_policy: str
    public_broadcast: bool = True
    max_debate_turns: int = 8
    synthetic_votes: bool = False
    round_extraction: bool = True
    extraction_schema_version: str = "v1"
    belief_snapshot_schema_version: str = "v2"
    complete_belief_panel_each_turn: bool = True
    model_ids: Dict[str, str] = field(default_factory=dict)
    condition_slug: str = ""
    legacy_condition_id: str = ""
    good_intervention: bool = False
    wolf_intervention: bool = False
    evidence_available: bool = False
    model_metadata: Dict[str, Any] = field(default_factory=dict)
    generation_parameters: Dict[str, Any] = field(default_factory=dict)
    git_commit: Optional[str] = None
    git_dirty: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def serialize_events(events: Iterable[Event]) -> List[Dict[str, Any]]:
    return [event.to_dict() for event in events]
