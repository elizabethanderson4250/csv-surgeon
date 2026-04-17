"""Binning / bucketing utilities for numeric columns."""
from __future__ import annotations

from typing import Iterable, Iterator, List, Optional, Tuple


def _find_bin(value: float, edges: List[float], labels: List[str], include_lowest: bool) -> str:
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        in_bin = (lo <= value < hi) if i < len(edges) - 2 else (lo <= value <= hi)
        if include_lowest and i == 0:
            in_bin = lo <= value < hi if i < len(edges) - 2 else lo <= value <= hi
        if in_bin:
            return labels[i]
    return ""


def bin_fixed(
    rows: Iterable[dict],
    column: str,
    edges: List[float],
    labels: Optional[List[str]] = None,
    output_column: Optional[str] = None,
    default: str = "",
) -> Iterator[dict]:
    """Assign each row to a fixed-width bin defined by *edges*.

    *edges* must have len >= 2.  *labels* must have len == len(edges) - 1.
    If *labels* is omitted, labels like '0-10' are auto-generated.
    """
    if len(edges) < 2:
        raise ValueError("edges must contain at least two values")
    n_bins = len(edges) - 1
    if labels is None:
        labels = [f"{edges[i]}-{edges[i+1]}" for i in range(n_bins)]
    if len(labels) != n_bins:
        raise ValueError(f"labels length {len(labels)} must equal len(edges)-1 = {n_bins}")
    out_col = output_column or f"{column}_bin"
    for row in rows:
        new_row = dict(row)
        raw = row.get(column, "")
        try:
            val = float(raw)
            new_row[out_col] = _find_bin(val, edges, labels, include_lowest=True) or default
        except (ValueError, TypeError):
            new_row[out_col] = default
        yield new_row


def bin_quantile(
    rows: Iterable[dict],
    column: str,
    n_quantiles: int = 4,
    output_column: Optional[str] = None,
    default: str = "",
) -> Iterator[dict]:
    """Assign rows to quantile-based bins (requires materialising the data)."""
    if n_quantiles < 2:
        raise ValueError("n_quantiles must be >= 2")
    all_rows = list(rows)
    values = []
    for r in all_rows:
        try:
            values.append(float(r.get(column, "")))
        except (ValueError, TypeError):
            values.append(None)
    valid = sorted(v for v in values if v is not None)
    if not valid:
        yield from ({**r, (output_column or f"{column}_bin"): default} for r in all_rows)
        return
    edges = [valid[int(len(valid) * i / n_quantiles)] for i in range(n_quantiles)]
    edges.append(valid[-1])
    labels = [f"Q{i+1}" for i in range(n_quantiles)]
    out_col = output_column or f"{column}_bin"
    for row, val in zip(all_rows, values):
        new_row = dict(row)
        if val is None:
            new_row[out_col] = default
        else:
            new_row[out_col] = _find_bin(val, edges, labels, include_lowest=True) or default
        yield new_row
