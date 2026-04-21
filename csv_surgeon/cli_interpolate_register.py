"""Register the interpolate sub-command with the main CLI."""
from csv_surgeon.cli_interpolate import add_interpolate_subparser


def register(subparsers) -> None:  # type: ignore[type-arg]
    add_interpolate_subparser(subparsers)
