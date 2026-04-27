"""CLI subcommand: regex-filter — filter rows by regex on one or more columns."""
from __future__ import annotations

import argparse
import csv
import sys

from csv_surgeon.regex_filter import filter_any_column, filter_by_regex
from csv_surgeon.writer import StreamingCSVWriter


def add_regex_filter_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "regex-filter",
        help="Filter rows using a regular expression on a column.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout).")
    p.add_argument("-c", "--column", help="Column to match against (omit to search all columns).")
    p.add_argument("-p", "--pattern", required=True, help="Regular expression pattern.")
    p.add_argument("-i", "--ignore-case", action="store_true", help="Case-insensitive matching.")
    p.add_argument("-v", "--invert", action="store_true", help="Invert match (exclude matching rows).")
    p.set_defaults(func=run_regex_filter)


def _open_input(path: str):
    if path == "-":
        return sys.stdin
    return open(path, newline="", encoding="utf-8")


def run_regex_filter(args: argparse.Namespace) -> None:
    with _open_input(args.input) as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if args.column:
        filtered = filter_by_regex(
            rows,
            args.column,
            args.pattern,
            ignore_case=args.ignore_case,
            invert=args.invert,
        )
    else:
        filtered = filter_any_column(
            rows,
            args.pattern,
            ignore_case=args.ignore_case,
            invert=args.invert,
        )

    writer = StreamingCSVWriter(args.output, fieldnames=fieldnames)
    writer.write_rows(filtered)
