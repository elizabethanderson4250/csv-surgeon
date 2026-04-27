"""Register the regex-filter subcommand with the main CLI."""
from csv_surgeon.cli_regex_filter import add_regex_filter_subparser


def register(subparsers) -> None:
    add_regex_filter_subparser(subparsers)
