"""Register the annotate sub-command with the main CLI parser."""
from csv_surgeon.cli_annotate import add_annotate_subparser


def register(subparsers) -> None:
    add_annotate_subparser(subparsers)
