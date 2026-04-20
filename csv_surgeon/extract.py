"""Column value extraction utilities: regex capture groups, substring, and split-index."""

import re
from typing import Iterable, Iterator


def _extractor(func):
    """Decorator that wraps a scalar extraction function into a row-level transform."""
    def _transform(column: str, output_column: str = None, default: str = "", **kwargs):
        dest = output_column or column

        def apply(row: dict) -> dict:
            result = dict(row)
            value = row.get(column, "")
            try:
                result[dest] = func(value, **kwargs)
            except Exception:
                result[dest] = default
            return result

        return apply
    _transform.__name__ = func.__name__
    return _transform


@_extractor
def extract_regex(value: str, pattern: str, group: int = 1) -> str:
    """Extract a capture group from *value* using *pattern*.

    Returns the matched group string, or empty string when there is no match.
    """
    match = re.search(pattern, value)
    if match is None:
        return ""
    return match.group(group)


@_extractor
def extract_substring(value: str, start: int = 0, end: int = None) -> str:
    """Return a slice of *value* from *start* to *end* (Python slice semantics)."""
    return value[start:end]


@_extractor
def extract_split_index(value: str, sep: str = ",", index: int = 0) -> str:
    """Split *value* on *sep* and return the part at *index*.

    Returns empty string when the index is out of range.
    """
    parts = value.split(sep)
    if index < 0 or index >= len(parts):
        return ""
    return parts[index].strip()


def apply_extract(rows: Iterable[dict], transform) -> Iterator[dict]:
    """Apply an extraction transform to every row in *rows*."""
    for row in rows:
        yield transform(row)
