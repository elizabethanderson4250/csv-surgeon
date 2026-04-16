"""CLI sub-commands for the annotate feature."""
from __future__ import annotations
import argparse
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.annotate import add_row_number, add_timestamp, add_hash, add_constant


def add_annotate_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("annotate", help="Annotate rows with metadata columns")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--row-num", metavar="COL", help="Add sequential row number column")
    p.add_argument("--timestamp", metavar="COL", help="Add UTC timestamp column")
    p.add_argument("--hash", metavar="COL", help="Add hash fingerprint column")
    p.add_argument("--hash-fields", metavar="COLS", help="Comma-separated fields to hash (default: all)")
    p.add_argument("--hash-algo", default="md5", help="Hash algorithm (default: md5)")
    p.add_argument("--constant", nargs=2, metavar=("COL", "VAL"), help="Add constant value column")
    p.set_defaults(func=run_annotate)


def run_annotate(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.rows()

    if args.row_num:
        rows = add_row_number(rows, column=args.row_num)
    if args.timestamp:
        rows = add_timestamp(rows, column=args.timestamp)
    if args.hash:
        fields = [f.strip() for f in args.hash_fields.split(",")] if args.hash_fields else None
        rows = add_hash(rows, column=args.hash, fields=fields, algorithm=args.hash_algo)
    if args.constant:
        col, val = args.constant
        rows = add_constant(rows, column=col, value=val)

    rows = list(rows)
    if not rows:
        return
    writer = StreamingCSVWriter(args.output, fieldnames=list(rows[0].keys()))
    writer.write_rows(iter(rows))
