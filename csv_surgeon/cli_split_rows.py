"""CLI sub-command: split-rows"""
import argparse
import csv
import sys

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.split_rows import split_rows, explode_rows
from csv_surgeon.writer import StreamingCSVWriter


def add_split_rows_subparser(subparsers) -> None:
    p: argparse.ArgumentParser = subparsers.add_parser(
        "split-rows",
        help="Split a multi-value column into one row per value.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to split")
    p.add_argument("--sep", default=",", help="Separator (default: comma)")
    p.add_argument(
        "--new-column",
        default=None,
        help="Write tokens to a new column, keeping original intact",
    )
    p.add_argument(
        "--keep-empty", action="store_true", help="Keep empty tokens as empty strings"
    )
    p.add_argument(
        "--no-strip", action="store_true", help="Do not strip whitespace from tokens"
    )
    p.set_defaults(func=run_split_rows)


def run_split_rows(args) -> None:
    reader = StreamingCSVReader(args.input)
    headers = reader.headers()
    strip = not args.no_strip

    if args.new_column:
        out_headers = headers + [args.new_column] if args.new_column not in headers else headers
        rows = explode_rows(
            reader.rows(),
            column=args.column,
            separator=args.sep,
            new_column=args.new_column,
            strip=strip,
        )
    else:
        out_headers = headers
        rows = split_rows(
            reader.rows(),
            column=args.column,
            separator=args.sep,
            strip=strip,
            keep_empty=args.keep_empty,
        )

    writer = StreamingCSVWriter(args.output, fieldnames=out_headers)
    writer.write_rows(rows)
