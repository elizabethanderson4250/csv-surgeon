"""CLI sub-commands for column rename / reorder / drop / select."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.rename_cols import (
    rename_columns,
    reorder_columns,
    drop_columns,
    select_columns,
)


def add_rename_cols_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "rename-cols",
        help="Rename, reorder, drop, or select columns.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("output", help="Output CSV file (use '-' for stdout).")

    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--rename",
        nargs="+",
        metavar="OLD=NEW",
        help="Rename columns: OLD=NEW pairs.",
    )
    action.add_argument(
        "--reorder",
        nargs="+",
        metavar="COL",
        help="Keep and reorder to these columns only.",
    )
    action.add_argument(
        "--drop",
        nargs="+",
        metavar="COL",
        help="Drop the listed columns.",
    )
    action.add_argument(
        "--select",
        nargs="+",
        metavar="COL",
        help="Select (keep) only these columns.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Raise an error if a referenced column is missing.",
    )


def _parse_rename_pairs(pairs: List[str]) -> dict:
    mapping = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid rename spec (expected OLD=NEW): {pair!r}")
        old, new = pair.split("=", 1)
        mapping[old.strip()] = new.strip()
    return mapping


def run_rename_cols(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(
        sys.stdin if args.input == "-" else args.input
    )
    rows = reader.rows()

    if args.rename:
        mapping = _parse_rename_pairs(args.rename)
        rows = rename_columns(rows, mapping, strict=args.strict)
        fieldnames = [
            mapping.get(h, h) for h in reader.headers
        ]
    elif args.reorder:
        rows = reorder_columns(rows, args.reorder)
        fieldnames = args.reorder
    elif args.drop:
        rows = drop_columns(rows, args.drop)
        fieldnames = [h for h in reader.headers if h not in set(args.drop)]
    else:  # select
        rows = select_columns(rows, args.select)
        fieldnames = args.select

    writer = StreamingCSVWriter(
        sys.stdout if args.output == "-" else args.output,
        fieldnames=fieldnames,
    )
    writer.write_rows(rows)
