"""Row aggregation utilities for grouping and summarising CSV data."""

from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Optional


def _safe_numeric(value: str) -> Optional[float]:
    """Return float(value) or None if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def group_by(
    rows: Iterable[Dict[str, str]],
    key_columns: List[str],
) -> Dict[tuple, List[Dict[str, str]]]:
    """Partition *rows* into groups keyed by the values of *key_columns*."""
    groups: Dict[tuple, List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = tuple(row.get(col, "") for col in key_columns)
        groups[key].append(row)
    return dict(groups)


def aggregate(
    rows: Iterable[Dict[str, str]],
    group_by_columns: List[str],
    agg_column: str,
    func: str = "sum",
    output_column: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Group *rows* by *group_by_columns* and aggregate *agg_column*.

    Supported *func* values: ``sum``, ``count``, ``mean``, ``min``, ``max``.
    The result column is named *output_column* (defaults to
    ``<agg_column>_<func>``).
    """
    if func not in {"sum", "count", "mean", "min", "max"}:
        raise ValueError(f"Unsupported aggregation function: {func!r}")

    out_col = output_column or f"{agg_column}_{func}"
    groups = group_by(rows, group_by_columns)
    result: List[Dict[str, str]] = []

    for key, group_rows in groups.items():
        key_dict = dict(zip(group_by_columns, key))

        if func == "count":
            value = len(group_rows)
        else:
            numerics = [
                n for n in (_safe_numeric(r.get(agg_column, "")) for r in group_rows)
                if n is not None
            ]
            if not numerics:
                value = ""
            elif func == "sum":
                value = sum(numerics)
            elif func == "mean":
                value = sum(numerics) / len(numerics)
            elif func == "min":
                value = min(numerics)
            elif func == "max":
                value = max(numerics)

        key_dict[out_col] = "" if value == "" else str(value)
        result.append(key_dict)

    return result
