"""Register the auto-cast sub-command."""
from csv_surgeon.cli_typecast_infer import add_typecast_infer_subparser


def register(subparsers) -> None:  # type: ignore[type-arg]
    add_typecast_infer_subparser(subparsers)
