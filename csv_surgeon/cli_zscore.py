"""CLI sub-commands for z-score normalization and min-max scaling."""
from __future__ import annotations

import argparse
import csv
import sys

from csv_surgeon.zscore import zscore_column, minmax_scale_column
from csv_surgeon.writer import StreamingCSVWriter


def add_zscore_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "zscore",
        help="Normalize a numeric column using z-score or min-max scaling.",
    )
    p.add_argument("input", help="Input CSV file (use - for stdin).")
    p.add_argument("output", help="Output CSV file (use - for stdout).")
    p.add_argument("--column", required=True, help="Column to normalize.")
    p.add_argument(
        "--method",
        choices=["zscore", "minmax"],
        default="zscore",
        help="Normalization method (default: zscore).",
    )
    p.add_argument("--output-column", default=None, help="Name for the result column.")
    p.add_argument("--default", default="", help="Value for non-numeric cells.")
    p.add_argument("--precision", type=int, default=6, help="Decimal precision (default: 6).")
    p.add_argument(
        "--range",
        dest="feature_range",
        default="0,1",
        help="Min,max target range for minmax (default: 0,1).",
    )
    p.set_defaults(func=run_zscore)


def run_zscore(args: argparse.Namespace) -> None:
    in_fh = open(args.input, newline="") if args.input != "-" else sys.stdin
    try:
        reader = csv.DictReader(in_fh)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

        out_col = args.output_column or (
            f"{args.column}_zscore" if args.method == "zscore" else f"{args.column}_scaled"
        )
        if out_col not in fieldnames:
            fieldnames = list(fieldnames) + [out_col]

        if args.method == "zscore":
            result = zscore_column(
                rows,
                column=args.column,
                output_column=out_col,
                default=args.default,
                precision=args.precision,
            )
        else:
            lo, hi = (float(x) for x in args.feature_range.split(","))
            result = minmax_scale_column(
                rows,
                column=args.column,
                output_column=out_col,
                default=args.default,
                precision=args.precision,
                feature_range=(lo, hi),
            )

        writer = StreamingCSVWriter(args.output, fieldnames=fieldnames)
        writer.write_rows(result)
    finally:
        if args.input != "-":
            in_fh.close()
