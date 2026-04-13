"""CLI subcommands: pivot and unpivot."""
import argparse
import csv
import sys
from csv_surgeon.pivot import pivot, unpivot
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_pivot_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("pivot", help="Pivot CSV rows into wide format")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--index", required=True, help="Index column")
    p.add_argument("--pivot-col", required=True, dest="pivot_col", help="Column to pivot")
    p.add_argument("--value-col", required=True, dest="value_col", help="Values column")
    p.add_argument(
        "--agg",
        default="first",
        choices=["first", "last", "sum", "count"],
        help="Aggregation for duplicate (index, pivot) pairs (default: first)",
    )
    p.set_defaults(func=run_pivot)

    u = subparsers.add_parser("unpivot", help="Unpivot (melt) CSV columns into long format")
    u.add_argument("input", help="Input CSV file")
    u.add_argument("output", help="Output CSV file")
    u.add_argument("--id-cols", required=True, dest="id_cols", help="Comma-separated id columns")
    u.add_argument("--variable-col", default="variable", dest="variable_col")
    u.add_argument("--value-col", default="value", dest="value_col")
    u.add_argument(
        "--columns",
        default="",
        help="Comma-separated columns to melt (default: all non-id columns)",
    )
    u.set_defaults(func=run_unpivot)


def run_pivot(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    pivoted = pivot(
        reader.rows(),
        index_col=args.index,
        pivot_col=args.pivot_col,
        value_col=args.value_col,
        agg=args.agg,
    )
    if not pivoted:
        print("No rows produced.", file=sys.stderr)
        return
    writer = StreamingCSVWriter(args.output, fieldnames=list(pivoted[0].keys()))
    writer.write_rows(iter(pivoted))


def run_unpivot(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    id_cols = [c.strip() for c in args.id_cols.split(",") if c.strip()]
    melt_cols = [c.strip() for c in args.columns.split(",") if c.strip()]
    melted = unpivot(
        reader.rows(),
        id_cols=id_cols,
        value_col=args.value_col,
        variable_col=args.variable_col,
        columns=melt_cols or None,
    )
    # peek at first row to get fieldnames
    try:
        first = next(melted)
    except StopIteration:
        print("No rows produced.", file=sys.stderr)
        return
    import itertools
    writer = StreamingCSVWriter(args.output, fieldnames=list(first.keys()))
    writer.write_rows(itertools.chain([first], melted))
