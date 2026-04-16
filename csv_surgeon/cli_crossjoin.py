"""CLI subcommands for cross-join and semi-join operations."""
import argparse
import csv
import sys

from csv_surgeon.crossjoin import cross_join, semi_join
from csv_surgeon.writer import StreamingCSVWriter


def add_crossjoin_subparser(subparsers: argparse._SubParsersAction) -> None:
    p_cross = subparsers.add_parser("crossjoin", help="Cartesian product of two CSV files")
    p_cross.add_argument("left", help="Left CSV file")
    p_cross.add_argument("right", help="Right CSV file")
    p_cross.add_argument("-o", "--output", required=True, help="Output CSV file")
    p_cross.set_defaults(func=run_crossjoin)

    p_semi = subparsers.add_parser("semijoin", help="Semi-join or anti-join two CSV files")
    p_semi.add_argument("left", help="Left CSV file")
    p_semi.add_argument("right", help="Right CSV file")
    p_semi.add_argument("--left-key", required=True, dest="left_key")
    p_semi.add_argument("--right-key", required=True, dest="right_key")
    p_semi.add_argument("--anti", action="store_true", help="Anti-join (exclude matches)")
    p_semi.add_argument("-o", "--output", required=True, help="Output CSV file")
    p_semi.set_defaults(func=run_semijoin)


def _read_rows(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def run_crossjoin(args) -> None:
    left_rows = _read_rows(args.left)
    right_rows = _read_rows(args.right)
    result = list(cross_join(left_rows, right_rows))
    if not result:
        print("No rows produced.", file=sys.stderr)
        return
    writer = StreamingCSVWriter(args.output, fieldnames=list(result[0].keys()))
    writer.write_rows(result)


def run_semijoin(args) -> None:
    left_rows = _read_rows(args.left)
    right_rows = _read_rows(args.right)
    result = list(semi_join(left_rows, right_rows, args.left_key, args.right_key, negate=args.anti))
    if not result:
        print("No rows produced.", file=sys.stderr)
        return
    writer = StreamingCSVWriter(args.output, fieldnames=list(result[0].keys()))
    writer.write_rows(result)
