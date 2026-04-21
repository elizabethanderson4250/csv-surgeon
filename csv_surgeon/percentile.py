"""Percentile and quantile calculations over streaming CSV rows."""

from __future__ import annotations

from typing import Iterable, Iterator


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _percentile(sorted_values: list[float], p: float) -> float:
    """Return the p-th percentile (0-100) using linear interpolation."""
    if not sorted_values:
        raise ValueError("Cannot compute percentile of empty list")
    if not 0 <= p <= 100:
        raise ValueError(f"Percentile must be between 0 and 100, got {p}")
    n = len(sorted_values)
    if n == 1:
        return sorted_values[0]
    index = (p / 100) * (n - 1)
    lo = int(index)
    hi = lo + 1
    if hi >= n:
        return sorted_values[-1]
    fraction = index - lo
    return sorted_values[lo] + fraction * (sorted_values[hi] - sorted_values[lo])


def compute_percentiles(
    rows: Iterable[dict],
    column: str,
    percentiles: list[float],
    output_column: str | None = None,
) -> dict[str, float]:
    """Collect numeric values from *column* and return requested percentile values.

    Returns a mapping of ``"p{n}" -> value`` for each requested percentile.
    """
    values: list[float] = []
    for row in rows:
        v = _safe_float(row.get(column, ""))
        if v is not None:
            values.append(v)
    values.sort()
    return {f"p{p}": _percentile(values, p) for p in percentiles}


def flag_percentile_band(
    rows: Iterable[dict],
    column: str,
    lower: float,
    upper: float,
    output_column: str = "percentile_band",
) -> Iterator[dict]:
    """Annotate each row with a label indicating which percentile band its value falls in.

    Values below *lower* percentile get label "low", above *upper* get "high",
    otherwise "mid".  Non-numeric values receive an empty string label.
    """
    collected: list[dict] = list(rows)
    values = [_safe_float(r.get(column, "")) for r in collected]
    numeric = sorted(v for v in values if v is not None)
    if not numeric:
        for row in collected:
            yield {**row, output_column: ""}
        return
    lo_val = _percentile(numeric, lower)
    hi_val = _percentile(numeric, upper)
    for row, v in zip(collected, values):
        if v is None:
            label = ""
        elif v < lo_val:
            label = "low"
        elif v > hi_val:
            label = "high"
        else:
            label = "mid"
        yield {**row, output_column: label}
