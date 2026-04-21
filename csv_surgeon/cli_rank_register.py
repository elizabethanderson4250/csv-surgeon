"""Register the 'rank' sub-command with the main CLI parser."""
from csv_surgeon.cli_rank import add_rank_subparser


def register(subparsers) -> None:  # type: ignore[type-arg]
    """Called by cli.py to attach the rank sub-command."""
    add_rank_subparser(subparsers)
