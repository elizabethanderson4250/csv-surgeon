"""CLI sub-command: sample — draw rows from a CSV file."""

import argparse
import sys

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.sample import head, sample_fraction, sample_rows
from csv_surgeon.writer import StreamingCSVWriter


def add_sample_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("sample", help="Sample rows from a CSV file")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file (use '-' for stdout)")

    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--head",
        metavar="N",
        type=int,
        help="Keep the first N rows",
    )
    mode.add_argument(
        "--reservoir",
        metavar="N",
        type=int,
        help="Reservoir-sample exactly N rows",
    )
    mode.add_argument(
        "--fraction",
        metavar="F",
        type=float,
        help="Keep each row with probability F (0 < F <= 1)",
    )

    p.add_argument("--seed", type=int, default=None, help="Random seed")
    p.set_defaults(func=run_sample)


def run_sample(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows_iter = reader.rows()

    if args.head is not None:
        sampled = head(rows_iter, n=args.head)
    elif args.reservoir is not None:
        sampled = sample_rows(rows_iter, n=args.reservoir, seed=args.seed)
    else:
        sampled = sample_fraction(rows_iter, fraction=args.fraction, seed=args.seed)

    dest = sys.stdout if args.output == "-" else args.output
    writer = StreamingCSVWriter(dest, fieldnames=reader.headers)
    writer.write_rows(iter(sampled))
