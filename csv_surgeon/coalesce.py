"""Coalesce: return first non-empty value across multiple columns."""
from typing import Iterable, Dict, List, Optional


def _is_empty(value: str) -> bool:
    return value is None or str(value).strip() == ""


def coalesce(rows: Iterable[Dict], source_columns: List[str], target_column: str,
             default: str = "") -> Iterable[Dict]:
    """For each row, set target_column to the first non-empty value
    among source_columns, or default if all are empty."""
    for row in rows:
        result = row.copy()
        chosen = default
        for col in source_columns:
            val = row.get(col, "")
            if not _is_empty(val):
                chosen = val
                break
        result[target_column] = chosen
        yield result


def coalesce_fill(rows: Iterable[Dict], target_column: str,
                  source_columns: List[str], default: str = "") -> Iterable[Dict]:
    """Alias with argument order friendlier for CLI use."""
    yield from coalesce(rows, source_columns, target_column, default)


def first_valid(row: Dict, columns: List[str], default: str = "") -> str:
    """Return the first non-empty value from the given columns in a single row."""
    for col in columns:
        val = row.get(col, "")
        if not _is_empty(val):
            return val
    return default
