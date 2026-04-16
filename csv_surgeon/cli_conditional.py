"""CLI sub-command: conditional — set a column value based on a condition."""

import argparse
import csv
import sys
from typing import List

from csv_surgeon.conditional import if_else, apply_conditional
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_conditional_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "conditional",
        help="Set a column value based on a condition over another column.",
    )
    p.add_argument("input", help="Input CSV file path")
    p.add_argument("output", help="Output CSV file path")
    p.add_argument("--column", required=True, help="Column to set")
    p.add_argument("--when", required=True, metavar="COL=VALUE",
                   help="Condition expressed as COL=VALUE")
    p.add_argument("--true", dest="true_value", required=True,
                   help="Value to write when condition is true")
    p.add_argument("--false", dest="false_value", required=True,
                   help="Value to write when condition is false")
    p.set_defaults(func=run_conditional)


def _parse_condition(when_expr: str):
    """Parse 'COL=VALUE' into a callable that tests a row."""
    if "=" not in when_expr:
        raise argparse.ArgumentTypeError(
            f"--when must be in COL=VALUE format, got: {when_expr!r}"
        )
    col, _, val = when_expr.partition("=")
    col = col.strip()
    val = val.strip()

    def condition(row):
        return row.get(col, "") == val

    return condition


def run_conditional(args) -> None:
    condition = _parse_condition(args.when)
    transform = if_else(
        column=args.column,
        condition=condition,
        true_value=args.true_value,
        false_value=args.false_value,
    )

    reader = StreamingCSVReader(args.input)
    rows = apply_conditional(reader.rows(), transform)
    writer = StreamingCSVWriter(args.output, fieldnames=reader.headers())
    writer.write_rows(rows)
