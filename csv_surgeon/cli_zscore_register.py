"""Register the zscore sub-command with the main CLI."""
from csv_surgeon.cli_zscore import add_zscore_subparser


def register(subparsers):
    add_zscore_subparser(subparsers)
