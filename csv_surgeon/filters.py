"""Row filtering utilities for csv-surgeon."""

from typing import Callable, Dict, Any, List, Optional
import re


RowDict = Dict[str, Any]
FilterFunc = Callable[[RowDict], bool]


def equals(column: str, value: str) -> FilterFunc:
    """Return rows where column value equals the given string."""
    def _filter(row: RowDict) -> bool:
        return row.get(column) == value
    return _filter


def not_equals(column: str, value: str) -> FilterFunc:
    """Return rows where column value does not equal the given string."""
    def _filter(row: RowDict) -> bool:
        return row.get(column) != value
    return _filter


def contains(column: str, substring: str) -> FilterFunc:
    """Return rows where column value contains the given substring."""
    def _filter(row: RowDict) -> bool:
        val = row.get(column, "")
        return substring in (val or "")
    return _filter


def matches(column: str, pattern: str) -> FilterFunc:
    """Return rows where column value matches the given regex pattern."""
    compiled = re.compile(pattern)

    def _filter(row: RowDict) -> bool:
        val = row.get(column, "") or ""
        return bool(compiled.search(val))
    return _filter


def greater_than(column: str, value: float) -> FilterFunc:
    """Return rows where column value (numeric) is greater than the given value."""
    def _filter(row: RowDict) -> bool:
        try:
            return float(row.get(column, 0)) > value
        except (ValueError, TypeError):
            return False
    return _filter


def less_than(column: str, value: float) -> FilterFunc:
    """Return rows where column value (numeric) is less than the given value."""
    def _filter(row: RowDict) -> bool:
        try:
            return float(row.get(column, 0)) < value
        except (ValueError, TypeError):
            return False
    return _filter


def combine_and(*filters: FilterFunc) -> FilterFunc:
    """Combine multiple filters with logical AND."""
    def _filter(row: RowDict) -> bool:
        return all(f(row) for f in filters)
    return _filter


def combine_or(*filters: FilterFunc) -> FilterFunc:
    """Combine multiple filters with logical OR."""
    def _filter(row: RowDict) -> bool:
        return any(f(row) for f in filters)
    return _filter


def apply_filters(rows, *filters: FilterFunc):
    """Generator that yields rows passing all provided filters."""
    combined = combine_and(*filters) if len(filters) > 1 else filters[0]
    for row in rows:
        if combined(row):
            yield row
