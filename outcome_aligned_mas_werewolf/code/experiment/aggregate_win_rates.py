"""Aggregate Villager and Werewolf win rates over a seed range."""

import argparse
import json
from pathlib import Path

from experiment.conditions import get_condition


def summarize(root: Path, conditions: list[str], start_seed: int, end_seed: int):
    rows = []
    expected_seeds = list(range(start_seed, end_seed + 1))
    for short_id in conditions:
        condition_id = get_condition(short_id).legacy_full_id
        winners = {}
        missing = []
        for seed in expected_seeds:
            path = root / condition_id / f"seed_{seed}" / "game_complete.json"
            if not path.exists():
                missing.append(seed)
                continue
            winners[seed] = json.loads(path.read_text(encoding="utf-8"))["winner"]

        villagers = sum(winner == "Villagers" for winner in winners.values())
        werewolves = sum(winner == "Werewolves" for winner in winners.values())
        completed = len(winners)
        rows.append({
            "condition_id": condition_id,
            "seed_start": start_seed,
            "seed_end": end_seed,
            "requested_episodes": len(expected_seeds),
            "completed_episodes": completed,
            "missing_seeds": missing,
            "villager_wins": villagers,
            "werewolf_wins": werewolves,
            "villager_win_rate": villagers / completed if completed else None,
            "werewolf_win_rate": werewolves / completed if completed else None,
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", default="runs_openai")
    parser.add_argument("--conditions", nargs="+", default=["C0", "C1", "C3", "C4"])
    parser.add_argument("--start_seed", type=int, default=1001)
    parser.add_argument("--end_seed", type=int, default=1100)
    parser.add_argument("--output", default="win_rate_summary.json")
    args = parser.parse_args()

    rows = summarize(Path(args.runs), args.conditions, args.start_seed, args.end_seed)
    Path(args.output).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
