# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
import traceback
from typing import List, Tuple
import itertools
import pandas as pd
import os
import datetime
import json
import uuid
from pathlib import Path

from absl import flags
import tqdm

from werewolf import logging
from werewolf import game
from werewolf.model import Doctor
from werewolf.model import SEER
from werewolf.model import Seer
from werewolf.model import State
from werewolf.model import Villager
from werewolf.model import WEREWOLF
from werewolf.model import Werewolf
from werewolf.config import get_player_names
from experiment.arena_adapter import ExperimentEventSink, configure_players
from experiment.conditions import get_condition
from experiment.evidence import assign_complementary_evidence, generate_positive_evidence
from experiment.events import (
    BeliefSnapshotEvent,
    EpisodeManifest,
    PublicMessageEvent,
    RoundExtractionEvent,
)
from experiment.metrics import episode_metrics
from experiment.model_registry import git_state, model_metadata

_RUN_GAME = flags.DEFINE_boolean("run", False, "Runs a single game.")
_RESUME = flags.DEFINE_boolean("resume", False, "Resumes games.")
_EVAL = flags.DEFINE_boolean("eval", False, "Collect eval data by running many games.")
_NUM_GAMES = flags.DEFINE_integer(
    "num_games", 2, "Number of games to run used with eval."
)
_VILLAGER_MODELS = flags.DEFINE_list(
    "v_models", "", "The model used for villagers values are: flash, pro, gpt4"
)
_WEREWOLF_MODELS = flags.DEFINE_list(
    "w_models", "", "The model used for werewolves values are: flash, pro, gpt4"
)
_ARENA = flags.DEFINE_boolean(
    "arena", False, "Only run games using different models for villagers and werewolves"
)
_THREADS = flags.DEFINE_integer("threads", 2, "Number of threads to run.")
_EXPERIMENT_CONDITION = flags.DEFINE_string(
    "experiment_condition", "", "Run the outcome-aligned condition C0-C4."
)
_EXPERIMENT_SEED = flags.DEFINE_integer(
    "experiment_seed", 0, "Seed for an outcome-aligned Arena episode."
)
_EXPERIMENT_CONFIG = flags.DEFINE_string(
    "experiment_config", "", "Optional JSON experiment configuration path."
)
_OUTPUT_DIR = flags.DEFINE_string(
    "output_dir", "", "Directory for outcome-aligned experiment artifacts."
)
_DISABLE_SYNTHETIC_VOTES = flags.DEFINE_bool(
    "disable_synthetic_votes", False, "Disable votes after intermediate debate turns."
)

DEFAULT_WEREWOLF_MODELS = ["flash", "pro1.5"]
DEFAULT_VILLAGER_MODELS = ["flash", "pro1.5"]
RESUME_DIRECTORIES = []

model_to_id = {
    "pro1.5": "gemini-1.5-pro-preview-0514",
    "flash": "gemini-1.5-flash-001",
    "pro1": "gemini-pro",
    "gpt4": "gpt-4-turbo-2024-04-09",
    "gpt4o": "gpt-4o-2024-05-13",
    "gpt3.5": "gpt-3.5-turbo-0125",
}


def initialize_players(
    villager_model: str, werewolf_model: str
) -> Tuple[Seer, Doctor, List[Villager], List[Werewolf]]:
    """Assigns roles to players and initializes their game view."""

    player_names = get_player_names()
    random.shuffle(player_names)

    seer = Seer(
        name=player_names.pop(),
        model=villager_model,
        # personality="You are cunning.",
    )
    doctor = Doctor(name=player_names.pop(), model=villager_model)
    werewolves = [
        Werewolf(name=player_names.pop(), model=werewolf_model) for _ in range(2)
    ]
    villagers = [Villager(name=name, model=villager_model) for name in player_names]

    # Initialize game view for all players
    for player in [seer, doctor] + werewolves + villagers:
        other_wolf = (
            next((w.name for w in werewolves if w != player), None)
            if isinstance(player, Werewolf)
            else None
        )
        tqdm.tqdm.write(f"{player.name} has role {player.role}")
        player.initialize_game_view(
            current_players=player_names
            + [seer.name, doctor.name]
            + [w.name for w in werewolves],
            round_number=0,
            other_wolf=other_wolf,
        )

    return seer, doctor, villagers, werewolves


def resume_game(directory: str) -> bool:
    state, logs = logging.load_game(directory)

    # remove the failed round and resume from the beginning of that round.
    last_round = state.rounds[-1]
    if not last_round.success:
        state.rounds.pop()
        logs.pop()
    # Reset the error state
    state.error_message = ""

    if not state.rounds:
        werewolves = []
        for p in state.players.values():
            p.initialize_game_view(
                round_number=0,
                current_players=list(state.players.keys()),
            )
            p.observations = []

            if p.role == WEREWOLF:
                werewolves.append(p)

            if p.role == SEER:
                p.previously_unmasked = {}

        if len(werewolves) == 2:
            werewolves[0].gamestate.other_wolf = werewolves[1].name
            werewolves[1].gamestate.other_wolf = werewolves[0].name
    else:
        # Update the GameView for every active player
        werewolves = []
        for p in state.rounds[-1].players:
            player = state.players.get(p, None)
            if player:
                player.initialize_game_view(
                    round_number=len(state.rounds),
                    current_players=state.rounds[-1].players[:],
                )

                # Remove the observation from the failed round for all active players
                failed_round = len(state.rounds)
                player.observations = [
                    o
                    for o in player.observations
                    if not o.startswith(f"Round {failed_round}")
                ]

                if player.role == WEREWOLF:
                    werewolves.append(player)

                # update the seer's unmasking history
                unmasking_history = {}
                if player.role == SEER:
                    for r in state.rounds:
                        if r.unmasked:
                            unmasked_player = state.players.get(r.unmasked, None)
                            if unmasked_player:
                                unmasking_history[r.unmasked] = unmasked_player.role
                    player.previously_unmasked = unmasking_history

        if len(werewolves) == 2:
            werewolves[0].gamestate.other_wolf = werewolves[1].name
            werewolves[1].gamestate.other_wolf = werewolves[0].name

    gm = game.GameMaster(state, num_threads=_THREADS.value)
    gm.logs = logs
    try:
        gm.run_game()
    except Exception as e:
        state.error_message = traceback.format_exc()
    logging.save_game(state, gm.logs, directory)
    return not state.error_message


def resume_games(directories: list[str]):
    successful_resumes = []
    failed_resumes = []
    invalid_resumes = []
    for i in tqdm.tqdm(range(len(directories)), desc="Games"):
        d = directories[i]
        try:
            success = resume_game(d)
            if success:
                successful_resumes.append(d)
            else:
                failed_resumes.append(d)
        except Exception as e:
            if "not found" in str(e):
                invalid_resumes.append(d)
            print(f"Error encountered during resume: {e}")

    print(
        f"Successful resumes: {successful_resumes}.\nFailed resumes:"
        f" {failed_resumes}\nInvalid resumes(no partial game found):"
        f" {invalid_resumes}"
    )


def run_experiment_game(
    werewolf_model: str,
    villager_model: str,
    condition_id: str,
    seed: int,
    output_dir: str | None = None,
    disable_synthetic_votes: bool = True,
    config_path: str | None = None,
) -> Tuple[str, str]:
    """Run a real Arena game with the outcome-aligned instrumentation."""
    random.seed(seed)
    condition = get_condition(condition_id)
    config = {}
    if config_path:
        with open(config_path, "r", encoding="utf-8") as handle:
            config = json.load(handle)
    actual_max_debate_turns = int(
        config.get("max_debate_turns", condition.max_debate_turns)
    )

    seer, doctor, villagers, werewolves = initialize_players(
        villager_model, werewolf_model
    )
    session_id = f"experiment_{condition_id}_{seed}_{uuid.uuid4().hex[:8]}"
    state = State(
        villagers=villagers,
        werewolves=werewolves,
        seer=seer,
        doctor=doctor,
        session_id=session_id,
    )

    good_players = [player for player in state.players.values() if player.role != WEREWOLF]
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
        if condition.evidence_mode == "system_full_complementary"
        else {}
    )
    configure_players(
        state.players,
        condition,
        assignments,
        max_debate_turns=actual_max_debate_turns,
    )
    sink = ExperimentEventSink(condition)
    gamemaster = game.GameMaster(
        state,
        num_threads=_THREADS.value,
        event_sink=sink,
        run_synthetic_votes=not disable_synthetic_votes,
        max_debate_turns=actual_max_debate_turns,
    )
    winner = ""
    try:
        winner = gamemaster.run_game()
    except Exception:
        state.error_message = traceback.format_exc()
        print(f"Error encountered during experiment game: {state.error_message}")

    if output_dir:
        if villager_model.startswith("local:"):
            model_alias = model_metadata(villager_model)["alias"]
            episode_dir = (
                Path(output_dir)
                / str(model_alias)
                / condition.condition_slug
                / f"seed_{seed}"
            )
        else:
            episode_dir = (
                Path(output_dir) / condition.legacy_full_id / f"seed_{seed}"
            )
    else:
        episode_dir = Path(logging.log_directory())
    episode_dir.mkdir(parents=True, exist_ok=True)
    logging.save_game(state, gamemaster.logs, str(episode_dir))
    sink.write_jsonl(episode_dir / "events.jsonl")
    (episode_dir / "evidence.json").write_text(
        json.dumps([item.to_dict() for item in evidence], indent=2),
        encoding="utf-8",
    )
    messages = [event for event in sink.events if isinstance(event, PublicMessageEvent)]
    extractions = [
        event for event in sink.events if isinstance(event, RoundExtractionEvent)
    ]
    beliefs = [
        event for event in sink.events if isinstance(event, BeliefSnapshotEvent)
    ]
    available_message_ids = {}
    for message in messages:
        for recipient in message.recipients:
            available_message_ids.setdefault(recipient, set()).add(message.event_id)

    day_votes = [round_state.votes[-1] for round_state in state.rounds if round_state.votes]
    final_votes = day_votes[-1] if day_votes else {}
    day_exiles = [round_state.exiled for round_state in state.rounds if round_state.exiled]
    final_exile = day_exiles[-1] if day_exiles else None
    wolf_names = {wolf.name for wolf in state.werewolves}
    metrics = episode_metrics(
        messages=messages,
        extractions=extractions,
        evidence=evidence,
        votes=final_votes,
        wolves=wolf_names,
        exiled=final_exile,
        available_message_ids=available_message_ids,
    )
    metrics.update({
        "episode_status": "completed" if not state.error_message else "failed",
        "game_winner": state.winner,
        "days_played": len(state.rounds),
        "day_exiles": day_exiles,
        "wolf_exile_count": sum(exile in wolf_names for exile in day_exiles),
        "good_exile_count": sum(exile not in wolf_names for exile in day_exiles),
        "final_exile": final_exile,
        "belief_snapshot_count": len(beliefs),
        "belief_snapshot_repair_count": sum(
            event.structured_repair for event in beliefs
        ),
        "belief_snapshot_repair_rate": (
            sum(event.structured_repair for event in beliefs) / len(beliefs)
            if beliefs else 0.0
        ),
        "public_message_repair_count": sum(
            message.structured_repair for message in messages
        ),
        "public_message_repair_rate": (
            sum(message.structured_repair for message in messages) / len(messages)
            if messages else 0.0
        ),
    })
    metrics["good_team_win"] = int(state.winner == "Villagers")
    (episode_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    repository_state = git_state()
    manifest = EpisodeManifest(
        condition_id=condition.condition_id,
        seed=seed,
        role_assignment={name: player.role for name, player in state.players.items()},
        player_names=list(state.players),
        evidence_mode=condition.evidence_mode,
        good_policy=condition.good_policy,
        wolf_policy=condition.wolf_policy,
        public_broadcast=True,
        max_debate_turns=actual_max_debate_turns,
        synthetic_votes=not disable_synthetic_votes,
        round_extraction=True,
        model_ids={"villager": villager_model, "werewolf": werewolf_model},
        condition_slug=condition.condition_slug,
        legacy_condition_id=condition.legacy_id,
        good_intervention=condition.good_intervention,
        wolf_intervention=condition.wolf_intervention,
        evidence_available=condition.evidence_available,
        model_metadata={
            "villager": model_metadata(villager_model),
            "werewolf": model_metadata(werewolf_model),
        },
        generation_parameters={
            "experiment_seed": seed,
            "threads": _THREADS.value,
            "max_debate_turns": actual_max_debate_turns,
            "synthetic_votes": not disable_synthetic_votes,
        },
        git_commit=repository_state["commit"],
        git_dirty=repository_state["dirty"],
    )
    (episode_dir / "manifest.json").write_text(
        json.dumps(manifest.to_dict(), indent=2), encoding="utf-8"
    )
    print(f"Experiment artifacts saved to: {episode_dir}")
    return winner, str(episode_dir)


def run_game(
    werewolf_model: str,
    villager_model: str,
) -> Tuple[str, str]:
    """Runs a single game of Werewolf.

    Returns: (winner, log_dir)
    """
    seer, doctor, villagers, werewolves = initialize_players(
        villager_model, werewolf_model
    )
    session_id = "10"  # You might want to make this unique per game
    state = State(
        villagers=villagers,
        werewolves=werewolves,
        seer=seer,
        doctor=doctor,
        session_id=session_id,
    )

    gamemaster = game.GameMaster(state, num_threads=_THREADS.value)
    winner = None
    try:
        winner = gamemaster.run_game()
    except Exception as e:
        state.error_message = traceback.format_exc()
        print(f"Error encountered during game: {e}")

    log_directory = logging.log_directory()
    logging.save_game(state, gamemaster.logs, log_directory)
    print(f"Game logs saved to: {log_directory}")

    return winner, log_directory


def run() -> None:
    villager_models = _VILLAGER_MODELS.value or DEFAULT_VILLAGER_MODELS
    werewolf_models = _WEREWOLF_MODELS.value or DEFAULT_WEREWOLF_MODELS
    v_ids = [model_to_id.get(m, m) for m in villager_models]
    w_ids = [model_to_id.get(m, m) for m in werewolf_models]
    model_combinations = list(itertools.product(v_ids, w_ids))
    if _RUN_GAME.value:
        villager_model, werewolf_model = model_combinations[0]
        print(f"Villagers: {villager_model} versus Werwolves:  {werewolf_model}")
        if _EXPERIMENT_CONDITION.value:
            run_experiment_game(
                werewolf_model=werewolf_model,
                villager_model=villager_model,
                condition_id=_EXPERIMENT_CONDITION.value,
                seed=_EXPERIMENT_SEED.value,
                output_dir=_OUTPUT_DIR.value or None,
                disable_synthetic_votes=_DISABLE_SYNTHETIC_VOTES.value,
                config_path=_EXPERIMENT_CONFIG.value or None,
            )
        else:
            run_game(
                werewolf_model=werewolf_model,
                villager_model=villager_model,
            )
    elif _EVAL.value:
        results = []
        for villager_model, werewolf_model in model_combinations:
            # only run games using different models in the arena mode
            if villager_model == werewolf_model and _ARENA.value:
                continue
            print(
                f"Running games with Villagers: {villager_model} and"
                f" Werewolves:{werewolf_model}"
            )
            for _ in tqdm.tqdm(range(_NUM_GAMES.value), desc="Games"):
                winner, log_dir = run_game(
                    werewolf_model=werewolf_model,
                    villager_model=villager_model,
                )
                results.append([villager_model, werewolf_model, winner, log_dir])

        df = pd.DataFrame(
            results, columns=["VillagerModel", "WerewolfModel", "Winner", "Log"]
        )
        print("######## Eval results ########")
        print(df)

        pacific_timezone = datetime.timezone(datetime.timedelta(hours=-8))
        timestamp = datetime.datetime.now(pacific_timezone).strftime("%Y%m%d_%H%M%S")
        csv_file = f"{os.getcwd()}/logs/eval_results_{timestamp}.csv"
        df.to_csv(csv_file)
        print(f"Wrote eval results to {csv_file}")

    elif _RESUME.value:
        resume_games(RESUME_DIRECTORIES)
