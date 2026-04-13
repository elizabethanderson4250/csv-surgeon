"""CLI sub-command: aggregate — group and summarise CSV columns."""

import argparse
import sys

from csv_surgeon.aggregate import aggregate
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_aggregate_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser(
        "aggregate",
        help="Group rows and compute an aggregate over a numeric column.",
    )
    parser.add_argument("input", help="Path to input CSV file.")
    parser.add_argument("output", help="Path to write aggregated CSV file.")
    parser.add_argument(
        "--group-by",
        required=True,
        dest="group_by",
        help="Comma-separated list of columns to group by.",
    )
    parser.add_argument(
        "--agg-column",
        required=True,
        dest="agg_column",
        help="Column to aggregate.",
    )
    parser.add_argument(
        "--func",
        default="sum",
        choices=["sum", "count", "mean", "min", "max"],
        help="Aggregation function (default: sum).",
    )
    parser.add_argument(
        "--output-column",
        dest="output_column",
        default=None,
        help="Name for the result column (default: <agg_column>_<func>).",
    )
    parser.set_defaults(func=run_aggregate)


def run_aggregate(args: argparse.Namespace) -> None:
    group_cols = [c.strip() for c in args.group_by.split(",")]

    reader = StreamingCSVReader(args.input)
    rows = list(reader.rows())

    try:
        result = aggregate(
            rows,
            group_by_columns=group_cols,
            agg_column=args.agg_column,
            func=args.func,
            output_column=args.output_column,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not result:
        print("Warning: no rows produced.", file=sys.stderr)
        return

    writer = StreamingCSVWriter(args.output, fieldnames=list(result[0].keys()))
    writer.write_rows(iter(result))
