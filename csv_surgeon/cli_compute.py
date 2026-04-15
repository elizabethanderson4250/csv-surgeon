"""CLI sub-commands columns."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csv_surgeon.compute import add_column, compute_expression, copy_column, drop_column
from csv_surgeon.reader import StreamingCSsurgeon.writer import StreamingCSVWriter


def add_compute_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("compute", help="Add or manipulate columns")
    sub = p.add_subparsers(dest="compute_cmd", required=True)

    # add-column via expression
    expr_p = sub.add_parser("expr", help="Add column from arithmetic expression")
    expr_p.add_argument("--input", required=True)
    expr_p.add_argument("--output", required=True)
    expr_p.add_argument("--name", required=True, help="New column name")
    expr_p.add_argument("--expr", required=True, help="Arithmetic expression")

    # copy
    copy_p = sub.add_parser("copy", help="Copy a column")
    copy_p.add_argument("--input", required=True)
    copy_p.add_argument("--output", required=True)
    copy_p.add_argument("--source", required=True)
    copy_p.add_argument("--dest", required=True)

    # drop
    drop_p = sub.add_parser("drop", help="Drop one or more columns")
    drop_p.add_argument("--input", required=True)
    drop_p.add_argument("--output", required=True)
    drop_p.add_argument("--columns", required=True, nargs="+")

    p.set_defaults(func=run_compute)


def run_compute(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.rows()

    if args.compute_cmd == "expr":
        result = compute_expression(rows, args.name, args.expr)
        # Derive headers: original + new column
        headers = reader.headers + [args.name]
    elif args.compute_cmd == "copy":
        result = copy_column(rows, args.source, args.dest)
        headers = reader.headers + [args.dest]
    elif args.compute_cmd == "drop":
        result = rows
        for col in args.columns:
            result = drop_column(result, col)
        headers = [h for h in reader.headers if h not in args.columns]
    else:
        print(f"Unknown compute sub-command: {args.compute_cmd}", file=sys.stderr)
        sys.exit(1)

    writer = StreamingCSVWriter(args.output, fieldnames=headers)
    writer.write_rows(result)
