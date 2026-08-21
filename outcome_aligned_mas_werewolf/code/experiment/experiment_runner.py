"""Run the deterministic one-day controlled fixture from the proposal.

This is the first executable stage before full multi-round Arena integration.
It preserves open broadcast, logs every public message, gives each living agent
private round extraction, and writes analysis-ready JSON artifacts.
"""

import argparse
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Set

from .conditions import Condition, condition_cli_aliases, get_condition
from .evidence import EvidenceItem, assign_complementary_evidence, generate_positive_evidence, validate_evidence
from .events import (
    BeliefSnapshotEvent,
    EpisodeManifest,
    PublicMessageEvent,
    RoundExtractionEvent,
)
from .fake_api import FakeResponseProvider
from .metrics import episode_metrics
from .policies import SHARED_OPEN_CONVERSATION, policy_text


@dataclass
class AgentState:
    name: str
    role: str
    private_evidence: List[EvidenceItem] = field(default_factory=list)
    private_memory: List[RoundExtractionEvent] = field(default_factory=list)


class OneDayExperiment:
    def __init__(
        self,
        condition: Condition,
        seed: int,
        *,
        target: str = "Tyler",
        player_names: Sequence[str] | None = None,
        turns: int | None = None,
    ) -> None:
        self.condition = condition
        self.seed = seed
        self.rng = random.Random(seed)
        self.target = target
        self.player_names = list(player_names or [
            "Derek", "Scott", "Jacob", "Isaac", "Hayley", "David", "Tyler", "Ginger"
        ])
        if target not in self.player_names:
            raise ValueError(f"Target {target} is not a player.")
        self.turns = turns if turns is not None else min(condition.max_debate_turns, len(self.player_names))
        wolves = {target, "Ginger"} if target != "Ginger" else {target, "Tyler"}
        self.wolves = wolves
        self.agents = {
            name: AgentState(name, "Werewolf" if name in wolves else "Villager")
            for name in self.player_names
        }
        good_names = [name for name in self.player_names if name not in wolves]
        self.evidence = (
            generate_positive_evidence(target, good_names[:3])
            if condition.evidence_mode == "system_full_complementary"
            else []
        )
        if self.evidence:
            validate_evidence(self.evidence, target)
        if self.evidence:
            assignments = assign_complementary_evidence(self.evidence, good_names[:3])
            for name, items in assignments.items():
                self.agents[name].private_evidence = items
        self.messages: List[PublicMessageEvent] = []
        self.belief_snapshots: List[BeliefSnapshotEvent] = []
        self.extractions: List[RoundExtractionEvent] = []
        self.votes: Dict[str, str] = {}
        self.provider = FakeResponseProvider(target)

    @property
    def good_names(self) -> List[str]:
        return [name for name in self.player_names if name not in self.wolves]

    def _message_for(self, name: str, turn: int) -> PublicMessageEvent:
        agent = self.agents[name]
        response = self.provider.debate(
            name=name,
            role=agent.role,
            evidence=agent.private_evidence,
            turn=turn,
            condition=self.condition,
        )
        return PublicMessageEvent(
            event_id=f"r1_t{turn}_{name}",
            round=1,
            turn=turn,
            speaker=name,
            recipients=list(self.player_names),
            dialogue=str(response["say"]),
            evidence_refs=list(response.get("evidence_refs", [])),
            confidence=response.get("confidence"),
            prompt_policy=(
                self.condition.good_policy
                if agent.role != "Werewolf"
                else self.condition.wolf_policy
            ),
            condition_id=self.condition.condition_id,
        )

    def _belief_panel(self, turn: int) -> None:
        """Deterministic fake-model panel used to verify the artifact contract."""
        source_ids = [message.event_id for message in self.messages]
        for index, (name, agent) in enumerate(self.agents.items()):
            others = [candidate for candidate in self.player_names if candidate != name]
            has_private = bool(agent.private_evidence)
            if agent.role != "Werewolf" and has_private:
                top_suspect = self.target
                confidence = 4
            elif agent.role == "Werewolf":
                top_suspect = next(candidate for candidate in self.good_names if candidate != name)
                confidence = 3
            else:
                top_suspect = others[(index + turn - 1) % len(others)]
                confidence = 2
            levels = [
                {
                    "player": candidate,
                    "level": (
                        confidence
                        if candidate == top_suspect
                        else 1 if candidate in self.good_names else 2
                    ),
                }
                for candidate in others
            ]
            evidence_state = (
                "private_only" if has_private and not source_ids
                else "corroborated" if has_private
                else "public_only" if source_ids
                else "none"
            )
            self.belief_snapshots.append(BeliefSnapshotEvent(
                event_id=f"r1_t{turn}_belief_{name}",
                round=1,
                turn=turn,
                player=name,
                living_players=list(self.player_names),
                source_message_ids=list(source_ids),
                bid=(index + turn) % 5,
                speaker_eligible=True,
                top_suspect=top_suspect,
                suspect_confidence_bin=confidence,
                intended_vote=top_suspect,
                evidence_state=evidence_state,
                suspect_levels=levels,
                prompt_policy=(
                    self.condition.wolf_policy
                    if agent.role == "Werewolf"
                    else self.condition.good_policy
                ),
                condition_id=self.condition.condition_id,
            ))
    def _extract_round(self) -> None:
        source_ids = [message.event_id for message in self.messages]
        refs = [ref for message in self.messages for ref in message.evidence_refs]
        for name, agent in self.agents.items():
            response = self.provider.extract(
                name=name,
                source_message_ids=source_ids,
                evidence_refs=refs,
            )
            event = RoundExtractionEvent(
                event_id=f"r1_extract_{name}",
                round=1,
                player=name,
                source_message_ids=list(response["source_message_ids"]),
                extracted_claims=list(response["extracted_claims"]),
                summary=str(response["summary"]),
                confidence=response["confidence"],
                visible_to=[name],
                condition_id=self.condition.condition_id,
            )
            agent.private_memory.append(event)
            self.extractions.append(event)

    def run(self) -> Dict[str, object]:
        for turn in range(1, self.turns + 1):
            self._belief_panel(turn)
            speaker = self.player_names[(turn - 1) % len(self.player_names)]
            message = self._message_for(speaker, turn)
            if set(message.recipients) != set(self.player_names):
                raise AssertionError("Primary experiment must broadcast to every living agent.")
            self.messages.append(message)

        if self.condition.round_extraction:
            self._extract_round()

        options = [name for name in self.player_names]
        for name, agent in self.agents.items():
            vote_options = [option for option in options if option != name]
            self.votes[name] = self.provider.vote(
                name=name,
                role=agent.role,
                condition=self.condition,
                options=vote_options,
            )
        good_votes = [self.votes[name] for name in self.good_names]
        counts = {option: good_votes.count(option) for option in set(good_votes)}
        top = max(counts, key=counts.get) if counts else None
        exiled = top if counts.get(top, 0) > len(self.good_names) / 2 else None
        return {
            "condition": self.condition,
            "manifest": self.manifest().to_dict(),
            "evidence": [item.to_dict() for item in self.evidence],
            "messages": self.messages,
            "belief_snapshots": self.belief_snapshots,
            "extractions": self.extractions,
            "votes": self.votes,
            "exiled": exiled,
            "metrics": episode_metrics(
                messages=self.messages,
                extractions=self.extractions,
                evidence=self.evidence,
                votes=self.votes,
                wolves=self.wolves,
                exiled=exiled,
                available_message_ids={
                    name: {message.event_id for message in self.messages}
                    for name in self.player_names
                },
            ),
        }

    def manifest(self) -> EpisodeManifest:
        return EpisodeManifest(
            condition_id=self.condition.condition_id,
            seed=self.seed,
            role_assignment={name: agent.role for name, agent in self.agents.items()},
            player_names=list(self.player_names),
            evidence_mode=self.condition.evidence_mode,
            good_policy=self.condition.good_policy,
            wolf_policy=self.condition.wolf_policy,
            public_broadcast=True,
            max_debate_turns=self.turns,
            synthetic_votes=self.condition.synthetic_votes,
            round_extraction=self.condition.round_extraction,
            condition_slug=self.condition.condition_slug,
            legacy_condition_id=self.condition.legacy_id,
            good_intervention=self.condition.good_intervention,
            wolf_intervention=self.condition.wolf_intervention,
            evidence_available=self.condition.evidence_available,
        )


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def write_episode(result: Mapping[str, object], output_dir: str | Path) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "manifest.json", result["manifest"])
    _write_json(output / "evidence.json", result["evidence"])
    metrics = dict(result["metrics"])
    metrics.setdefault("episode_status", "completed")
    _write_json(output / "metrics.json", metrics)
    _write_json(output / "game_complete.json", {"votes": result["votes"], "exiled": result["exiled"]})
    with (output / "events.jsonl").open("w", encoding="utf-8") as handle:
        for event in [
            *result["belief_snapshots"],
            *result["messages"],
            *result["extractions"],
        ]:
            handle.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
    (output / "prompts.txt").write_text(
        f"{SHARED_OPEN_CONVERSATION}\n\nGOOD/WOLF POLICY BLOCKS:\n"
        f"{policy_text(result['manifest']['good_policy'])}\n\n"
        f"{policy_text(result['manifest']['wolf_policy'])}\n",
        encoding="utf-8",
    )
    return output


def run_episode(condition_id: str, seed: int, output_dir: str | Path, turns: int | None = None) -> Path:
    experiment = OneDayExperiment(get_condition(condition_id), seed, turns=turns)
    return write_episode(experiment.run(), output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the outcome-aligned one-day fixture.")
    parser.add_argument("--condition", default="+-", choices=condition_cli_aliases())
    parser.add_argument("--seed", type=int, default=1001)
    parser.add_argument("--turns", type=int, default=None)
    parser.add_argument("--output_dir", default="runs")
    args = parser.parse_args()
    output = Path(args.output_dir) / get_condition(args.condition).condition_slug / f"seed_{args.seed}"
    path = run_episode(args.condition, args.seed, output, turns=args.turns)
    print(path)


if __name__ == "__main__":
    main()
