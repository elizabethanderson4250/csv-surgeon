"""CLI sub-commands for reshape: widen, narrow, stack, unstack."""
import argparse
import csv
import sys
from typing import List

from csv_surgeon.reshape import widen, narrow, stack_columns, unstack_column
from csv_surgeon.writer import StreamingCSVWriter


def add_reshape_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("reshape", help="Reshape CSV columns")
    sub = p.add_subparsers(dest="reshape_cmd", required=True)

    # widen
    pw = sub.add_parser("widen", help="Long -> wide (pivot)")
    pw.add_argument("--index", required=True, help="Index column")
    pw.add_argument("--key", required=True, help="Column whose values become headers")
    pw.add_argument("--value", required=True, help="Column whose values fill cells")
    pw.add_argument("--input", required=True)
    pw.add_argument("--output", required=True)

    # narrow
    pn = sub.add_parser("narrow", help="Wide -> long (melt)")
    pn.add_argument("--index", required=True)
    pn.add_argument("--columns", required=True, help="Comma-separated value columns")
    pn.add_argument("--key-col", default="key")
    pn.add_argument("--value-col", default="value")
    pn.add_argument("--input", required=True)
    pn.add_argument("--output", required=True)

    # stack
    ps = sub.add_parser("stack", help="Stack multiple columns into one")
    ps.add_argument("--columns", required=True, help="Comma-separated columns to stack")
    ps.add_argument("--output-col", default="value")
    ps.add_argument("--label-col", default="source")
    ps.add_argument("--input", required=True)
    ps.add_argument("--output", required=True)

    # unstack
    pu = sub.add_parser("unstack", help="Unstack label+value back to columns")
    pu.add_argument("--index", required=True)
    pu.add_argument("--label-col", required=True)
    pu.add_argument("--value-col", required=True)
    pu.add_argument("--input", required=True)
    pu.add_argument("--output", required=True)


def _read_rows(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def run_reshape(args: argparse.Namespace) -> None:
    if args.reshape_cmd == "widen":
        rows = _read_rows(args.input)
        result = widen(iter(rows), args.index, args.key, args.value)
    elif args.reshape_cmd == "narrow":
        rows = _read_rows(args.input)
        cols = [c.strip() for c in args.columns.split(",")]
        result = list(narrow(iter(rows), args.index, cols, args.key_col, args.value_col))
    elif args.reshape_cmd == "stack":
        rows = _read_rows(args.input)
        cols = [c.strip() for c in args.columns.split(",")]
        result = list(stack_columns(iter(rows), cols, args.output_col, args.label_col))
    elif args.reshape_cmd == "unstack":
        rows = _read_rows(args.input)
        result = unstack_column(iter(rows), args.label_col, args.value_col, args.index)
    else:
        print(f"Unknown reshape command: {args.reshape_cmd}", file=sys.stderr)
        sys.exit(1)

    if not result:
        print("No rows produced.", file=sys.stderr)
        return

    fieldnames = list(result[0].keys())
    writer = StreamingCSVWriter(args.output, fieldnames=fieldnames)
    writer.write_rows(iter(result))
