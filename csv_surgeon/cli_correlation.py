"""CLI sub-command: correlate — compute Pearson correlation between columns."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import Sequence

from csv_surgeon.correlation import correlate_columns, correlation_matrix


def add_correlation_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "correlate",
        help="Compute Pearson correlation between numeric columns.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument(
        "--cols",
        required=True,
        help="Comma-separated list of column names to correlate.",
    )
    p.add_argument(
        "--pair",
        nargs=2,
        metavar=("COL_A", "COL_B"),
        help="Compute correlation for exactly this pair instead of a full matrix.",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write results to this CSV file (default: stdout).",
    )
    p.set_defaults(func=run_correlation)


def _open_input(path: str):
    if path == "-":
        return sys.stdin
    return open(path, newline="", encoding="utf-8")


def run_correlation(args: argparse.Namespace) -> None:
    columns: list[str] = [c.strip() for c in args.cols.split(",") if c.strip()]

    with _open_input(args.input) as fh:
        reader = csv.DictReader(fh)
        data = list(reader)

    if args.pair:
        col_a, col_b = args.pair
        r = correlate_columns(iter(data), col_a, col_b)
        result_rows = [{"col_a": col_a, "col_b": col_b, "pearson_r": "" if r is None else f"{r:.6f}"}]
    else:
        matrix = correlation_matrix(data, columns)
        result_rows = [
            {"col_a": a, "col_b": b, "pearson_r": "" if r is None else f"{r:.6f}"}
            for (a, b), r in sorted(matrix.items())
        ]

    fieldnames = ["col_a", "col_b", "pearson_r"]
    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(result_rows)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result_rows)
