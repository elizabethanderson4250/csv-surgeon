import argparse
import sys
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.pipeline import FilterPipeline
from csv_surgeon.transform_pipeline import TransformPipeline
import csv_surgeon.filters as filters
import csv_surgeon.transforms as transforms


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-surgeon",
        description="Surgical column transformations and filtering on large CSV files.",
    )
    parser.add_argument("input", help="Path to input CSV file")
    parser.add_argument("-o", "--output", help="Path to output CSV file (default: stdout)")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: comma)")
    parser.add_argument(
        "--filter",
        action="append",
        metavar="COL:OP:VALUE",
        dest="filter_rules",
        help="Filter rule in format column:operator:value (e.g. age:gt:18)",
    )
    parser.add_argument(
        "--transform",
        action="append",
        metavar="COL:OP[:VALUE]",
        dest="transform_rules",
        help="Transform rule in format column:operation[:value] (e.g. name:uppercase)",
    )
    return parser


FILTER_MAP = {
    "eq": filters.equals,
    "neq": filters.not_equals,
    "contains": filters.contains,
    "gt": filters.greater_than,
    "lt": filters.less_than,
}

TRANSFORM_MAP = {
    "uppercase": transforms.uppercase,
    "lowercase": transforms.lowercase,
    "strip": transforms.strip_whitespace,
    "rename": transforms.rename,
    "replace": transforms.replace,
}


def parse_filter_rules(rules):
    pipeline = FilterPipeline()
    for rule in (rules or []):
        parts = rule.split(":", 2)
        if len(parts) < 3:
            print(f"Invalid filter rule: {rule}", file=sys.stderr)
            sys.exit(1)
        col, op, val = parts
        if op not in FILTER_MAP:
            print(f"Unknown filter operator: {op}", file=sys.stderr)
            sys.exit(1)
        pipeline.add_filter(FILTER_MAP[op](col, val))
    return pipeline


def parse_transform_rules(rules):
    pipeline = TransformPipeline()
    for rule in (rules or []):
        parts = rule.split(":", 2)
        col, op = parts[0], parts[1]
        val = parts[2] if len(parts) > 2 else None
        if op not in TRANSFORM_MAP:
            print(f"Unknown transform operation: {op}", file=sys.stderr)
            sys.exit(1)
        pipeline.add_transform(TRANSFORM_MAP[op](col, val) if val else TRANSFORM_MAP[op](col))
    return pipeline


def run(args=None):
    parser = build_arg_parser()
    parsed = parser.parse_args(args)

    reader = StreamingCSVReader(parsed.input, delimiter=parsed.delimiter)
    filter_pipeline = parse_filter_rules(parsed.filter_rules)
    transform_pipeline = parse_transform_rules(parsed.transform_rules)

    filtered = filter_pipeline.execute(reader.rows())
    transformed = transform_pipeline.execute(filtered)

    if parsed.output:
        writer = StreamingCSVWriter(parsed.output, reader.headers(), delimiter=parsed.delimiter)
        count = writer.write_rows(transformed)
        print(f"Written {count} rows to {parsed.output}")
    else:
        import csv, io
        out = io.TextIOWrapper(sys.stdout.buffer, newline="")
        w = csv.DictWriter(out, fieldnames=reader.headers(), delimiter=parsed.delimiter)
        w.writeheader()
        for row in transformed:
            w.writerow(row)


if __name__ == "__main__":
    run()
