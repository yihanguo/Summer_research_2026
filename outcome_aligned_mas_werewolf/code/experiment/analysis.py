"""Aggregate saved episode metrics without depending on pandas."""

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List


def load_metric_files(root: str | Path) -> List[Dict[str, object]]:
    root_path = Path(root)
    records = []
    for path in sorted(root_path.glob("**/metrics.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        manifest_path = path.with_name("manifest.json")
        if manifest_path.exists():
            record["condition_id"] = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )["condition_id"]
        records.append(record)
    return records


def summarize(records: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    grouped = defaultdict(list)
    for record in records:
        grouped[record.get("condition_id", "unknown")].append(record)
    summary = []
    for condition_id, rows in sorted(grouped.items()):
        summary.append({
            "condition_id": condition_id,
            "episodes": len(rows),
            "good_team_win_rate": mean(float(row["good_team_win"]) for row in rows),
            "mean_u_day": mean(float(row["u_day"]) for row in rows),
            "mean_evidence_coverage": mean(float(row["evidence_coverage"]) for row in rows),
            "mean_evidence_correctness": mean(float(row["evidence_correctness"]) for row in rows),
            "mean_anchoring_index": mean(float(row["anchoring_index"]) for row in rows),
            "mean_extraction_coverage": mean(float(row["extraction_coverage"]) for row in rows),
        })
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate outcome-aligned metrics.")
    parser.add_argument("--runs", default="runs")
    parser.add_argument("--output", default="condition_summary.json")
    args = parser.parse_args()
    output = summarize(load_metric_files(args.runs))
    Path(args.output).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
