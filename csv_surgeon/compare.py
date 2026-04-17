"""Column-level comparison utilities for CSV rows."""
from typing import Iterator, Dict, Any, List, Optional


def compare_column(
    rows: Iterator[Dict[str, Any]],
    col_a: str,
    col_b: str,
    result_col: str = "_cmp",
) -> Iterator[Dict[str, Any]]:
    """Add a column with -1, 0, or 1 comparing col_a vs col_b numerically,
    falling back to lexicographic comparison."""
    for row in rows:
        a, b = row.get(col_a, ""), row.get(col_b, "")
        try:
            av, bv = float(a), float(b)
            result = (av > bv) - (av < bv)
        except (ValueError, TypeError):
            sa, sb = str(a), str(b)
            result = (sa > sb) - (sa < sb)
        yield {**row, result_col: str(result)}


def flag_changed(
    rows: Iterator[Dict[str, Any]],
    columns: List[str],
    flag_col: str = "_changed",
    true_val: str = "1",
    false_val: str = "0",
) -> Iterator[Dict[str, Any]]:
    """Flag rows where any of the given columns changed from the previous row."""
    prev: Optional[Dict[str, Any]] = None
    for row in rows:
        if prev is None:
            changed = False
        else:
            changed = any(row.get(c) != prev.get(c) for c in columns)
        yield {**row, flag_col: true_val if changed else false_val}
        prev = row


def diff_columns(
    rows: Iterator[Dict[str, Any]],
    col_a: str,
    col_b: str,
    result_col: str = "_diff",
    default: str = "",
) -> Iterator[Dict[str, Any]]:
    """Subtract col_b from col_a numerically; write result or default on error."""
    for row in rows:
        a, b = row.get(col_a, ""), row.get(col_b, "")
        try:
            result = str(float(a) - float(b))
        except (ValueError, TypeError):
            result = default
        yield {**row, result_col: result}
