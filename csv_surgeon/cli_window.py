"""CLI sub-commands for window/rolling operations."""
import argparse
import statistics
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.window import lag, rolling_aggregate

_FUNCS = {
    "mean": statistics.mean,
    "sum": sum,
    "min": min,
    "max": max,
}


def add_window_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("window", help="Rolling/window column operations")
    sub = p.add_subparsers(dest="window_cmd", required=True)

    roll = sub.add_parser("rolling", help="Rolling aggregate over a column")
    roll.add_argument("input", help="Input CSV file")
    roll.add_argument("output", help="Output CSV file")
    roll.add_argument("--column", required=True, help="Column to aggregate")
    roll.add_argument("--size", type=int, required=True, help="Window size")
    roll.add_argument(
        "--func",
        choices=list(_FUNCS.keys()),
        default="mean",
        help="Aggregate function",
    )
    roll.add_argument("--output-column", default=None, help="Name of the new column")

    lg = sub.add_parser("lag", help="Add a lagged column")
    lg.add_argument("input", help="Input CSV file")
    lg.add_argument("output", help="Output CSV file")
    lg.add_argument("--column", required=True, help="Column to lag")
    lg.add_argument("--periods", type=int, default=1, help="Number of periods to lag")
    lg.add_argument("--output-column", default=None, help="Name of the new column")
    lg.add_argument("--fill-value", default="", help="Fill value for initial rows")


def run_window(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    if args.window_cmd == "rolling":
        func = _FUNCS[args.func]
        result = rolling_aggregate(
            reader.rows(),
            column=args.column,
            size=args.size,
            func=func,
            output_column=args.output_column,
        )
    else:
        result = lag(
            reader.rows(),
            column=args.column,
            periods=args.periods,
            output_column=args.output_column,
            fill_value=args.fill_value,
        )
    rows = list(result)
    if not rows:
        StreamingCSVWriter(args.output).write_rows(iter([]), reader.headers)
        return
    headers = list(rows[0].keys())
    StreamingCSVWriter(args.output).write_rows(iter(rows), headers)
