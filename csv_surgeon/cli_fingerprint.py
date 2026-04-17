"""CLI sub-command: fingerprint."""
from __future__ import annotations
import argparse
import json
import sys

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.fingerprint import fingerprint_columns, fingerprint_rows
from csv_surgeon.writer import StreamingCSVWriter


def add_fingerprint_subparser(subparsers) -> None:
    p = subparsers.add_parser("fingerprint", help="Fingerprint columns or annotate rows with hash")
    sub = p.add_subparsers(dest="fp_cmd", required=True)

    # columns sub-command
    cols_p = sub.add_parser("columns", help="Print per-column fingerprint stats as JSON")
    cols_p.add_argument("input", help="Input CSV file")
    cols_p.add_argument("--sample-limit", type=int, default=5)

    # rows sub-command
    rows_p = sub.add_parser("rows", help="Annotate rows with a hash of key columns")
    rows_p.add_argument("input", help="Input CSV file")
    rows_p.add_argument("output", help="Output CSV file")
    rows_p.add_argument("--key-columns", required=True, help="Comma-separated key columns")


def run_fingerprint(args: argparse.Namespace) -> None:
    if args.fp_cmd == "columns":
        reader = StreamingCSVReader(args.input)
        stats = fingerprint_columns(reader.rows(), sample_limit=args.sample_limit)
        json.dump(stats, sys.stdout, indent=2)
        sys.stdout.write("\n")
    elif args.fp_cmd == "rows":
        key_cols = [c.strip() for c in args.key_columns.split(",")]
        reader = StreamingCSVReader(args.input)
        annotated = fingerprint_rows(reader.rows(), key_columns=key_cols)
        headers = reader.headers() + ["_row_hash"]
        writer = StreamingCSVWriter(args.output, fieldnames=headers)
        writer.write_rows(annotated)
