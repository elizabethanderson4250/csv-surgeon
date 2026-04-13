"""Pivot and unpivot (melt) operations for CSV rows."""
from typing import Iterable, Iterator, List, Optional


def pivot(
    rows: Iterable[dict],
    index_col: str,
    pivot_col: str,
    value_col: str,
    agg: str = "first",
) -> List[dict]:
    """Pivot rows so unique values in *pivot_col* become new column headers.

    Args:
        rows: Iterable of row dicts.
        index_col: Column whose values identify each output row.
        pivot_col: Column whose distinct values become new columns.
        value_col: Column whose values populate the new columns.
        agg: Aggregation strategy when multiple values exist for the same
             (index, pivot) pair: 'first', 'last', 'sum', 'count'.

    Returns:
        List of aggregated row dicts.
    """
    from collections import defaultdict

    # accumulate: {index_val: {pivot_val: [values]}}
    buckets: dict = defaultdict(lambda: defaultdict(list))
    pivot_values: list = []

    for row in rows:
        idx = row.get(index_col, "")
        piv = row.get(pivot_col, "")
        val = row.get(value_col, "")
        buckets[idx][piv].append(val)
        if piv not in pivot_values:
            pivot_values.append(piv)

    def _agg(vals: list) -> str:
        if not vals:
            return ""
        if agg == "last":
            return str(vals[-1])
        if agg == "sum":
            try:
                return str(sum(float(v) for v in vals))
            except ValueError:
                return str(vals[0])
        if agg == "count":
            return str(len(vals))
        return str(vals[0])  # first

    result = []
    for idx_val, piv_map in buckets.items():
        row_out = {index_col: idx_val}
        for pv in pivot_values:
            row_out[pv] = _agg(piv_map.get(pv, []))
        result.append(row_out)
    return result


def unpivot(
    rows: Iterable[dict],
    id_cols: List[str],
    value_col: str = "value",
    variable_col: str = "variable",
    columns: Optional[List[str]] = None,
) -> Iterator[dict]:
    """Melt wide rows into long format.

    Args:
        rows: Iterable of row dicts.
        id_cols: Columns to keep as identifiers.
        value_col: Name for the new values column.
        variable_col: Name for the new variable/column-name column.
        columns: Explicit list of columns to unpivot; defaults to all
                 non-id columns found in the first row.

    Yields:
        One dict per (row, melted column) pair.
    """
    _cols_resolved = False
    melt_cols: List[str] = columns or []

    for row in rows:
        if not _cols_resolved:
            if not melt_cols:
                melt_cols = [c for c in row.keys() if c not in id_cols]
            _cols_resolved = True
        base = {col: row.get(col, "") for col in id_cols}
        for col in melt_cols:
            out = dict(base)
            out[variable_col] = col
            out[value_col] = row.get(col, "")
            yield out
