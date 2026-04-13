"""Column transformation functions for csv-surgeon."""

import re
from typing import Callable, Any


def rename(new_name: str) -> Callable[[str, dict], tuple[str, Any]]:
    """Rename a column to a new name."""
    def _transform(col: str, row: dict) -> tuple[str, Any]:
        return new_name, row[col]
    return _transform


def uppercase() -> Callable[[str, dict], tuple[str, Any]]:
    """Transform column value to uppercase."""
    def _transform(col: str, row: dict) -> tuple[str, Any]:
        return col, str(row[col]).upper()
    return _transform


def lowercase() -> Callable[[str, dict], tuple[str, Any]]:
    """Transform column value to lowercase."""
    def _transform(col: str, row: dict) -> tuple[str, Any]:
        return col, str(row[col]).lower()
    return _transform


def strip_whitespace() -> Callable[[str, dict], tuple[str, Any]]:
    """Strip leading and trailing whitespace from column value."""
    def _transform(col: str, row: dict) -> tuple[str, Any]:
        return col, str(row[col]).strip()
    return _transform


def replace(old: str, new: str) -> Callable[[str, dict], tuple[str, Any]]:
    """Replace occurrences of old with new in column value."""
    def _transform(col: str, row: dict) -> tuple[str, Any]:
        return col, str(row[col]).replace(old, new)
    return _transform


def regex_replace(pattern: str, replacement: str) -> Callable[[str, dict], tuple[str, Any]]:
    """Replace regex pattern matches with replacement in column value."""
    compiled = re.compile(pattern)

    def _transform(col: str, row: dict) -> tuple[str, Any]:
        return col, compiled.sub(replacement, str(row[col]))
    return _transform


def cast(type_fn: Callable) -> Callable[[str, dict], tuple[str, Any]]:
    """Cast column value using the provided callable (e.g. int, float, str)."""
    def _transform(col: str, row: dict) -> tuple[str, Any]:
        return col, type_fn(row[col])
    return _transform


def apply(fn: Callable[[Any], Any]) -> Callable[[str, dict], tuple[str, Any]]:
    """Apply an arbitrary function to the column value."""
    def _transform(col: str, row: dict) -> tuple[str, Any]:
        return col, fn(row[col])
    return _transform
