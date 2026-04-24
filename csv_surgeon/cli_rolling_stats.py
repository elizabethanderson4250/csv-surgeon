"""CLI sub-command for cumulative / rolling statistics."""
from __future__ import annotations

import argparse
import csv
import sys

from csv_surgeon.rolling_stats import (
    cumulative_max,
    cumulative_mean,
    cumulative_min,
    cumulative_sum,
)

_FUNCS = {
    "sum": cumulative_sum,
    "mean": cumulative_mean,
    "max": cumulative_max,
    "min": cumulative_min,
}


def add_rolling_stats_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "rolling-stats",
        help="Append a cumulative statistic column (sum/mean/max/min) to each row.",
    )
    p.add_argument("input", help="Input CSV file (use - for stdin)")
    p.add_argument("output", help="Output CSV file (use - for stdout)")
    p.add_argument("--column", required=True, help="Source numeric column")
    p.add_argument(
        "--func",
        choices=list(_FUNCS),
        default="sum",
        help="Cumulative function to apply (default: sum)",
    )
    p.add_argument("--output-column", default="", help="Name for the new column")
    p.add_argument(
        "--default", default="", help="Value to emit when source is non-numeric"
    )
    p.set_defaults(handler=run_rolling_stats)


def run_rolling_stats(args: argparse.Namespace) -> None:
    in_fh = open(args.input, newline="") if args.input != "-" else sys.stdin
    out_fh = open(args.output, "w", newline="") if args.output != "-" else sys.stdout

    try:
        reader = csv.DictReader(in_fh)
        rows = list(reader)
        if not rows:
            return

        func = _FUNCS[args.func]
        result_rows = list(
            func(
                rows,
                column=args.column,
                output_column=args.output_column,
                default=args.default,
            )
        )

        fieldnames = list(result_rows[0].keys()) if result_rows else []
        writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result_rows)
    finally:
        if args.input != "-":
            in_fh.close()
        if args.output != "-":
            out_fh.close()
