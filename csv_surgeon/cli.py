"""Main CLI entry point for csv-surgeon."""

import argparse
from csv_surgeon.cli_dedup import add_dedup_subparser
from csv_surgeon.cli_join import add_join_subparser
from csv_surgeon.cli_pivot import add_pivot_subparser
from csv_surgeon.cli_sample import add_sample_subparser
from csv_surgeon.cli_validate import add_validate_subparser
from csv_surgeon.cli_schema import add_schema_subparser
from csv_surgeon.cli_sort import add_sort_subparser
from csv_surgeon.cli_diff import add_diff_subparser
from csv_surgeon.cli_aggregate import add_aggregate_subparser
from csv_surgeon.cli_flatten import add_flatten_subparser
from csv_surgeon.cli_cast import add_cast_subparser
from csv_surgeon.cli_window import add_window_subparser
from csv_surgeon.cli_mask import add_mask_subparser
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.pipeline import FilterPipeline
from csv_surgeon.transform_pipeline import TransformPipeline
from csv_surgeon import filters as f
from csv_surgeon import transforms as t


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-surgeon",
        description="Surgical column transformations and filtering on CSV files."
    )
    subparsers = parser.add_subparsers(dest="command")

    # filter/transform subcommand
    p = subparsers.add_parser("run", help="Filter and transform a CSV file")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--filter", dest="filters", action="append", default=[], metavar="COL:OP:VAL")
    p.add_argument("--transform", dest="transforms", action="append", default=[], metavar="COL:OP:VAL")
    p.set_defaults(func=run)

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
    add_cast_subparser(subparsers)
    add_window_subparser(subparsers)
    add_mask_subparser(subparsers)

    return parser


def parse_filter_rules(rules: list):
    filter_map = {
        "eq": f.equals,
        "ne": f.not_equals,
        "contains": f.contains,
        "gt": f.greater_than,
        "lt": f.less_than,
        "gte": f.greater_than_or_equal,
        "lte": f.less_than_or_equal,
        "matches": f.matches,
    }
    result = []
    for rule in rules:
        col, op, val = rule.split(":", 2)
        result.append(filter_map[op](col, val))
    return result


def parse_transform_rules(rules: list):
    transform_map = {
        "uppercase": lambda col, val: t.uppercase(col),
        "lowercase": lambda col, val: t.lowercase(col),
        "strip": lambda col, val: t.strip_whitespace(col),
        "replace": lambda col, val: t.replace(col, *val.split(",", 1)),
        "rename": lambda col, val: t.rename(col, val),
    }
    result = []
    for rule in rules:
        col, op, val = rule.split(":", 2)
        result.append(transform_map[op](col, val))
    return result


def run(args) -> None:
    reader = StreamingCSVReader(args.input)
    filter_fns = parse_filter_rules(args.filters)
    transform_fns = parse_transform_rules(args.transforms)

    pipeline = FilterPipeline()
    for fn in filter_fns:
        pipeline.add_filter(fn)

    transform_pipeline = TransformPipeline(reader.headers)
    for fn in transform_fns:
        transform_pipeline.add_transform(fn)

    filtered = pipeline.execute(reader.rows())
    transformed = transform_pipeline.execute(filtered)

    writer = StreamingCSVWriter(args.output, fieldnames=transform_pipeline.headers)
    writer.write_rows(transformed)


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
