from __future__ import annotations

import argparse
import csv
from pathlib import Path
from sys import exit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the aggregated Locust 95th percentile latency."
    )
    parser.add_argument("stats_csv", type=Path)
    parser.add_argument("--max-p95", type=float, default=200.0)
    return parser.parse_args()


def read_aggregated_p95(stats_csv: Path) -> float:
    with stats_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("Name") == "Aggregated" or row.get("Type") == "Aggregated":
                return float(row["95%"])

    raise ValueError("Aggregated row not found in Locust stats CSV")


def main() -> None:
    args = parse_args()
    p95 = read_aggregated_p95(args.stats_csv)
    print(f"Aggregated P95: {p95:.2f} ms")

    if p95 >= args.max_p95:
        print(f"P95 must be below {args.max_p95:.2f} ms")
        exit(1)


if __name__ == "__main__":
    main()
