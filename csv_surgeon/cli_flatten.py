"""CLI sub-commands for flatten / merge / split column operations."""
import argparse
import csv
import sys
from typing import List

from csv_surgeon.flatten import flatten_column, merge_columns, split_column
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_flatten_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *flatten* sub-command group."""
    p = subparsers.add_parser("flatten", help="Flatten, merge or split columns")
    sub = p.add_subparsers(dest="flatten_cmd", required=True)

    # flatten column
    pf = sub.add_parser("explode", help="Explode a delimited column into multiple rows")
    pf.add_argument("input", help="Input CSV file")
    pf.add_argument("output", help="Output CSV file")
    pf.add_argument("--column", required=True, help="Column to explode")
    pf.add_argument("--separator", default="|", help="Delimiter (default: |)")
    pf.add_argument("--no-strip", action="store_true", help="Do not strip whitespace")

    # merge columns
    pm = sub.add_parser("merge", help="Merge multiple columns into one")
    pm.add_argument("input", help="Input CSV file")
    pm.add_argument("output", help="Output CSV file")
    pm.add_argument("--columns", required=True, nargs="+", help="Columns to merge")
    pm.add_argument("--into", required=True, help="Name of the new merged column")
    pm.add_argument("--separator", default=" ", help="Separator between values")
    pm.add_argument("--keep-originals", action="store_true", help="Keep source columns")

    # split column
    ps = sub.add_parser("split", help="Split a column into multiple named columns")
    ps.add_argument("input", help="Input CSV file")
    ps.add_argument("output", help="Output CSV file")
    ps.add_argument("--column", required=True, help="Column to split")
    ps.add_argument("--into", required=True, nargs="+", help="New column names")
    ps.add_argument("--separator", default=" ", help="Delimiter")
    ps.add_argument("--keep-original", action="store_true", help="Keep source column")


def run_flatten(args: argparse.Namespace) -> None:
    """Dispatch to the correct flatten operation."""
    reader = StreamingCSVReader(args.input)
    rows = reader.rows()

    if args.flatten_cmd == "explode":
        result = flatten_column(
            rows,
            column=args.column,
            separator=args.separator,
            strip=not args.no_strip,
        )
        headers = reader.headers
    elif args.flatten_cmd == "merge":
        result = merge_columns(
            rows,
            columns=args.columns,
            into=args.into,
            separator=args.separator,
            drop_originals=not args.keep_originals,
        )
        headers = [c for c in reader.headers if c not in args.columns] + [args.into]
        if args.keep_originals:
            headers = reader.headers + [args.into]
    elif args.flatten_cmd == "split":
        result = split_column(
            rows,
            column=args.column,
            into=args.into,
            separator=args.separator,
            drop_original=not args.keep_original,
        )
        base = [c for c in reader.headers if c != args.column]
        headers = base + args.into if not args.keep_original else reader.headers + args.into
    else:
        print(f"Unknown flatten command: {args.flatten_cmd}", file=sys.stderr)
        sys.exit(1)

    writer = StreamingCSVWriter(args.output, fieldnames=headers)
    writer.write_rows(result)
