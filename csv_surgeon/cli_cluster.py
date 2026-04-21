"""CLI sub-command: cluster."""
from __future__ import annotations

import argparse

from csv_surgeon.cluster import cluster_by_soundex, cluster_by_value
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_cluster_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "cluster",
        help="Annotate rows with a cluster key derived from a column value.",
    )
    p.add_argument("input", help="Input CSV file.")
    p.add_argument("output", help="Output CSV file.")
    p.add_argument("--column", required=True, help="Column to cluster on.")
    p.add_argument(
        "--output-column",
        default="cluster_key",
        dest="output_column",
        help="Name of the new cluster-key column (default: cluster_key).",
    )
    p.add_argument(
        "--method",
        choices=["exact", "soundex"],
        default="exact",
        help="Clustering method (default: exact).",
    )
    p.set_defaults(func=run_cluster)


def run_cluster(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.rows()

    if args.method == "soundex":
        clustered = cluster_by_soundex(rows, args.column, args.output_column)
    else:
        clustered = cluster_by_value(rows, args.column, args.output_column)

    # Peek at the first row to discover headers (including the new column)
    first = next(clustered, None)
    if first is None:
        StreamingCSVWriter(args.output, reader.headers + [args.output_column]).write_rows(iter([]))
        return

    out_headers = list(first.keys())
    writer = StreamingCSVWriter(args.output, out_headers)
    writer.write_rows(row for row in ([first] + list(clustered)))
