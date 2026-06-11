#!/usr/bin/env python3
"""Print compact ranked literature rows for inspection."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "related_work_matrix.csv"


def main() -> int:
    limit = 30
    if len(sys.argv) > 1:
        try:
            limit = max(1, int(sys.argv[1]))
        except ValueError:
            limit = 30
    with MATRIX.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for idx, row in enumerate(reader, start=1):
            if idx > limit:
                break
            print(
                f"{row['rank']:>4} | {row['year']:<4} | {row['cited_by_count']:>5} | "
                f"{row['title'][:120]} | {row['venue'][:50]}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

