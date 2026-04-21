"""Interpolation helpers: fill missing numeric values between known points."""
from __future__ import annotations

from typing import Iterable, Iterator, List, Optional


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def linear_interpolate(
    rows: Iterable[dict],
    column: str,
    output_column: Optional[str] = None,
    fill_leading: bool = False,
    fill_trailing: bool = False,
) -> Iterator[dict]:
    """Linearly interpolate missing (empty) values in *column*.

    Gaps between two known numeric values are filled using linear interpolation.
    Leading / trailing gaps are left empty unless *fill_leading* / *fill_trailing*
    are set, in which case they are forward- or backward-filled from the nearest
    known value.
    """
    out_col = output_column or column
    buffer: List[dict] = list(rows)

    values: List[Optional[float]] = [_to_float(r.get(column, "")) for r in buffer]

    n = len(values)
    for i in range(n):
        if values[i] is not None:
            continue
        # find previous known index
        left = next((j for j in range(i - 1, -1, -1) if values[j] is not None), None)
        # find next known index
        right = next((j for j in range(i + 1, n) if values[j] is not None), None)

        if left is not None and right is not None:
            span = right - left
            values[i] = values[left] + (values[right] - values[left]) * (i - left) / span  # type: ignore[operator]
        elif left is None and right is not None and fill_leading:
            values[i] = values[right]
        elif right is None and left is not None and fill_trailing:
            values[i] = values[left]

    for row, val in zip(buffer, values):
        new_row = dict(row)
        new_row[out_col] = "" if val is None else str(val)
        yield new_row


def forward_fill(
    rows: Iterable[dict],
    column: str,
    output_column: Optional[str] = None,
) -> Iterator[dict]:
    """Carry the last known value forward into empty cells."""
    out_col = output_column or column
    last: Optional[str] = None
    for row in rows:
        new_row = dict(row)
        val = row.get(column, "")
        if val.strip() == "":
            new_row[out_col] = last if last is not None else ""
        else:
            last = val
            new_row[out_col] = val
        yield new_row


def backward_fill(
    rows: Iterable[dict],
    column: str,
    output_column: Optional[str] = None,
) -> Iterator[dict]:
    """Fill empty cells with the next known value."""
    out_col = output_column or column
    buffer = list(rows)
    values = [r.get(column, "") for r in buffer]
    n = len(values)
    for i in range(n - 2, -1, -1):
        if values[i].strip() == "" and i + 1 < n and values[i + 1].strip() != "":
            values[i] = values[i + 1]
    for row, val in zip(buffer, values):
        new_row = dict(row)
        new_row[out_col] = val
        yield new_row
