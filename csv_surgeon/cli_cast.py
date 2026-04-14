"""CLI subcommand for casting CSV column types."""

import argparse
import csv
import sys
from csv_surgeon.cast import to_int, to_float, to_bool, to_str
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter

_CAST_MAP = {
    "int": to_int,
    "float": to_float,
    "bool": to_bool,
    "str": to_str,
}


def add_cast_subparser(subparsers) -> None:
    parser = subparsers.add_parser("cast", help="Cast column values to a target type")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("output", help="Output CSV file")
    parser.add_argument(
        "--cast",
        action="append",
        metavar="COL:TYPE",
        dest="casts",
        required=True,
        help="Column and target type, e.g. age:int or score:float (repeatable)",
    )


def run_cast(args) -> None:
    casts = []
    for spec in args.casts:
        if ":" not in spec:
            print(f"Invalid cast spec {spec!r}, expected COL:TYPE", file=sys.stderr)
            sys.exit(1)
        col, type_name = spec.split(":", 1)
        if type_name not in _CAST_MAP:
            print(f"Unknown type {type_name!r}. Choose from: {list(_CAST_MAP)}", file=sys.stderr)
            sys.exit(1)
        casts.append(_CAST_MAP[type_name](col))

    reader = StreamingCSVReader(args.input)
    headers = reader.headers()

    def _cast_rows():
        for row in reader.rows():
            for fn in casts:
                row = fn(row)
            yield row

    writer = StreamingCSVWriter(args.output, fieldnames=headers)
    writer.write_rows(_cast_rows())
