"""Column validation utilities for csv-surgeon."""

import re
from typing import Callable, Dict, Iterable, Iterator, List, Optional


def _validator(func: Callable) -> Callable:
    """Decorator that marks a function as a validator factory."""
    return func


@_validator
def required(column: str) -> Callable[[Dict], Optional[str]]:
    """Fail if the column value is empty or missing."""
    def _validate(row: Dict) -> Optional[str]:
        val = row.get(column, "")
        if val is None or str(val).strip() == "":
            return f"{column}: value is required"
        return None
    return _validate


@_validator
def is_numeric(column: str) -> Callable[[Dict], Optional[str]]:
    """Fail if the column value cannot be parsed as a number."""
    def _validate(row: Dict) -> Optional[str]:
        val = row.get(column, "")
        try:
            float(val)
            return None
        except (TypeError, ValueError):
            return f"{column}: '{val}' is not numeric"
    return _validate


@_validator
def max_length(column: str, length: int) -> Callable[[Dict], Optional[str]]:
    """Fail if the column value exceeds the given character length."""
    def _validate(row: Dict) -> Optional[str]:
        val = str(row.get(column, ""))
        if len(val) > length:
            return f"{column}: '{val}' exceeds max length {length}"
        return None
    return _validate


@_validator
def matches_pattern(column: str, pattern: str) -> Callable[[Dict], Optional[str]]:
    """Fail if the column value does not match the given regex pattern."""
    compiled = re.compile(pattern)

    def _validate(row: Dict) -> Optional[str]:
        val = str(row.get(column, ""))
        if not compiled.search(val):
            return f"{column}: '{val}' does not match pattern '{pattern}'"
        return None
    return _validate


def validate_rows(
    rows: Iterable[Dict],
    validators: List[Callable[[Dict], Optional[str]]],
    fail_fast: bool = False,
) -> Iterator[Dict]:
    """
    Yield rows that pass all validators.
    Rows that fail any validator are skipped.
    If fail_fast is True, raises ValueError on first invalid row.
    """
    for row in rows:
        errors = [v(row) for v in validators]
        errors = [e for e in errors if e is not None]
        if errors:
            if fail_fast:
                raise ValueError(f"Validation failed: {'; '.join(errors)}")
            continue
        yield row
