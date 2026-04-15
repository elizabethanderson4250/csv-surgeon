"""Column truncation and padding utilities for csv-surgeon."""

from typing import Iterator, Callable


def _truncator(col: str, func: Callable[[str], str]) -> Callable[[dict], dict]:
    def _transform(row: dict) -> dict:
        if col not in row:
            return row
        result = dict(row)
        result[col] = func(row[col])
        return result
    return _transform


def truncate_left(col: str, max_len: int, ellipsis: bool = False) -> Callable[[dict], dict]:
    """Truncate a column value from the left to at most max_len characters."""
    if max_len < 0:
        raise ValueError("max_len must be >= 0")

    def _func(value: str) -> str:
        if len(value) <= max_len:
            return value
        if ellipsis and max_len >= 3:
            return "..." + value[-(max_len - 3):]
        return value[-max_len:] if max_len > 0 else ""

    return _truncator(col, _func)


def truncate_right(col: str, max_len: int, ellipsis: bool = False) -> Callable[[dict], dict]:
    """Truncate a column value from the right to at most max_len characters."""
    if max_len < 0:
        raise ValueError("max_len must be >= 0")

    def _func(value: str) -> str:
        if len(value) <= max_len:
            return value
        if ellipsis and max_len >= 3:
            return value[:max_len - 3] + "..."
        return value[:max_len]

    return _truncator(col, _func)


def pad_right(col: str, width: int, char: str = " ") -> Callable[[dict], dict]:
    """Pad a column value on the right to at least width characters."""
    if len(char) != 1:
        raise ValueError("char must be a single character")

    def _func(value: str) -> str:
        return value.ljust(width, char)

    return _truncator(col, _func)


def pad_left(col: str, width: int, char: str = " ") -> Callable[[dict], dict]:
    """Pad a column value on the left to at least width characters."""
    if len(char) != 1:
        raise ValueError("char must be a single character")

    def _func(value: str) -> str:
        return value.rjust(width, char)

    return _truncator(col, _func)


def apply(
    rows: Iterator[dict],
    transforms: list,
) -> Iterator[dict]:
    """Apply a list of truncation/padding transforms to each row."""
    for row in rows:
        for t in transforms:
            row = t(row)
        yield row
