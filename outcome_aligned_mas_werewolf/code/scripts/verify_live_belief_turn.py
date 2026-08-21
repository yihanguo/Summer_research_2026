#!/usr/bin/env python3
"""Verify one real-model belief panel and matching public declaration."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import random
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from experiment.arena_adapter import ExperimentEventSink, configure_players
from experiment.conditions import get_condition
from experiment.evidence import assign_complementary_evidence, generate_positive_evidence
from experiment.model_registry import git_state, get_model_config
from werewolf.game import GameMaster
from werewolf.model import Round, RoundLog, State, WEREWOLF
from werewolf.runner import initialize_players


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="mistral_nemo_12b")
    parser.add_argument("--condition", default="pp")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--base-url", default="http://127.0.0.1:18080/v1")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    os.environ["LOCAL_LLM_BACKEND"] = "vllm"
    os.environ["LOCAL_LLM_BASE_URL"] = args.base_url.rstrip("/")
    os.environ["EXPERIMENT_SEED"] = str(args.seed)
    random.seed(args.seed)
    model_name = f"local:{args.model}"
    model = get_model_config(model_name)
    condition = get_condition(args.condition)

    seer, doctor, villagers, werewolves = initialize_players(
        model_name, model_name
    )
    state = State(
        villagers=villagers,
        werewolves=werewolves,
        seer=seer,
        doctor=doctor,
        session_id=f"live_turn_{args.model}_{condition.condition_slug}_{args.seed}",
    )
    good_players = [
        player for player in state.players.values() if player.role != WEREWOLF
    ]
    evidence = (
        generate_positive_evidence(
            werewolves[0].name,
            [player.name for player in good_players[:3]],
        )
        if condition.evidence_mode == "system_full_complementary"
        else []
    )
    assignments = (
        assign_complementary_evidence(
            evidence, [player.name for player in good_players[:3]]
        )
        if evidence
        else {}
    )
    configure_players(state.players, condition, assignments)
    sink = ExperimentEventSink(condition)
    game = GameMaster(state, num_threads=1, event_sink=sink)
    round_state = Round()
    round_state.players = list(state.players)
    state.rounds.append(round_state)
    game.logs.append(RoundLog())

    speaker = game.get_next_speaker(1)
    dialogue, debate_log = state.players[speaker].debate()
    if not dialogue or not isinstance(debate_log.result, dict):
        raise AssertionError("Selected speaker did not return a public declaration.")

    beliefs = [
        event for event in sink.events if event.event_type == "belief_snapshot"
    ]
    living = set(state.players)
    if {event.player for event in beliefs} != living:
        raise AssertionError("The live belief panel does not cover every player.")
    for event in beliefs:
        expected = living - {event.player}
        observed = {str(item["player"]) for item in event.suspect_levels}
        if observed != expected:
            raise AssertionError(
                f"Suspicion-vector coverage mismatch for {event.player}."
            )
        if event.top_suspect not in expected or event.intended_vote not in expected:
            raise AssertionError(f"Illegal categorical belief for {event.player}.")

    expected_public = {
        str(item["player"]): int(item["level"])
        for item in state.players[speaker].current_belief["suspect_levels"]
    }
    observed_public = {
        str(item["player"]): int(item["level"])
        for item in debate_log.result["public_suspect_levels"]
    }
    if observed_public != expected_public:
        raise AssertionError("The public vector does not match the measured vector.")
    if any(name.lower() not in dialogue.lower() for name in expected_public):
        raise AssertionError("The public statement does not name every rated player.")

    repaired_beliefs = sum(event.structured_repair for event in beliefs)
    summary = {
        "status": "passed",
        "git": git_state(),
        "model_alias": args.model,
        "served_model": model["endpoint_model"],
        "condition_id": condition.condition_id,
        "seed": args.seed,
        "living_players": sorted(living),
        "belief_snapshot_count": len(beliefs),
        "belief_snapshot_repair_count": repaired_beliefs,
        "belief_snapshot_repair_rate": repaired_beliefs / len(beliefs),
        "selected_speaker": speaker,
        "public_declaration_repaired": bool(
            debate_log.metadata.get("structured_repair", False)
        ),
        "complete_public_vector": True,
    }
    output = Path(args.output).resolve()
    write_json(output, summary)
    print(output)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
