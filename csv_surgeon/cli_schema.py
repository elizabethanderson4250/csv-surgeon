"""CLI sub-commands for schema inference and enforcement."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.schema import enforce_schema, infer_schema
from csv_surgeon.writer import StreamingCSVWriter


def add_schema_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # --- infer ---
    infer_p = subparsers.add_parser("schema-infer", help="Infer column types from a CSV file.")
    infer_p.add_argument("input", help="Input CSV file")
    infer_p.add_argument(
        "--output", "-o", default=None,
        help="Write JSON schema to this file (default: stdout)",
    )
    infer_p.set_defaults(schema_cmd="infer")

    # --- enforce ---
    enforce_p = subparsers.add_parser(
        "schema-enforce", help="Filter rows that do not match a JSON schema."
    )
    enforce_p.add_argument("input", help="Input CSV file")
    enforce_p.add_argument("schema", help="JSON schema file produced by schema-infer")
    enforce_p.add_argument("--output", "-o", required=True, help="Output CSV file")
    enforce_p.add_argument(
        "--strict", action="store_true",
        help="Raise an error on the first non-conforming row instead of skipping it",
    )
    enforce_p.set_defaults(schema_cmd="enforce")


def run_schema_infer(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    schema = infer_schema(reader.rows())
    text = json.dumps(schema, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        print(text)


def run_schema_enforce(args: argparse.Namespace) -> None:
    with open(args.schema, "r", encoding="utf-8") as fh:
        schema = json.load(fh)

    reader = StreamingCSVReader(args.input)
    conforming = enforce_schema(reader.rows(), schema, strict=args.strict)
    writer = StreamingCSVWriter(args.output, fieldnames=reader.headers)
    writer.write_rows(conforming)


def run_schema(args: argparse.Namespace) -> None:
    cmd = getattr(args, "schema_cmd", None)
    if cmd == "infer":
        run_schema_infer(args)
    elif cmd == "enforce":
        run_schema_enforce(args)
    else:
        print("Unknown schema sub-command.", file=sys.stderr)
        sys.exit(1)
