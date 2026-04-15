"""CLI subcommand for masking/redacting CSV columns."""

import argparse
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon import mask as mask_mod


def add_mask_subparser(subparsers) -> None:
    p = subparsers.add_parser("mask", help="Mask or redact column values")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--redact", metavar="COL", action="append", default=[],
        help="Fully redact column (repeatable)"
    )
    p.add_argument(
        "--mask-chars", metavar="COL:KEEP_LAST", action="append", default=[],
        help="Mask column chars, optionally keep last N (e.g. card:4)"
    )
    p.add_argument(
        "--mask-regex", metavar="COL:PATTERN", action="append", default=[],
        help="Mask regex matches in column (e.g. email:[^@]+@)"
    )
    p.set_defaults(func=run_mask)


def run_mask(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    masks = []

    for col in args.redact:
        masks.append(mask_mod.redact(col))

    for spec in args.mask_chars:
        parts = spec.split(":", 1)
        col = parts[0]
        keep_last = int(parts[1]) if len(parts) > 1 else 0
        masks.append(mask_mod.mask_chars(col, keep_last=keep_last))

    for spec in args.mask_regex:
        col, pattern = spec.split(":", 1)
        masks.append(mask_mod.mask_regex(col, pattern=pattern))

    masked_rows = mask_mod.apply_masks(reader.rows(), masks)
    writer = StreamingCSVWriter(args.output, fieldnames=reader.headers)
    writer.write_rows(masked_rows)
