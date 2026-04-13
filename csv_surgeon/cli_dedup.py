"""CLI helpers for the dedup sub-command of csv-surgeon."""
import argparse
import csv
import sys
from typing import List, Optional

from csv_surgeon.dedup import dedup_by_columns
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_dedup_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'dedup' sub-command on *subparsers*."""
    parser = subparsers.add_parser(
        "dedup",
        help="Remove duplicate rows from a CSV file based on one or more columns.",
    )
    parser.add_argument("input", help="Path to the input CSV file.")
    parser.add_argument("-o", "--output", default=None, help="Output file path (default: stdout).")
    parser.add_argument(
        "-c", "--columns",
        required=True,
        help="Comma-separated column names used to detect duplicates.",
    )
    parser.add_argument(
        "--keep",
        choices=["first", "last"],
        default="first",
        help="Which occurrence to keep when duplicates are found (default: first).",
    )
    parser.set_defaults(func=run_dedup)


def run_dedup(args: argparse.Namespace) -> None:
    """Execute the dedup sub-command."""
    columns: List[str] = [c.strip() for c in args.columns.split(",") if c.strip()]
    if not columns:
        print("Error: --columns must not be empty.", file=sys.stderr)
        sys.exit(1)

    reader = StreamingCSVReader(args.input)

    # Validate requested columns exist in the file
    missing = [c for c in columns if c not in reader.headers]
    if missing:
        print(f"Error: columns not found in CSV: {missing}", file=sys.stderr)
        sys.exit(1)

    unique_rows = dedup_by_columns(reader.rows(), columns=columns, keep=args.keep)

    if args.output:
        writer = StreamingCSVWriter(args.output, fieldnames=reader.headers)
        count = writer.write_rows(unique_rows)
        print(f"Wrote {count} unique row(s) to {args.output}")
    else:
        writer_out = csv.DictWriter(sys.stdout, fieldnames=reader.headers)
        writer_out.writeheader()
        for row in unique_rows:
            writer_out.writerow(row)
