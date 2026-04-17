"""CLI subcommand for binning a numeric column."""
from __future__ import annotations

import argparse
from typing import List

from csv_surgeon.bin_column import bin_fixed, bin_quantile
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_bin_column_subparser(subparsers) -> None:
    p: argparse.ArgumentParser = subparsers.add_parser(
        "bin", help="Bucket a numeric column into labelled bins"
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to bin")
    p.add_argument("--output-column", default=None, help="Name for the new bin column")
    p.add_argument("--default", default="", help="Value for rows that don't fit any bin")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--edges",
        nargs="+",
        type=float,
        metavar="EDGE",
        help="Fixed bin edges (at least 2 values)",
    )
    mode.add_argument(
        "--quantiles",
        type=int,
        metavar="N",
        help="Number of quantile bins",
    )
    p.add_argument(
        "--labels",
        nargs="+",
        default=None,
        help="Custom labels for fixed bins (must match len(edges)-1)",
    )


def run_bin_column(args) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.rows()
    if args.edges:
        binned = bin_fixed(
            rows,
            column=args.column,
            edges=args.edges,
            labels=args.labels,
            output_column=args.output_column,
            default=args.default,
        )
    else:
        binned = bin_quantile(
            rows,
            column=args.column,
            n_quantiles=args.quantiles,
            output_column=args.output_column,
            default=args.default,
        )
    first = next(binned, None)
    if first is None:
        StreamingCSVWriter(args.output).write_rows(iter([]), fieldnames=reader.headers)
        return
    headers = list(first.keys())
    writer = StreamingCSVWriter(args.output)
    import itertools
    writer.write_rows(itertools.chain([first], binned), fieldnames=headers)
