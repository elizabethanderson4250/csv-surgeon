"""CLI subcommand for joining two CSV files."""

import argparse
import sys
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.join import inner_join, left_join


def add_join_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "join",
        help="Join two CSV files on a common key column.",
    )
    parser.add_argument("left", help="Path to the left (primary) CSV file.")
    parser.add_argument("right", help="Path to the right (lookup) CSV file.")
    parser.add_argument("--left-on", required=True, dest="left_on", help="Join key column in left file.")
    parser.add_argument("--right-on", required=True, dest="right_on", help="Join key column in right file.")
    parser.add_argument(
        "--how",
        choices=["inner", "left"],
        default="inner",
        help="Join type: 'inner' (default) or 'left'.",
    )
    parser.add_argument(
        "--right-prefix",
        default="right_",
        dest="right_prefix",
        help="Prefix for conflicting right-side column names (default: 'right_').",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV path (default: stdout).")


def run_join(args: argparse.Namespace) -> None:
    left_reader = StreamingCSVReader(args.left)
    right_reader = StreamingCSVReader(args.right)

    left_rows = left_reader.rows()
    right_rows = list(right_reader.rows())  # right side loaded into memory

    if args.how == "inner":
        joined = inner_join(left_rows, right_rows, args.left_on, args.right_on, args.right_prefix)
    else:
        joined = left_join(left_rows, right_rows, args.left_on, args.right_on, args.right_prefix)

    joined_list = list(joined)
    if not joined_list:
        if args.output:
            open(args.output, "w").close()
        return

    fieldnames = list(joined_list[0].keys())
    writer = StreamingCSVWriter(args.output, fieldnames=fieldnames)
    writer.write_rows(iter(joined_list))
