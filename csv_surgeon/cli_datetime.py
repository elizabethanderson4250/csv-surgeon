"""CLI subcommand for datetime parsing/formatting transforms."""

import argparse
import sys
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon import datetime_parse


def add_datetime_subparser(subparsers) -> None:
    p = subparsers.add_parser("datetime", help="Parse or reformat date columns")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--output", "-o", required=True, help="Output CSV file")
    p.add_argument("--col", required=True, help="Column to transform")
    p.add_argument(
        "--mode",
        choices=["parse", "format", "extract"],
        required=True,
        help="Operation mode",
    )
    p.add_argument("--in-fmt", default="%Y-%m-%d", help="Input date format")
    p.add_argument("--out-fmt", default="%d/%m/%Y", help="Output date format (for format mode)")
    p.add_argument("--part", help="Date part to extract (year/month/day/weekday/hour/minute)")
    p.add_argument("--out-col", help="Target column name for extract mode")
    p.set_defaults(func=run_datetime)


def run_datetime(args) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.rows()

    if args.mode == "parse":
        transform = datetime_parse.parse_date(args.col, fmt=args.in_fmt)
        rows = datetime_parse.apply(rows, transform)
    elif args.mode == "format":
        transform = datetime_parse.format_date(args.col, in_fmt=args.in_fmt, out_fmt=args.out_fmt)
        rows = datetime_parse.apply(rows, transform)
    elif args.mode == "extract":
        if not args.part:
            print("--part is required for extract mode", file=sys.stderr)
            sys.exit(1)
        transform = datetime_parse.extract_part(
            args.col, args.part, in_fmt=args.in_fmt, out_col=args.out_col
        )
        rows = datetime_parse.apply(rows, transform)

    writer = StreamingCSVWriter(args.output)
    count = writer.write_rows(rows, fieldnames=reader.headers)
    print(f"Written {count} rows to {args.output}")
