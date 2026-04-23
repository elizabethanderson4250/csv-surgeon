"""Compute pairwise Pearson correlation between numeric columns."""
from __future__ import annotations

import math
from typing import Iterable, Iterator


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    """Return Pearson r for two equal-length lists, or None if undefined."""
    n = len(xs)
    if n < 2:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    std_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if std_x == 0 or std_y == 0:
        return None
    return cov / (std_x * std_y)


def correlate_columns(
    rows: Iterable[dict[str, str]],
    col_a: str,
    col_b: str,
) -> float | None:
    """Compute Pearson correlation between two named columns.

    Rows where either value is non-numeric are skipped.
    Returns None when fewer than 2 valid pairs exist.
    """
    xs: list[float] = []
    ys: list[float] = []
    for row in rows:
        a = _safe_float(row.get(col_a, ""))
        b = _safe_float(row.get(col_b, ""))
        if a is not None and b is not None:
            xs.append(a)
            ys.append(b)
    return _pearson(xs, ys)


def correlation_matrix(
    rows: Iterable[dict[str, str]],
    columns: list[str],
) -> dict[tuple[str, str], float | None]:
    """Compute all pairwise Pearson correlations for the given columns.

    Materialises rows once, then iterates over pairs.
    Returns a dict keyed by (col_a, col_b) tuples.
    """
    data = list(rows)
    result: dict[tuple[str, str], float | None] = {}
    for i, col_a in enumerate(columns):
        for col_b in columns[i:]:
            r = correlate_columns(iter(data), col_a, col_b)
            result[(col_a, col_b)] = r
            if col_a != col_b:
                result[(col_b, col_a)] = r
    return result
