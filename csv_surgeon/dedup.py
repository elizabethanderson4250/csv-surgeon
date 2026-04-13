"""Deduplication utilities for streaming CSV rows."""
from typing import Callable, Generator, Iterable, List, Optional


def dedup_by_columns(
    rows: Iterable[dict],
    columns: List[str],
    keep: str = "first",
) -> Generator[dict, None, None]:
    """Yield rows deduplicated by the given column(s).

    Args:
        rows: Iterable of row dicts.
        columns: Column names to form the dedup key.
        keep: 'first' keeps the first occurrence; 'last' keeps the last.
              'last' requires buffering all rows — use with caution on large files.

    Yields:
        Unique rows according to the dedup key.
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    if keep == "first":
        seen = set()
        for row in rows:
            key = _make_key(row, columns)
            if key not in seen:
                seen.add(key)
                yield row
    else:  # last
        latest: dict = {}
        order: list = []
        for row in rows:
            key = _make_key(row, columns)
            if key not in latest:
                order.append(key)
            latest[key] = row
        for key in order:
            yield latest[key]


def dedup_by_key_func(
    rows: Iterable[dict],
    key_func: Callable[[dict], object],
    keep: str = "first",
) -> Generator[dict, None, None]:
    """Yield rows deduplicated using a custom key function.

    Args:
        rows: Iterable of row dicts.
        key_func: Callable that receives a row dict and returns a hashable key.
        keep: 'first' or 'last'.

    Yields:
        Unique rows according to key_func.
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    if keep == "first":
        seen = set()
        for row in rows:
            key = key_func(row)
            if key not in seen:
                seen.add(key)
                yield row
    else:
        latest: dict = {}
        order: list = []
        for row in rows:
            key = key_func(row)
            if key not in latest:
                order.append(key)
            latest[key] = row
        for key in order:
            yield latest[key]


def _make_key(row: dict, columns: List[str]) -> tuple:
    """Build a hashable tuple key from specified columns of a row."""
    return tuple(row.get(col, "") for col in columns)
