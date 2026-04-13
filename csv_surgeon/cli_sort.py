"""CLI subcommand for sorting CSV files."""

import argparse
import csv
import sys

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.sort import sort_rows
from csv_surgeon.writer import StreamingCSVWriter


def add_sort_subparser(subparsers) -> None:
    """Register the 'sort' subcommand."""
    parser = subparsers.add_parser(
        "sort",
        help="Sort rows in a CSV file by one or more columns.",
    )
    parser.add_argument("input", help="Path to input CSV file.")
    parser.add_argument("output", help="Path to output CSV file.")
    parser.add_argument(
        "--by",
        required=True,
        nargs="+",
        metavar="COLUMN",
        help="Column(s) to sort by, in priority order.",
    )
    parser.add_argument(
        "--desc",
        action="store_true",
        default=False,
        help="Sort in descending order.",
    )
    parser.add_argument(
        "--numeric",
        action="store_true",
        default=False,
        help="Treat sort key values as numbers.",
    )
    parser.set_defaults(func=run_sort)


def run_sort(args) -> None:
    """Execute the sort subcommand."""
    reader = StreamingCSVReader(args.input)

    missing = [col for col in args.by if col not in reader.headers]
    if missing:
        print(
            f"Error: column(s) not found in CSV: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)

    sorted_rows = sort_rows(
        reader.rows(),
        key_columns=args.by,
        reverse=args.desc,
        numeric=args.numeric,
    )

    writer = StreamingCSVWriter(args.output, fieldnames=reader.headers)
    writer.write_rows(sorted_rows)
