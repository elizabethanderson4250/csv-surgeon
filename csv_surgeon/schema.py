"""Schema inference and enforcement for CSV files."""
from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, Optional


_TYPE_PRIORITY = ["integer", "float", "boolean", "string"]
_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0"}


def _infer_type(value: str) -> str:
    """Return the most specific type that fits *value*."""
    v = value.strip()
    if v == "":
        return "string"
    try:
        int(v)
        return "integer"
    except ValueError:
        pass
    try:
        float(v)
        return "float"
    except ValueError:
        pass
    if v.lower() in _BOOL_VALUES:
        return "boolean"
    return "string"


def _merge_types(a: str, b: str) -> str:
    """Return the least-specific type that covers both *a* and *b*."""
    if a == b:
        return a
    idx_a = _TYPE_PRIORITY.index(a) if a in _TYPE_PRIORITY else len(_TYPE_PRIORITY)
    idx_b = _TYPE_PRIORITY.index(b) if b in _TYPE_PRIORITY else len(_TYPE_PRIORITY)
    return _TYPE_PRIORITY[max(idx_a, idx_b)]


def infer_schema(rows: Iterable[Dict[str, str]]) -> Dict[str, str]:
    """Infer column types by scanning all *rows* (dicts).

    Returns a mapping of ``{column_name: type_string}``.
    """
    schema: Dict[str, str] = {}
    for row in rows:
        for col, val in row.items():
            inferred = _infer_type(val)
            if col not in schema:
                schema[col] = inferred
            else:
                schema[col] = _merge_types(schema[col], inferred)
    return schema


class SchemaViolation(Exception):
    """Raised when a row does not conform to the expected schema."""

    def __init__(self, column: str, value: str, expected_type: str) -> None:
        self.column = column
        self.value = value
        self.expected_type = expected_type
        super().__init__(
            f"Column '{column}': value {value!r} is not of type '{expected_type}'"
        )


def _cast(value: str, expected_type: str) -> bool:
    v = value.strip()
    if expected_type == "integer":
        try:
            int(v)
            return True
        except ValueError:
            return False
    if expected_type == "float":
        try:
            float(v)
            return True
        except ValueError:
            return False
    if expected_type == "boolean":
        return v.lower() in _BOOL_VALUES
    return True  # string always passes


def enforce_schema(
    rows: Iterable[Dict[str, str]],
    schema: Dict[str, str],
    strict: bool = False,
) -> Iterator[Dict[str, str]]:
    """Yield rows that conform to *schema*.

    If *strict* is True, raise :class:`SchemaViolation` on the first bad row;
    otherwise, silently skip non-conforming rows.
    """
    for row in rows:
        valid = True
        for col, expected_type in schema.items():
            val = row.get(col, "")
            if not _cast(val, expected_type):
                if strict:
                    raise SchemaViolation(col, val, expected_type)
                valid = False
                break
        if valid:
            yield row
