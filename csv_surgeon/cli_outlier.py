"""CLI sub-command for outlier detection."""
from __future__ import annotations

import argparse
import sys

from csv_surgeon.outlier import flag_outliers_iqr, flag_outliers_zscore, remove_outliers_iqr
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_outlier_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("outlier", help="Detect or remove outliers in a numeric column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Numeric column to analyse")
    p.add_argument(
        "--method",
        choices=["iqr", "zscore"],
        default="iqr",
        help="Detection method (default: iqr)",
    )
    p.add_argument("--threshold", type=float, default=3.0, help="Z-score threshold (zscore method)")
    p.add_argument("--multiplier", type=float, default=1.5, help="IQR multiplier (iqr method)")
    p.add_argument(
        "--action",
        choices=["flag", "remove"],
        default="flag",
        help="Whether to flag outliers or remove them (default: flag)",
    )
    p.add_argument("--output-column", default="is_outlier", help="Column name for flag output")
    p.set_defaults(func=run_outlier)


def run_outlier(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.rows()

    if args.action == "remove":
        result = remove_outliers_iqr(rows, column=args.column, multiplier=args.multiplier)
    elif args.method == "zscore":
        result = flag_outliers_zscore(
            rows,
            column=args.column,
            threshold=args.threshold,
            output_column=args.output_column,
        )
    else:
        result = flag_outliers_iqr(
            rows,
            column=args.column,
            multiplier=args.multiplier,
            output_column=args.output_column,
        )

    buffered = list(result)
    if not buffered:
        print("No rows to write.", file=sys.stderr)
        return

    writer = StreamingCSVWriter(args.output, fieldnames=list(buffered[0].keys()))
    writer.write_rows(iter(buffered))
