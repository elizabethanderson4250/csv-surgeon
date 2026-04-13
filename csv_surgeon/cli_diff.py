"""CLI sub-command: diff — compare two CSV files by a key column."""

import argparse
import csv
import json
import sys
from pathlib import Path

from csv_surgeon.diff import diff_rows


def add_diff_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("diff", help="Diff two CSV files by a key column")
    p.add_argument("left", help="Path to the original (left) CSV file")
    p.add_argument("right", help="Path to the modified (right) CSV file")
    p.add_argument("--key", required=True, help="Column name to use as the row key")
    p.add_argument(
        "--columns",
        nargs="+",
        default=None,
        help="Limit comparison to these columns (default: all)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )


def _read_rows(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def run_diff(args: argparse.Namespace) -> None:
    left_rows = _read_rows(args.left)
    right_rows = _read_rows(args.right)

    added, removed, changed = diff_rows(
        iter(left_rows),
        iter(right_rows),
        key=args.key,
        columns=args.columns,
    )

    if args.format == "json":
        output = {"added": added, "removed": removed, "changed": changed}
        print(json.dumps(output, indent=2))
    else:
        if added:
            print(f"ADDED ({len(added)} rows):")
            for row in added:
                print(f"  + {row}")
        if removed:
            print(f"REMOVED ({len(removed)} rows):")
            for row in removed:
                print(f"  - {row}")
        if changed:
            print(f"CHANGED ({len(changed)} rows):")
            for entry in changed:
                print(f"  ~ key={entry['key']}  before={entry['before']}  after={entry['after']}")
        if not added and not removed and not changed:
            print("No differences found.")
