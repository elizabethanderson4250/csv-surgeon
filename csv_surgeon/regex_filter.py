"""Column-level regex filtering utilities."""
from __future__ import annotations

import re
from typing import Iterable, Iterator, Pattern


def _compile(pattern: str, ignore_case: bool) -> Pattern[str]:
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


def filter_by_regex(
    rows: Iterable[dict],
    column: str,
    pattern: str,
    *,
    ignore_case: bool = False,
    invert: bool = False,
) -> Iterator[dict]:
    """Yield rows where *column* matches (or doesn't match) *pattern*."""
    rx = _compile(pattern, ignore_case)
    for row in rows:
        value = row.get(column, "")
        matched = bool(rx.search(value))
        if invert:
            matched = not matched
        if matched:
            yield row


def filter_any_column(
    rows: Iterable[dict],
    pattern: str,
    *,
    ignore_case: bool = False,
    invert: bool = False,
) -> Iterator[dict]:
    """Yield rows where ANY column value matches *pattern*."""
    rx = _compile(pattern, ignore_case)
    for row in rows:
        matched = any(rx.search(v) for v in row.values())
        if invert:
            matched = not matched
        if matched:
            yield row


def filter_all_columns(
    rows: Iterable[dict],
    columns: list[str],
    pattern: str,
    *,
    ignore_case: bool = False,
) -> Iterator[dict]:
    """Yield rows where ALL specified columns match *pattern*."""
    rx = _compile(pattern, ignore_case)
    for row in rows:
        if all(rx.search(row.get(col, "")) for col in columns):
            yield row
