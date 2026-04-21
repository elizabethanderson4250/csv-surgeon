"""CLI sub-command: auto-cast — infer column types and cast values."""
from __future__ import annotations

import argparse
import csv
import io
import sys
from typing import List

from csv_surgeon.typecast_infer import auto_cast_rows
from csv_surgeon.writer import StreamingCSVWriter


def add_typecast_infer_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "auto-cast",
        help="Infer column types from sample rows and cast all values.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout).")
    p.add_argument(
        "--sample-size",
        type=int,
        default=200,
        metavar="N",
        help="Number of rows to sample for type inference (default: 200).",
    )
    p.add_argument(
        "--stringify",
        action="store_true",
        help="Write cast values as strings (preserves CSV format).",
    )
    p.set_defaults(func=run_typecast_infer)


def _open_input(path: str):
    if path == "-":
        return sys.stdin
    return open(path, newline="", encoding="utf-8")


def run_typecast_infer(args: argparse.Namespace) -> None:
    fh = _open_input(args.input)
    try:
        reader = csv.DictReader(fh)
        raw_rows = list(reader)
        fieldnames: List[str] = reader.fieldnames or []
    finally:
        if fh is not sys.stdin:
            fh.close()

    cast_iter = auto_cast_rows(iter(raw_rows), sample_size=args.sample_size)

    # Convert back to str-dicts for the writer
    str_rows = [
        {k: ("" if v is None else str(v)) for k, v in row.items()}
        for row in cast_iter
    ]

    if args.output == "-":
        buf = io.StringIO()
        writer = StreamingCSVWriter(buf, fieldnames=fieldnames)  # type: ignore[arg-type]
        writer.write_rows(str_rows)
        print(buf.getvalue(), end="")
    else:
        with open(args.output, "w", newline="", encoding="utf-8") as out:
            writer = StreamingCSVWriter(out, fieldnames=fieldnames)  # type: ignore[arg-type]
            writer.write_rows(str_rows)
