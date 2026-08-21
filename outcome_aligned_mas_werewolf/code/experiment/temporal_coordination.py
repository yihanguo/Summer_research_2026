"""Temporal information-theoretic coordination from belief snapshots.

This module implements the two quantities used in the Emergent Coordination
reference setting, adapted only in the definition of the task-native state:

* Williams--Beer two-source PID with I_min redundancy, applied to the future
  joint state of an agent pair.
* The macro criterion S_macro(l) = I(V_t; V_{t+l}) - sum_k I(X_k,t; V_{t+l}).

Hidden Werewolf roles are used only to define an offline good-agent coalition.
They are never components of X or V.  All estimates are categorical plugin
estimates in bits and should be interpreted together with sample size and the
temporal-permutation null.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path
import random
from statistics import mean, median
from typing import Any, Dict, Iterable, Mapping, Sequence


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return tuple(sorted((str(key), freeze(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    if isinstance(value, set):
        return tuple(sorted(freeze(item) for item in value))
    return value


def mutual_information(samples: Iterable[tuple[Any, Any]]) -> float:
    """Categorical plugin estimate of I(X;Y), in bits."""
    usable = [(freeze(x), freeze(y)) for x, y in samples if x is not None and y is not None]
    if not usable:
        return 0.0
    joint = Counter(usable)
    count_x = Counter(x for x, _ in usable)
    count_y = Counter(y for _, y in usable)
    total = len(usable)
    result = 0.0
    for (x, y), count in joint.items():
        result += (count / total) * math.log2(
            (count * total) / (count_x[x] * count_y[y])
        )
    return max(0.0, result)


def _specific_information(samples: Sequence[tuple[Any, Any]], target_value: Any) -> float:
    """I(Y=y;X) = sum_x p(x|y) log[p(y|x)/p(y)]."""
    pairs = [(freeze(x), freeze(y)) for x, y in samples]
    total = len(pairs)
    target_count = sum(y == target_value for _, y in pairs)
    if not total or not target_count:
        return 0.0
    count_x = Counter(x for x, _ in pairs)
    count_xy = Counter(pairs)
    value = 0.0
    for x, y in pairs:
        if y != target_value:
            continue
        p_x_given_y = count_xy[(x, y)] / target_count
        p_y_given_x = count_xy[(x, y)] / count_x[x]
        p_y = target_count / total
        # Iterate once per unique x rather than once per observation.
        value += (p_x_given_y / count_xy[(x, y)]) * math.log2(p_y_given_x / p_y)
    return max(0.0, value)


def williams_beer_pid(samples: Iterable[tuple[Any, Any, Any]]) -> Dict[str, float | int]:
    """Williams--Beer I_min PID for two categorical sources and one target."""
    triples = [
        (freeze(x_i), freeze(x_j), freeze(target))
        for x_i, x_j, target in samples
        if x_i is not None and x_j is not None and target is not None
    ]
    if not triples:
        return {
            "unique_i_bits": 0.0,
            "unique_j_bits": 0.0,
            "redundancy_bits": 0.0,
            "synergy_bits": 0.0,
            "joint_information_bits": 0.0,
            "individual_i_bits": 0.0,
            "individual_j_bits": 0.0,
            "samples": 0,
        }
    source_i = [(x_i, target) for x_i, _, target in triples]
    source_j = [(x_j, target) for _, x_j, target in triples]
    i_i = mutual_information(source_i)
    i_j = mutual_information(source_j)
    i_joint = mutual_information([((x_i, x_j), target) for x_i, x_j, target in triples])
    target_counts = Counter(target for _, _, target in triples)
    redundancy = 0.0
    for target, count in target_counts.items():
        redundancy += (count / len(triples)) * min(
            _specific_information(source_i, target),
            _specific_information(source_j, target),
        )
    synergy = i_joint - i_i - i_j + redundancy
    return {
        "unique_i_bits": max(0.0, i_i - redundancy),
        "unique_j_bits": max(0.0, i_j - redundancy),
        "redundancy_bits": max(0.0, redundancy),
        "synergy_bits": max(0.0, synergy),
        "joint_information_bits": i_joint,
        "individual_i_bits": i_i,
        "individual_j_bits": i_j,
        "samples": len(triples),
    }


def agent_state(event: Mapping[str, Any]) -> tuple[Any, ...]:
    """Task-native X_i,t built solely from the model's reported belief."""
    levels = tuple(
        sorted(
            (str(item["player"]), int(item["level"]))
            for item in event.get("suspect_levels", [])
        )
    )
    return (
        int(event.get("bid", 0)),
        str(event.get("top_suspect", "")),
        int(event.get("suspect_confidence_bin", 0)),
        str(event.get("intended_vote", "")),
        str(event.get("evidence_state", "none")),
        levels,
    )


def macro_state(
    panel: Mapping[str, Mapping[str, Any]],
    coalition: Sequence[str],
) -> tuple[Any, ...] | None:
    """Task-native V_t: identities plus group suspicion consensus.

    The alive tuple records stable player identities, not hidden roles.  Each
    living candidate also receives the median 0--4 suspicion level assigned by
    the coalition. The final consensus bin is 1 when a strict majority shares
    the modal top suspect and 0 otherwise. Thus V is a deterministic, richer
    compression of all reported X states, not an outcome or role label.
    """
    members = [name for name in coalition if name in panel]
    if not members:
        return None
    living = tuple(sorted(str(name) for name in next(iter(panel.values()))["living_players"]))
    candidate_consensus = []
    for candidate in living:
        ratings = []
        for source in members:
            ratings.extend(
                int(item["level"])
                for item in panel[source].get("suspect_levels", [])
                if item["player"] == candidate
            )
        candidate_consensus.append((candidate, median(ratings) if ratings else None))
    top_counts = Counter(str(panel[name]["top_suspect"]) for name in members)
    group_top, agreement = sorted(
        top_counts.items(), key=lambda item: (-item[1], item[0])
    )[0]
    consensus_bin = int(agreement / len(members) > 0.5)
    return (living, tuple(candidate_consensus), group_top, consensus_bin)


def validate_panel(panel: Mapping[str, Mapping[str, Any]]) -> None:
    if not panel:
        raise ValueError("A belief panel cannot be empty.")
    living_sets = {tuple(sorted(event["living_players"])) for event in panel.values()}
    if len(living_sets) != 1:
        raise ValueError("Belief events in one panel disagree about living players.")
    living = set(next(iter(living_sets)))
    if set(panel) != living:
        raise ValueError(f"Panel coverage mismatch: expected {sorted(living)}, got {sorted(panel)}")
    for player, event in panel.items():
        expected = living - {player}
        observed = [str(item["player"]) for item in event.get("suspect_levels", [])]
        if len(observed) != len(set(observed)) or set(observed) != expected:
            raise ValueError(f"Suspicion-vector coverage mismatch for {player}.")


def _episode_transitions(
    events: Sequence[Mapping[str, Any]],
    roles: Mapping[str, str],
    lag: int,
    coalition_mode: str,
    *,
    include_repaired: bool = False,
) -> list[Dict[str, Any]]:
    by_time: Dict[tuple[int, int], Dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for event in events:
        if event.get("event_type") == "belief_snapshot":
            by_time[(int(event["round"]), int(event["turn"]))][str(event["player"])] = event
    for panel in by_time.values():
        validate_panel(panel)
    transitions = []
    for (round_number, turn), panel_t in sorted(by_time.items()):
        panel_future = by_time.get((round_number, turn + lag))
        if not panel_future:
            continue
        common = sorted(set(panel_t) & set(panel_future))
        if coalition_mode == "good":
            coalition = [name for name in common if roles.get(name) != "Werewolf"]
        elif coalition_mode == "all":
            coalition = common
        else:
            raise ValueError(f"Unknown coalition mode: {coalition_mode}")
        if len(coalition) < 2:
            continue
        if not include_repaired and any(
            bool(panel_t[name].get("structured_repair", False))
            or bool(panel_future[name].get("structured_repair", False))
            for name in coalition
        ):
            continue
        transitions.append({
            "round": round_number,
            "turn": turn,
            "coalition": coalition,
            "current": {name: agent_state(panel_t[name]) for name in coalition},
            "future": {name: agent_state(panel_future[name]) for name in coalition},
            "macro_current": macro_state(panel_t, coalition),
            "macro_future": macro_state(panel_future, coalition),
        })
    return transitions


def _pairwise_pid(transitions: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    rows_by_pair: Dict[tuple[str, str], list[tuple[Any, Any, Any]]] = defaultdict(list)
    for transition in transitions:
        coalition = list(transition["coalition"])
        for index, source_i in enumerate(coalition):
            for source_j in coalition[index + 1 :]:
                rows_by_pair[(source_i, source_j)].append((
                    transition["current"][source_i],
                    transition["current"][source_j],
                    (transition["future"][source_i], transition["future"][source_j]),
                ))
    pairs = {
        f"{source_i}|{source_j}": williams_beer_pid(rows)
        for (source_i, source_j), rows in sorted(rows_by_pair.items())
    }
    values = [float(result["synergy_bits"]) for result in pairs.values()]
    return {
        "median_synergy_bits": median(values) if values else 0.0,
        "mean_synergy_bits": mean(values) if values else 0.0,
        "pair_count": len(values),
        "pairs": pairs,
    }


def _macro_criterion(transitions: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    macro_information = mutual_information(
        (transition["macro_current"], transition["macro_future"])
        for transition in transitions
    )
    sources = sorted({name for transition in transitions for name in transition["coalition"]})
    individual = {
        source: mutual_information(
            (transition["current"].get(source), transition["macro_future"])
            for transition in transitions
            if source in transition["current"]
        )
        for source in sources
    }
    return {
        "macro_predictive_information_bits": macro_information,
        "individual_information_bits": individual,
        "sum_individual_information_bits": sum(individual.values()),
        "s_macro_bits": macro_information - sum(individual.values()),
        "samples": len(transitions),
    }


def _null_distribution(
    transitions: Sequence[Mapping[str, Any]],
    permutations: int,
    seed: int,
) -> Dict[str, Any]:
    observed_pair = _pairwise_pid(transitions)["median_synergy_bits"]
    observed_macro = _macro_criterion(transitions)["s_macro_bits"]
    if not transitions or permutations <= 0:
        return {"permutations": 0}
    rng = random.Random(seed)
    pair_null = []
    macro_null = []
    for _ in range(permutations):
        future = [
            (transition["future"], transition["macro_future"])
            for transition in transitions
        ]
        rng.shuffle(future)
        permuted = []
        for transition, (future_agents, future_macro) in zip(transitions, future):
            common = [name for name in transition["coalition"] if name in future_agents]
            if len(common) < 2:
                continue
            copied = dict(transition)
            copied["coalition"] = common
            copied["future"] = future_agents
            copied["macro_future"] = future_macro
            permuted.append(copied)
        pair_null.append(float(_pairwise_pid(permuted)["median_synergy_bits"]))
        macro_null.append(float(_macro_criterion(permuted)["s_macro_bits"]))
    return {
        "permutations": permutations,
        "pairwise_synergy_null_mean_bits": mean(pair_null),
        "pairwise_synergy_null_median_bits": median(pair_null),
        "pairwise_synergy_null_corrected_bits": observed_pair - mean(pair_null),
        "pairwise_synergy_p_ge_observed": (
            1 + sum(value >= observed_pair for value in pair_null)
        ) / (permutations + 1),
        "macro_null_mean_bits": mean(macro_null),
        "macro_null_median_bits": median(macro_null),
        "macro_null_corrected_bits": observed_macro - mean(macro_null),
        "macro_p_ge_observed": (
            1 + sum(value >= observed_macro for value in macro_null)
        ) / (permutations + 1),
    }


def load_complete_episodes(root: Path) -> list[Dict[str, Any]]:
    episodes = []
    for manifest_path in sorted(root.glob("**/manifest.json")):
        directory = manifest_path.parent
        events_path = directory / "events.jsonl"
        metrics_path = directory / "metrics.json"
        if not events_path.exists() or not metrics_path.exists():
            continue
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        if metrics.get("episode_status") != "completed":
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        events = [
            json.loads(line)
            for line in events_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if not any(event.get("event_type") == "belief_snapshot" for event in events):
            continue
        model = manifest.get("model_metadata", {}).get("villager", {})
        episodes.append({
            "directory": str(directory),
            "model_alias": model.get("alias", "unknown"),
            "model_family": model.get("family", "unknown"),
            "condition_id": manifest["condition_id"],
            "seed": int(manifest["seed"]),
            "roles": manifest["role_assignment"],
            "events": events,
        })
    return episodes


def analyze(
    root: Path,
    *,
    lag: int = 1,
    permutations: int = 100,
    seed: int = 20260813,
) -> Dict[str, Any]:
    episodes = load_complete_episodes(root)
    grouped: Dict[tuple[str, str, str], list[Dict[str, Any]]] = defaultdict(list)
    for episode in episodes:
        grouped[(episode["model_alias"], episode["model_family"], episode["condition_id"])].append(episode)
    cells = []
    for (alias, family, condition), cell_episodes in sorted(grouped.items()):
        for coalition_mode in ("good", "all"):
            transitions = []
            transitions_including_repairs = []
            for episode in cell_episodes:
                transitions.extend(
                    _episode_transitions(
                        episode["events"], episode["roles"], lag, coalition_mode
                    )
                )
                transitions_including_repairs.extend(
                    _episode_transitions(
                        episode["events"], episode["roles"], lag, coalition_mode,
                        include_repaired=True,
                    )
                )
            pairwise = _pairwise_pid(transitions)
            macro = _macro_criterion(transitions)
            null = _null_distribution(
                transitions,
                permutations,
                seed + sum(ord(char) for char in f"{alias}{condition}{coalition_mode}"),
            )
            cells.append({
                "model_alias": alias,
                "model_family": family,
                "condition_id": condition,
                "coalition": coalition_mode,
                "episodes": len(cell_episodes),
                "seeds": sorted(episode["seed"] for episode in cell_episodes),
                "lag": lag,
                "transitions": len(transitions),
                "transitions_including_repairs": len(transitions_including_repairs),
                "repair_excluded_transitions": (
                    len(transitions_including_repairs) - len(transitions)
                ),
                "pairwise_pid": pairwise,
                "macro_criterion": macro,
                "temporal_null": null,
            })
    return {
        "estimator": "Williams-Beer I_min PID and exact macro information contrast",
        "state_definition": {
            "agent": [
                "bid", "top_suspect", "suspect_confidence_bin", "intended_vote",
                "evidence_state", "complete_suspect_levels",
            ],
            "macro": [
                "living_player_identities", "per_candidate_median_suspicion_level",
                "group_top_suspect", "majority_consensus_bin",
            ],
            "hidden_roles_in_state": False,
            "good_coalition_note": "Roles select the offline coalition only; roles are not state variables.",
            "repair_handling": (
                "Primary PID and macro estimates exclude transitions where any "
                "coalition source was deterministically repaired at t or t+lag."
            ),
        },
        "complete_episodes_with_belief_panels": len(episodes),
        "lag": lag,
        "permutations": permutations,
        "cells": cells,
    }


def write_results(payload: Mapping[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "temporal_coordination.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    rows = []
    for cell in payload["cells"]:
        pairwise = cell["pairwise_pid"]
        macro = cell["macro_criterion"]
        null = cell["temporal_null"]
        rows.append({
            "model_alias": cell["model_alias"],
            "model_family": cell["model_family"],
            "condition_id": cell["condition_id"],
            "coalition": cell["coalition"],
            "episodes": cell["episodes"],
            "transitions": cell["transitions"],
            "repair_excluded_transitions": cell["repair_excluded_transitions"],
            "pair_count": pairwise["pair_count"],
            "median_pairwise_synergy_bits": pairwise["median_synergy_bits"],
            "null_corrected_pairwise_synergy_bits": null.get("pairwise_synergy_null_corrected_bits"),
            "pairwise_synergy_p": null.get("pairwise_synergy_p_ge_observed"),
            "s_macro_bits": macro["s_macro_bits"],
            "null_corrected_s_macro_bits": null.get("macro_null_corrected_bits"),
            "s_macro_p": null.get("macro_p_ge_observed"),
        })
    if rows:
        with (output / "temporal_coordination.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    lines = [
        "# Temporal coordination analysis",
        "",
        f"Completed episodes with full belief panels: {payload['complete_episodes_with_belief_panels']}",
        f"Lag: {payload['lag']} turn; temporal null permutations: {payload['permutations']}.",
        "",
        "The primary `good` coalition uses hidden roles only to select sources offline. Hidden roles are not included in either the agent state or macrostate.",
        "",
        "| Model | Condition | Coalition | Episodes | Valid transitions | Repair-excluded | Median PID synergy | Null-corrected synergy | S_macro | Null-corrected S_macro |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    def display_bits(value: Any) -> str:
        return "NA" if value is None else f"{float(value):.4f}"

    for row in rows:
        lines.append(
            f"| {row['model_alias']} | {row['condition_id']} | "
            f"{row['coalition']} | {row['episodes']} | {row['transitions']} | "
            f"{row['repair_excluded_transitions']} | "
            f"{display_bits(row['median_pairwise_synergy_bits'])} | "
            f"{display_bits(row['null_corrected_pairwise_synergy_bits'])} | "
            f"{display_bits(row['s_macro_bits'])} | "
            f"{display_bits(row['null_corrected_s_macro_bits'])} |"
        )
    (output / "temporal_coordination.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
