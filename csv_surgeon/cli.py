"""Main CLI entry point for csv-surgeon."""
import argparse
import sys

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.pipeline import FilterPipeline
from csv_surgeon.transform_pipeline import TransformPipeline
from csv_surgeon import filters as F
from csv_surgeon import transforms as T
from csv_surgeon.cli_dedup import add_dedup_subparser, run_dedup
from csv_surgeon.cli_join import add_join_subparser, run_join
from csv_surgeon.cli_pivot import add_pivot_subparser, run_pivot
from csv_surgeon.cli_sample import add_sample_subparser, run_sample
from csv_surgeon.cli_validate import add_validate_subparser, run_validate
from csv_surgeon.cli_schema import add_schema_subparser, run_schema
from csv_surgeon.cli_sort import add_sort_subparser, run_sort
from csv_surgeon.cli_diff import add_diff_subparser, run_diff
from csv_surgeon.cli_aggregate import add_aggregate_subparser, run_aggregate
from csv_surgeon.cli_flatten import add_flatten_subparser, run_flatten


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-surgeon",
        description="Surgical column transformations and filtering on large CSV files.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # core filter/transform command
    process = subparsers.add_parser("process", help="Filter and transform a CSV file")
    process.add_argument("input", help="Input CSV file")
    process.add_argument("output", help="Output CSV file")
    process.add_argument(
        "--filter", dest="filters", action="append", metavar="RULE",
        help="Filter rule: column:op:value",
    )
    process.add_argument(
        "--transform", dest="transforms", action="append", metavar="RULE",
        help="Transform rule: column:op[:args]",
    )

    add_dedup_subparser(subparsers)
    add_join_subparser(subparsers)
    add_pivot_subparser(subparsers)
    add_sample_subparser(subparsers)
    add_validate_subparser(subparsers)
    add_schema_subparser(subparsers)
    add_sort_subparser(subparsers)
    add_diff_subparser(subparsers)
    add_aggregate_subparser(subparsers)
    add_flatten_subparser(subparsers)

    return parser


def parse_filter_rules(rules):
    pipeline = FilterPipeline()
    for rule in (rules or []):
        parts = rule.split(":")
        col, op = parts[0], parts[1]
        val = parts[2] if len(parts) > 2 else ""
        if op == "eq":
            pipeline.add_filter(F.equals(col, val))
        elif op == "ne":
            pipeline.add_filter(F.not_equals(col, val))
        elif op == "contains":
            pipeline.add_filter(F.contains(col, val))
        elif op == "gt":
            pipeline.add_filter(F.greater_than(col, float(val)))
        elif op == "lt":
            pipeline.add_filter(F.less_than(col, float(val)))
    return pipeline


def parse_transform_rules(rules):
    pipeline = TransformPipeline()
    for rule in (rules or []):
        parts = rule.split(":")
        col, op = parts[0], parts[1]
        if op == "upper":
            pipeline.add_transform(T.uppercase(col))
        elif op == "lower":
            pipeline.add_transform(T.lowercase(col))
        elif op == "strip":
            pipeline.add_transform(T.strip_whitespace(col))
        elif op == "rename" and len(parts) > 2:
            pipeline.add_transform(T.rename(col, parts[2]))
        elif op == "replace" and len(parts) > 3:
            pipeline.add_transform(T.replace(col, parts[2], parts[3]))
    return pipeline


def run(argv=None):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "process":
        reader = StreamingCSVReader(args.input)
        filter_pipeline = parse_filter_rules(args.filters)
        transform_pipeline = parse_transform_rules(args.transforms)
        rows = filter_pipeline.execute(reader.rows())
        rows = transform_pipeline.execute(rows)
        writer = StreamingCSVWriter(args.output, fieldnames=reader.headers)
        writer.write_rows(rows)
    elif args.command == "dedup":
        run_dedup(args)
    elif args.command == "join":
        run_join(args)
    elif args.command == "pivot":
        run_pivot(args)
    elif args.command == "sample":
        run_sample(args)
    elif args.command == "validate":
        run_validate(args)
    elif args.command == "schema":
        run_schema(args)
    elif args.command == "sort":
        run_sort(args)
    elif args.command == "diff":
        run_diff(args)
    elif args.command == "aggregate":
        run_aggregate(args)
    elif args.command == "flatten":
        run_flatten(args)
