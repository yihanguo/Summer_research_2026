"""Summarize complete open-model episodes and matched condition contrasts."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Iterable


METRICS = (
    "good_team_win",
    "u_day",
    "evidence_coverage",
    "evidence_correctness",
    "echo_rate",
    "anchoring_index",
    "extraction_coverage",
)


def standard_error(values: list[float]) -> float | None:
    return stdev(values) / math.sqrt(len(values)) if len(values) > 1 else None


def load_complete(root: Path) -> list[dict[str, Any]]:
    records = []
    for manifest_path in sorted(root.glob("**/manifest.json")):
        episode = manifest_path.parent
        required = [episode / "metrics.json", episode / "game_complete.json"]
        if not all(path.exists() for path in required):
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        metrics = json.loads(required[0].read_text(encoding="utf-8"))
        if metrics.get("episode_status") != "completed":
            continue
        model = manifest.get("model_metadata", {}).get("villager", {})
        records.append({
            "model_alias": model.get("alias", "unknown"),
            "model_family": model.get("family", "unknown"),
            "condition_id": manifest["condition_id"],
            "condition_slug": manifest.get("condition_slug", ""),
            "seed": manifest["seed"],
            **{metric: metrics.get(metric) for metric in METRICS},
        })
    return records


def summarize(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[
            (record["model_alias"], record["model_family"], record["condition_id"])
        ].append(record)
    rows = []
    for (alias, family, condition), group in sorted(groups.items()):
        row: dict[str, Any] = {
            "model_alias": alias,
            "model_family": family,
            "condition_id": condition,
            "episodes": len(group),
            "seeds": sorted(record["seed"] for record in group),
        }
        for metric in METRICS:
            values = [float(record[metric]) for record in group if record.get(metric) is not None]
            row[f"{metric}_mean"] = mean(values) if values else None
            row[f"{metric}_se"] = standard_error(values)
        rows.append(row)
    return rows


def paired_contrasts(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    by_cell = {
        (record["model_alias"], record["condition_id"], record["seed"]): record
        for record in records
    }
    aliases = sorted({record["model_alias"] for record in records})
    contrasts = (
        ("good_intervention_when_wolf_plus", "++", "-+", False),
        ("good_intervention_when_wolf_minus", "+-", "--", True),
        ("wolf_intervention_when_good_plus", "++", "+-", False),
        ("wolf_intervention_when_good_minus", "-+", "--", True),
    )
    output = []
    for alias in aliases:
        seeds = sorted({record["seed"] for record in records if record["model_alias"] == alias})
        for name, treatment, control, evidence_confounded in contrasts:
            pairs = [
                (by_cell[(alias, treatment, seed)], by_cell[(alias, control, seed)])
                for seed in seeds
                if (alias, treatment, seed) in by_cell and (alias, control, seed) in by_cell
            ]
            row: dict[str, Any] = {
                "model_alias": alias,
                "contrast": name,
                "treatment": treatment,
                "control": control,
                "paired_seeds": len(pairs),
                "evidence_confounded": evidence_confounded,
            }
            for metric in ("good_team_win", "u_day"):
                differences = [float(left[metric]) - float(right[metric]) for left, right in pairs]
                row[f"{metric}_difference_mean"] = mean(differences) if differences else None
                row[f"{metric}_difference_se"] = standard_error(differences)
            output.append(row)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", required=True)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    root = Path(args.runs).resolve()
    output = Path(args.output_dir).resolve() if args.output_dir else root / "analysis"
    output.mkdir(parents=True, exist_ok=True)
    records = load_complete(root)
    summary = summarize(records)
    contrasts = paired_contrasts(records)
    payload = {
        "complete_episodes": len(records),
        "summary": summary,
        "paired_contrasts": contrasts,
        "design_note": (
            "The contrasts +- minus -- and -+ minus -- are evidence-confounded "
            "because historical C0/-- has no complementary evidence while C1/+- "
            "and C4/-+ do. The other two contrasts hold evidence availability fixed."
        ),
    }
    (output / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if summary:
        with (output / "condition_summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
            writer.writeheader()
            writer.writerows(summary)
    if contrasts:
        with (output / "paired_contrasts.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(contrasts[0]))
            writer.writeheader()
            writer.writerows(contrasts)
    print(output / "summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
