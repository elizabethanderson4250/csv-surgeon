"""Register the format subcommand into the main CLI.

This module is imported by cli.py to attach the 'format' subcommand
to the shared argument parser.
"""
from csv_surgeon.cli_format import add_format_subparser


def register(subparsers) -> None:
    """Attach the format subcommand to the provided subparsers action."""
    add_format_subparser(subparsers)
