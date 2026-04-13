"""Streaming-friendly CSV row sorting utilities."""

from typing import Iterable, Iterator, List, Optional


def sort_rows(
    rows: Iterable[dict],
    key_columns: List[str],
    reverse: bool = False,
    numeric: bool = False,
) -> Iterator[dict]:
    """Sort rows by one or more columns.

    Loads all rows into memory to perform the sort, then yields them in order.

    Args:
        rows: Iterable of row dicts.
        key_columns: Column names to sort by (in priority order).
        reverse: If True, sort descending.
        numeric: If True, attempt numeric comparison for each key column.

    Yields:
        Sorted row dicts.
    """
    if not key_columns:
        raise ValueError("At least one key column must be specified.")

    def sort_key(row: dict):
        values = []
        for col in key_columns:
            val = row.get(col, "")
            if numeric:
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    val = float("-inf") if not reverse else float("inf")
            values.append(val)
        return values

    collected = list(rows)
    collected.sort(key=sort_key, reverse=reverse)
    yield from collected


def sort_by_key_func(
    rows: Iterable[dict],
    key_func,
    reverse: bool = False,
) -> Iterator[dict]:
    """Sort rows using a custom key function.

    Args:
        rows: Iterable of row dicts.
        key_func: Callable that accepts a row dict and returns a sort key.
        reverse: If True, sort descending.

    Yields:
        Sorted row dicts.
    """
    collected = list(rows)
    collected.sort(key=key_func, reverse=reverse)
    yield from collected
