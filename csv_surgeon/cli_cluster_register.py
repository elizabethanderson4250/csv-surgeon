"""Register the 'cluster' sub-command with the main CLI."""
from __future__ import annotations

from csv_surgeon.cli_cluster import add_cluster_subparser


def register(subparsers) -> None:
    add_cluster_subparser(subparsers)
