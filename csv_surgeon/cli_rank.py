"""CLI sub-command: rank — assign rank or row-number columns."""
from __future__ import annotations

import argparse
import sys

from csv_surgeon.rank import rank_rows, row_number
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_rank_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("rank", help="Rank rows by a column value")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--sort-column", required=True, dest="sort_column",
                   help="Column to sort/rank by")
    p.add_argument("--output-column", default="rank", dest="output_column",
                   help="Name for the new rank column (default: rank)")
    p.add_argument("--method", choices=["dense", "standard", "percent"],
                   default="dense", help="Ranking method (default: dense)")
    p.add_argument("--descending", action="store_true",
                   help="Rank in descending order")
    p.add_argument("--numeric", action="store_true",
                   help="Treat sort column as numeric")
    p.add_argument("--group-by", dest="group_by", default=None,
                   help="Reset rank per unique value of this column")
    p.add_argument("--row-number", action="store_true", dest="row_number",
                   help="Assign sequential row numbers instead of ranks")
    p.add_argument("--start", type=int, default=1,
                   help="Starting value for row-number mode (default: 1)")
    p.add_argument("-o", "--output", default=None,
                   help="Output CSV file (default: stdout)")
    p.set_defaults(func=run_rank)


def run_rank(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    headers = reader.headers()

    if args.row_number:
        ranked = list(row_number(
            reader.rows(),
            output_column=args.output_column,
            start=args.start,
            group_by=args.group_by,
        ))
    else:
        ranked = rank_rows(
            reader.rows(),
            sort_column=args.sort_column,
            output_column=args.output_column,
            method=args.method,
            ascending=not args.descending,
            group_by=args.group_by,
            numeric=args.numeric,
        )

    out_headers = headers + [args.output_column] if args.output_column not in headers else headers
    writer = StreamingCSVWriter(args.output or sys.stdout, fieldnames=out_headers)
    writer.write_rows(iter(ranked))
