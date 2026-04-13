"""CLI subcommand for validating CSV rows."""

import argparse
import sys
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.validate import required, is_numeric, max_length, matches_pattern, validate_rows
from csv_surgeon.writer import StreamingCSVWriter


def add_validate_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("validate", help="Validate rows against column rules")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--output", "-o", help="Output file for valid rows (default: stdout)")
    parser.add_argument(
        "--required", nargs="+", metavar="COL", default=[], help="Columns that must be non-empty"
    )
    parser.add_argument(
        "--numeric", nargs="+", metavar="COL", default=[], help="Columns that must be numeric"
    )
    parser.add_argument(
        "--max-length", nargs="+", metavar="COL:N", default=[],
        help="Columns with max char length (e.g. name:50)"
    )
    parser.add_argument(
        "--pattern", nargs="+", metavar="COL:REGEX", default=[],
        help="Columns that must match a regex (e.g. email:.*@.*)"
    )
    parser.add_argument(
        "--fail-fast", action="store_true", help="Stop on first validation error"
    )
    parser.set_defaults(func=run_validate)


def run_validate(args: argparse.Namespace) -> None:
    validators = []

    for col in args.required:
        validators.append(required(col))

    for col in args.numeric:
        validators.append(is_numeric(col))

    for spec in args.max_length:
        col, _, n = spec.partition(":")
        if not n.isdigit():
            print(f"Invalid --max-length spec '{spec}', expected COL:N", file=sys.stderr)
            sys.exit(1)
        validators.append(max_length(col, int(n)))

    for spec in args.pattern:
        col, _, pattern = spec.partition(":")
        validators.append(matches_pattern(col, pattern))

    reader = StreamingCSVReader(args.input)
    valid_rows = validate_rows(reader.rows(), validators, fail_fast=args.fail_fast)

    if args.output:
        writer = StreamingCSVWriter(args.output, fieldnames=reader.headers)
        writer.write_rows(valid_rows)
    else:
        import csv
        writer = csv.DictWriter(sys.stdout, fieldnames=reader.headers)
        writer.writeheader()
        for row in valid_rows:
            writer.writerow(row)
