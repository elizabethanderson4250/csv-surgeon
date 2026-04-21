"""CLI sub-command: interpolate — fill missing numeric column values."""
from __future__ import annotations

import argparse
from typing import List

from csv_surgeon.interpolate import backward_fill, forward_fill, linear_interpolate
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter

_METHODS = {"linear", "forward", "backward"}


def add_interpolate_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "interpolate",
        help="Fill missing values in a numeric column via interpolation.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to interpolate")
    p.add_argument(
        "--method",
        choices=list(_METHODS),
        default="linear",
        help="Interpolation method (default: linear)",
    )
    p.add_argument(
        "--output-column",
        default=None,
        help="Write result to a new column instead of overwriting",
    )
    p.add_argument(
        "--fill-leading",
        action="store_true",
        help="(linear) fill leading NaN from first known value",
    )
    p.add_argument(
        "--fill-trailing",
        action="store_true",
        help="(linear) fill trailing NaN from last known value",
    )
    p.set_defaults(func=run_interpolate)


def run_interpolate(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.rows()

    if args.method == "linear":
        result = linear_interpolate(
            rows,
            column=args.column,
            output_column=args.output_column,
            fill_leading=args.fill_leading,
            fill_trailing=args.fill_trailing,
        )
    elif args.method == "forward":
        result = forward_fill(rows, column=args.column, output_column=args.output_column)
    else:
        result = backward_fill(rows, column=args.column, output_column=args.output_column)

    headers = list(reader.headers)
    out_col = args.output_column or args.column
    if out_col not in headers:
        headers = headers + [out_col]

    writer = StreamingCSVWriter(args.output, fieldnames=headers)
    writer.write_rows(result)
