"""Outlier detection for numeric columns using IQR and Z-score methods."""
from __future__ import annotations

from typing import Iterable, Iterator
import math


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _mean_stddev(values: list[float]) -> tuple[float, float]:
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    return mean, math.sqrt(variance)


def _quartiles(sorted_values: list[float]) -> tuple[float, float]:
    n = len(sorted_values)
    mid = n // 2
    lower = sorted_values[:mid]
    upper = sorted_values[mid:] if n % 2 == 0 else sorted_values[mid + 1 :]
    q1 = (lower[len(lower) // 2 - 1] + lower[len(lower) // 2]) / 2 if len(lower) % 2 == 0 else lower[len(lower) // 2]
    q3 = (upper[len(upper) // 2 - 1] + upper[len(upper) // 2]) / 2 if len(upper) % 2 == 0 else upper[len(upper) // 2]
    return q1, q3


def flag_outliers_zscore(
    rows: Iterable[dict],
    column: str,
    threshold: float = 3.0,
    output_column: str = "is_outlier",
    flag_true: str = "1",
    flag_false: str = "0",
) -> Iterator[dict]:
    """Flag outliers using the Z-score method. Buffers all rows."""
    buffered = list(rows)
    values = [v for r in buffered if (v := _safe_float(r.get(column, ""))) is not None]
    mean, stddev = _mean_stddev(values)
    for row in buffered:
        v = _safe_float(row.get(column, ""))
        if v is None or stddev == 0.0:
            yield {**row, output_column: flag_false}
        else:
            z = abs((v - mean) / stddev)
            yield {**row, output_column: flag_true if z > threshold else flag_false}


def flag_outliers_iqr(
    rows: Iterable[dict],
    column: str,
    multiplier: float = 1.5,
    output_column: str = "is_outlier",
    flag_true: str = "1",
    flag_false: str = "0",
) -> Iterator[dict]:
    """Flag outliers using the IQR method. Buffers all rows."""
    buffered = list(rows)
    values = sorted(v for r in buffered if (v := _safe_float(r.get(column, ""))) is not None)
    if len(values) < 4:
        for row in buffered:
            yield {**row, output_column: flag_false}
        return
    q1, q3 = _quartiles(values)
    iqr = q3 - q1
    lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
    for row in buffered:
        v = _safe_float(row.get(column, ""))
        if v is None:
            yield {**row, output_column: flag_false}
        else:
            yield {**row, output_column: flag_true if v < lower or v > upper else flag_false}


def remove_outliers_iqr(
    rows: Iterable[dict],
    column: str,
    multiplier: float = 1.5,
) -> Iterator[dict]:
    """Yield only rows whose value in *column* is within IQR bounds."""
    for row in flag_outliers_iqr(rows, column, multiplier=multiplier, output_column="__outlier_tmp"):
        if row.pop("__outlier_tmp") == "0":
            yield row
