"""Datetime parsing and formatting transforms for CSV columns."""

from datetime import datetime
from typing import Callable, Iterator


def _dt_transform(col: str, func: Callable[[str], str]) -> Callable[[dict], dict]:
    def _transform(row: dict) -> dict:
        if col not in row:
            return row
        result = dict(row)
        try:
            result[col] = func(row[col])
        except (ValueError, TypeError):
            pass
        return result
    return _transform


def parse_date(col: str, fmt: str = "%Y-%m-%d") -> Callable[[dict], dict]:
    """Normalize a date column to ISO format (YYYY-MM-DD)."""
    def _convert(val: str) -> str:
        return datetime.strptime(val.strip(), fmt).strftime("%Y-%m-%d")
    return _dt_transform(col, _convert)


def format_date(col: str, in_fmt: str = "%Y-%m-%d", out_fmt: str = "%d/%m/%Y") -> Callable[[dict], dict]:
    """Reformat a date column from one format to another."""
    def _convert(val: str) -> str:
        return datetime.strptime(val.strip(), in_fmt).strftime(out_fmt)
    return _dt_transform(col, _convert)


def extract_part(col: str, part: str, in_fmt: str = "%Y-%m-%d", out_col: str | None = None) -> Callable[[dict], dict]:
    """Extract a date part (year, month, day, weekday) into a new or existing column."""
    _parts = {
        "year": lambda dt: str(dt.year),
        "month": lambda dt: str(dt.month),
        "day": lambda dt: str(dt.day),
        "weekday": lambda dt: dt.strftime("%A"),
        "hour": lambda dt: str(dt.hour),
        "minute": lambda dt: str(dt.minute),
    }
    if part not in _parts:
        raise ValueError(f"Unknown date part: {part!r}. Choose from {list(_parts)}.")
    target = out_col or f"{col}_{part}"

    def _transform(row: dict) -> dict:
        if col not in row:
            return row
        result = dict(row)
        try:
            dt = datetime.strptime(row[col].strip(), in_fmt)
            result[target] = _parts[part](dt)
        except (ValueError, TypeError):
            result[target] = ""
        return result
    return _transform


def apply(rows: Iterator[dict], *transforms: Callable[[dict], dict]) -> Iterator[dict]:
    for row in rows:
        for t in transforms:
            row = t(row)
        yield row
