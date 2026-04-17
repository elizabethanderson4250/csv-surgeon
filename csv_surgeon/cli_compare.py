"""CLI sub-commands for column comparison operations."""
import argparse
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.compare import compare_column, flag_changed, diff_columns


def add_compare_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("compare", help="Column comparison utilities")
    sub = p.add_subparsers(dest="compare_cmd", required=True)

    cmp = sub.add_parser("cmp", help="Compare two columns (-1/0/1)")
    cmp.add_argument("input")
    cmp.add_argument("--col-a", required=True)
    cmp.add_argument("--col-b", required=True)
    cmp.add_argument("--result-col", default="_cmp")
    cmp.add_argument("--output", required=True)

    chg = sub.add_parser("flag-changed", help="Flag rows where columns changed")
    chg.add_argument("input")
    chg.add_argument("--columns", required=True, help="Comma-separated column names")
    chg.add_argument("--flag-col", default="_changed")
    chg.add_argument("--output", required=True)

    dif = sub.add_parser("diff", help="Numeric difference between two columns")
    dif.add_argument("input")
    dif.add_argument("--col-a", required=True)
    dif.add_argument("--col-b", required=True)
    dif.add_argument("--result-col", default="_diff")
    dif.add_argument("--output", required=True)

    p.set_defaults(func=run_compare)


def run_compare(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.rows()

    if args.compare_cmd == "cmp":
        result = compare_column(rows, args.col_a, args.col_b, args.result_col)
    elif args.compare_cmd == "flag-changed":
        cols = [c.strip() for c in args.columns.split(",")]
        result = flag_changed(rows, cols, args.flag_col)
    elif args.compare_cmd == "diff":
        result = diff_columns(rows, args.col_a, args.col_b, args.result_col)
    else:
        raise ValueError(f"Unknown compare sub-command: {args.compare_cmd}")

    writer = StreamingCSVWriter(args.output)
    writer.write_rows(result)
