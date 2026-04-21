"""CLI sub-commands for percentile operations."""

from __future__ import annotations

import argparse
import csv
import sys

from csv_surgeon.percentile import compute_percentiles, flag_percentile_band
from csv_surgeon.writer import StreamingCSVWriter


def add_percentile_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("percentile", help="Percentile utilities")
    sub = p.add_subparsers(dest="percentile_cmd", required=True)

    # --- compute sub-command ---
    pc = sub.add_parser("compute", help="Print percentile values for a column")
    pc.add_argument("input", help="Input CSV file (use - for stdin)")
    pc.add_argument("--column", required=True, help="Column to analyse")
    pc.add_argument(
        "--percentiles",
        default="25,50,75",
        help="Comma-separated percentile values (default: 25,50,75)",
    )

    # --- band sub-command ---
    pb = sub.add_parser("band", help="Annotate rows with low/mid/high band")
    pb.add_argument("input", help="Input CSV file (use - for stdin)")
    pb.add_argument("output", help="Output CSV file (use - for stdout)")
    pb.add_argument("--column", required=True, help="Column to evaluate")
    pb.add_argument("--lower", type=float, default=25.0, help="Lower percentile boundary")
    pb.add_argument("--upper", type=float, default=75.0, help="Upper percentile boundary")
    pb.add_argument("--out-column", default="percentile_band", help="Output column name")


def _open_input(path: str):
    if path == "-":
        return csv.DictReader(sys.stdin)
    fh = open(path, newline="", encoding="utf-8")
    return csv.DictReader(fh)


def run_percentile(args: argparse.Namespace) -> None:
    reader = _open_input(args.input)
    rows = list(reader)

    if args.percentile_cmd == "compute":
        ps = [float(p.strip()) for p in args.percentiles.split(",")]
        result = compute_percentiles(rows, args.column, ps)
        for key, val in sorted(result.items(), key=lambda kv: float(kv[0][1:])):
            print(f"{key}: {val}")

    elif args.percentile_cmd == "band":
        annotated = flag_percentile_band(
            rows,
            column=args.column,
            lower=args.lower,
            upper=args.upper,
            output_column=args.out_column,
        )
        annotated_list = list(annotated)
        if not annotated_list:
            return
        fieldnames = list(annotated_list[0].keys())
        writer = StreamingCSVWriter(args.output, fieldnames=fieldnames)
        writer.write_rows(annotated_list)
