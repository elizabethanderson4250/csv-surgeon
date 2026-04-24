"""Rolling / cumulative statistics over a column of streaming rows."""
from __future__ import annotations

from typing import Iterable, Iterator


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def cumulative_sum(
    rows: Iterable[dict],
    column: str,
    output_column: str = "",
    default: str = "",
) -> Iterator[dict]:
    """Yield each row with a running cumulative sum appended."""
    out_col = output_column or f"{column}_cumsum"
    running = 0.0
    for row in rows:
        v = _safe_float(row.get(column, ""))
        if v is not None:
            running += v
            result = str(running)
        else:
            result = default
        yield {**row, out_col: result}


def cumulative_mean(
    rows: Iterable[dict],
    column: str,
    output_column: str = "",
    default: str = "",
) -> Iterator[dict]:
    """Yield each row with a running cumulative mean appended."""
    out_col = output_column or f"{column}_cummean"
    running = 0.0
    count = 0
    for row in rows:
        v = _safe_float(row.get(column, ""))
        if v is not None:
            running += v
            count += 1
            result = str(running / count)
        else:
            result = default
        yield {**row, out_col: result}


def cumulative_max(
    rows: Iterable[dict],
    column: str,
    output_column: str = "",
    default: str = "",
) -> Iterator[dict]:
    """Yield each row with a running cumulative maximum appended."""
    out_col = output_column or f"{column}_cummax"
    current_max: float | None = None
    for row in rows:
        v = _safe_float(row.get(column, ""))
        if v is not None:
            current_max = v if current_max is None else max(current_max, v)
            result = str(current_max)
        else:
            result = default
        yield {**row, out_col: result}


def cumulative_min(
    rows: Iterable[dict],
    column: str,
    output_column: str = "",
    default: str = "",
) -> Iterator[dict]:
    """Yield each row with a running cumulative minimum appended."""
    out_col = output_column or f"{column}_cummin"
    current_min: float | None = None
    for row in rows:
        v = _safe_float(row.get(column, ""))
        if v is not None:
            current_min = v if current_min is None else min(current_min, v)
            result = str(current_min)
        else:
            result = default
        yield {**row, out_col: result}
