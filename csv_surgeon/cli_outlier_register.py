"""Register the outlier sub-command with the main CLI."""
from csv_surgeon.cli_outlier import add_outlier_subparser


def register(subparsers) -> None:
    add_outlier_subparser(subparsers)
