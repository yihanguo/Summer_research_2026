"""Definition-level verification of the full fake-model condition/seed matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from experiment.conditions import primary_conditions
from experiment.experiment_runner import run_episode
from experiment.model_registry import default_seed_grid
from experiment.temporal_coordination import analyze, write_results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    root = Path(args.output_dir).resolve()
    expected = {
        "pp": ("++", "C3", "full_disclosure", "truth_restricted", True),
        "pm": ("+-", "C1", "full_disclosure", "strategic", True),
        "mp": ("-+", "C4", "baseline", "truth_restricted", True),
        "mm": ("--", "C0", "baseline", "strategic", False),
    }
    completed = []
    for seed in default_seed_grid():
        for condition in primary_conditions():
            output = root / condition.condition_slug / f"seed_{seed}"
            run_episode(condition.condition_slug, seed, output, turns=4)
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            evidence = json.loads((output / "evidence.json").read_text(encoding="utf-8"))
            events = [
                json.loads(line)
                for line in (output / "events.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            signs, legacy, good, wolf, evidence_available = expected[condition.condition_slug]
            assert manifest["condition_id"] == signs
            assert manifest["legacy_condition_id"] == legacy
            assert manifest["good_policy"] == good
            assert manifest["wolf_policy"] == wolf
            assert manifest["evidence_available"] is evidence_available
            assert bool(evidence) is evidence_available
            public = [event for event in events if event["event_type"] == "public_message"]
            beliefs = [event for event in events if event["event_type"] == "belief_snapshot"]
            assert len(public) == 4
            assert len(beliefs) == 4 * len(manifest["player_names"])
            assert all(set(event["recipients"]) == set(manifest["player_names"]) for event in public)
            for turn in range(1, 5):
                panel = [event for event in beliefs if event["turn"] == turn]
                assert {event["player"] for event in panel} == set(manifest["player_names"])
                for event in panel:
                    assert {item["player"] for item in event["suspect_levels"]} == (
                        set(manifest["player_names"]) - {event["player"]}
                    )
            completed.append({"condition_id": signs, "seed": seed, "output": str(output)})

    summary = {
        "status": "passed",
        "conditions": 4,
        "seeds": list(default_seed_grid()),
        "episodes": len(completed),
        "completed": completed,
    }
    (root / "verification_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    coordination = analyze(root, lag=1, permutations=5, seed=20260813)
    assert coordination["complete_episodes_with_belief_panels"] == len(completed)
    assert coordination["cells"]
    assert all(cell["transitions"] > 0 for cell in coordination["cells"])
    write_results(coordination, root / "coordination_analysis")
    print(root / "verification_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
