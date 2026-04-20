"""CLI subcommand: extract — pull values out of a column via regex, substring, or split."""

import argparse
import csv
import sys

from csv_surgeon.extract import extract_regex, extract_substring, extract_split_index, apply_extract
from csv_surgeon.writer import StreamingCSVWriter


def add_extract_subparser(subparsers) -> None:
    p = subparsers.add_parser("extract", help="Extract values from a column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--output", "-o", required=True, help="Output CSV file")
    p.add_argument("--column", "-c", required=True, help="Source column")
    p.add_argument("--into", default=None, help="Destination column (default: overwrite source)")
    p.add_argument("--default", default="", help="Value when extraction fails")

    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--regex", metavar="PATTERN", help="Regex pattern; use --group to pick capture group")
    mode.add_argument("--substring", nargs=2, metavar=("START", "END"), help="Substring slice (start end)")
    mode.add_argument("--split", nargs=2, metavar=("SEP", "INDEX"), help="Split on SEP and take INDEX")

    p.add_argument("--group", type=int, default=1, help="Capture group number for --regex (default: 1)")


def run_extract(args) -> None:
    column = args.column
    into = args.into
    default = args.default

    if args.regex:
        transform = extract_regex(column, output_column=into, default=default,
                                  pattern=args.regex, group=args.group)
    elif args.substring:
        start, end = int(args.substring[0]), int(args.substring[1])
        transform = extract_substring(column, output_column=into, default=default,
                                      start=start, end=end)
    else:
        sep, index = args.split[0], int(args.split[1])
        transform = extract_split_index(column, output_column=into, default=default,
                                        sep=sep, index=index)

    with open(args.input, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    dest_col = into or column
    if dest_col not in fieldnames:
        fieldnames.append(dest_col)

    transformed = list(apply_extract(rows, transform))
    writer = StreamingCSVWriter(args.output, fieldnames=fieldnames)
    writer.write_rows(transformed)
