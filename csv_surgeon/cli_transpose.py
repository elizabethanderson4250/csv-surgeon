"""CLI subcommand for transpose operations."""
import argparse
import csv
import sys
from csv_surgeon.transpose import transpose_to_rows, transpose_to_columns, flip
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_transpose_subparser(subparsers):
    p = subparsers.add_parser("transpose", help="Transpose CSV rows and columns")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--to-rows", action="store_true", help="Wide to key-value rows")
    mode.add_argument("--to-columns", action="store_true", help="Key-value rows to wide")
    mode.add_argument("--flip", action="store_true", help="Flip rows and columns")
    p.add_argument("--key-col", default="field", help="Key column name (default: field)")
    p.add_argument("--value-col", default="value", help="Value column name (default: value)")
    p.set_defaults(func=run_transpose)


def run_transpose(args):
    reader = StreamingCSVReader(args.input)
    rows = list(reader.rows())

    if args.to_rows:
        result = transpose_to_rows(rows, key_col=args.key_col, value_col=args.value_col)
    elif args.to_columns:
        result = transpose_to_columns(rows, key_col=args.key_col, value_col=args.value_col)
    else:
        result = flip(rows)

    if not result:
        print("No output rows produced.", file=sys.stderr)
        return

    writer = StreamingCSVWriter(args.output, fieldnames=list(result[0].keys()))
    writer.write_rows(iter(result))
