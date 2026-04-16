"""CLI sub-commands for lookup enrichment and filtering."""
from __future__ import annotations
import argparse
import csv
import sys

from csv_surgeon.lookup import lookup_enrich, lookup_filter
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_lookup_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("lookup", help="Enrich or filter rows via a reference CSV")
    sub = p.add_subparsers(dest="lookup_cmd", required=True)

    # enrich
    enrich = sub.add_parser("enrich", help="Add a column from a reference CSV")
    enrich.add_argument("input", help="Primary CSV file")
    enrich.add_argument("ref", help="Reference CSV file")
    enrich.add_argument("--src-col", required=True, help="Column in primary CSV to match on")
    enrich.add_argument("--ref-key", required=True, help="Key column in reference CSV")
    enrich.add_argument("--ref-value", required=True, help="Value column in reference CSV")
    enrich.add_argument("--dest-col", default=None, help="Destination column name (default: ref-value)")
    enrich.add_argument("--default", default="", help="Default when no match found")
    enrich.add_argument("-o", "--output", required=True, help="Output CSV file")

    # filter
    filt = sub.add_parser("filter", help="Filter rows using a reference CSV")
    filt.add_argument("input", help="Primary CSV file")
    filt.add_argument("ref", help="Reference CSV file")
    filt.add_argument("--src-col", required=True)
    filt.add_argument("--ref-key", required=True)
    filt.add_argument("--exclude", action="store_true", help="Exclude matching rows instead")
    filt.add_argument("-o", "--output", required=True)


def _read_rows(path: str):
    reader = StreamingCSVReader(path)
    return list(reader.rows())


def run_lookup(args: argparse.Namespace) -> None:
    primary = _read_rows(args.input)
    ref = _read_rows(args.ref)

    if args.lookup_cmd == "enrich":
        result = list(lookup_enrich(
            primary, ref,
            src_col=args.src_col,
            ref_key_col=args.ref_key,
            ref_value_col=args.ref_value,
            dest_col=args.dest_col,
            default=args.default,
        ))
    else:
        result = list(lookup_filter(
            primary, ref,
            src_col=args.src_col,
            ref_key_col=args.ref_key,
            exclude=args.exclude,
        ))

    if not result:
        print("No rows to write.", file=sys.stderr)
        return

    writer = StreamingCSVWriter(args.output, fieldnames=list(result[0].keys()))
    writer.write_rows(iter(result))
