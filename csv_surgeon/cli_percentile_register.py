"""Register the percentile sub-command with the main CLI."""

from __future__ import annotations

from csv_surgeon.cli_percentile import add_percentile_subparser, run_percentile


def register(subparsers, command_map: dict) -> None:
    """Attach the *percentile* sub-parser and map it to its runner."""
    add_percentile_subparser(subparsers)
    command_map["percentile"] = run_percentile
