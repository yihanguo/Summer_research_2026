"""Analyze saved belief panels with temporal PID and the macro criterion."""

import argparse
from pathlib import Path

from experiment.temporal_coordination import analyze, write_results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--lag", type=int, default=1)
    parser.add_argument("--permutations", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260813)
    args = parser.parse_args()
    root = Path(args.runs).resolve()
    output = Path(args.output_dir).resolve() if args.output_dir else root / "analysis"
    payload = analyze(
        root, lag=args.lag, permutations=args.permutations, seed=args.seed
    )
    write_results(payload, output)
    print(output / "temporal_coordination.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
