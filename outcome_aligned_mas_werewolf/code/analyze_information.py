"""Command-line entry point for the completed-game information analysis."""

import argparse
from pathlib import Path

from experiment.information_analysis import run_analysis


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze completed Werewolf Arena games with positive-channel information metrics."
    )
    parser.add_argument(
        "--runs",
        nargs="+",
        default=["runs_openai"],
        help="One or more saved-run roots.",
    )
    parser.add_argument(
        "--output",
        default="analysis/roundwise_information",
        help="Output directory for JSONL, JSON, and Markdown artifacts.",
    )
    args = parser.parse_args()
    result = run_analysis(args.runs, Path(args.output))
    print(f"Completed episodes: {result['completed_episodes']}")
    print(f"Claim records: {result['claim_records']}")
    print(f"Information rows: {result['information_rows']}")
    print(Path(args.output) / "information_report.md")


if __name__ == "__main__":
    main()
