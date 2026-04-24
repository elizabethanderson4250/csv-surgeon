"""Z-score normalization and standardization for CSV columns."""
from __future__ import annotations

import math
from typing import Iterable, Iterator


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _mean_std(values: list[float]) -> tuple[float, float]:
    """Return (mean, population std-dev) for a list of floats."""
    if not values:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return mean, math.sqrt(variance)


def zscore_column(
    rows: Iterable[dict],
    column: str,
    output_column: str | None = None,
    default: str = "",
    precision: int = 6,
) -> Iterator[dict]:
    """Yield rows with a z-score column added.

    Args:
        rows: Iterable of row dicts.
        column: Column whose values are standardized.
        output_column: Name for the new column; defaults to ``<column>_zscore``.
        default: Value written when the source value is non-numeric.
        precision: Decimal places for the z-score string.
    """
    out_col = output_column or f"{column}_zscore"
    rows = list(rows)
    numeric_vals = [v for r in rows if (v := _safe_float(r.get(column, ""))) is not None]
    mean, std = _mean_std(numeric_vals)

    for row in rows:
        new_row = dict(row)
        raw = row.get(column, "")
        val = _safe_float(raw)
        if val is None or std == 0.0:
            new_row[out_col] = default if val is None else "0.0"
        else:
            new_row[out_col] = f"{(val - mean) / std:.{precision}f}"
        yield new_row


def minmax_scale_column(
    rows: Iterable[dict],
    column: str,
    output_column: str | None = None,
    default: str = "",
    precision: int = 6,
    feature_range: tuple[float, float] = (0.0, 1.0),
) -> Iterator[dict]:
    """Yield rows with a min-max scaled column added.

    Args:
        rows: Iterable of row dicts.
        column: Column to scale.
        output_column: Name for the new column; defaults to ``<column>_scaled``.
        default: Value written when the source value is non-numeric.
        precision: Decimal places for the scaled value string.
        feature_range: Target (min, max) range; defaults to (0, 1).
    """
    out_col = output_column or f"{column}_scaled"
    rows = list(rows)
    numeric_vals = [v for r in rows if (v := _safe_float(r.get(column, ""))) is not None]
    lo, hi = (min(numeric_vals), max(numeric_vals)) if numeric_vals else (0.0, 0.0)
    range_in = hi - lo
    range_out = feature_range[1] - feature_range[0]

    for row in rows:
        new_row = dict(row)
        val = _safe_float(row.get(column, ""))
        if val is None:
            new_row[out_col] = default
        elif range_in == 0.0:
            new_row[out_col] = f"{feature_range[0]:.{precision}f}"
        else:
            scaled = feature_range[0] + (val - lo) / range_in * range_out
            new_row[out_col] = f"{scaled:.{precision}f}"
        yield new_row
