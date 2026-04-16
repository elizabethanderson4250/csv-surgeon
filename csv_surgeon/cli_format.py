"""CLI subcommand for column formatting."""
import argparse
import csv
import sys
from csv_surgeon import format as fmt
from csv_surgeon.transform_pipeline import TransformPipeline
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def add_format_subparser(subparsers) -> None:
    p = subparsers.add_parser("format", help="Format column values")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--output", "-o", required=True, help="Output CSV file")
    p.add_argument("--zero-pad", nargs=2, metavar=("COL", "WIDTH"), action="append", default=[])
    p.add_argument("--title-case", metavar="COL", action="append", default=[])
    p.add_argument("--wrap", nargs=3, metavar=("COL", "PREFIX", "SUFFIX"), action="append", default=[])
    p.add_argument("--number-format", nargs=2, metavar=("COL", "DECIMALS"), action="append", default=[])
    p.add_argument("--strip", metavar="COL", action="append", default=[])
    p.add_argument("--remove-non-alphanumeric", metavar="COL", action="append", default=[])
    p.set_defaults(func=run_format)


def run_format(args) -> None:
    pipeline = TransformPipeline()

    for col, width in args.zero_pad:
        pipeline.add_transform(fmt.zero_pad(col, int(width)))
    for col in args.title_case:
        pipeline.add_transform(fmt.title_case(col))
    for col, prefix, suffix in args.wrap:
        pipeline.add_transform(fmt.wrap(col, prefix, suffix))
    for col, decimals in args.number_format:
        pipeline.add_transform(fmt.number_format(col, int(decimals)))
    for col in args.strip:
        pipeline.add_transform(fmt.strip_chars(col))
    for col in args.remove_non_alphanumeric:
        pipeline.add_transform(fmt.remove_non_alphanumeric(col))

    reader = StreamingCSVReader(args.input)
    writer = StreamingCSVWriter(args.output, headers=reader.headers)
    writer.write_rows(pipeline.execute(reader.rows()))
