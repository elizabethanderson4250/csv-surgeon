"""Diff two CSV streams by a key column, identifying added, removed, and changed rows."""

from typing import Iterator, Dict, Any, Tuple, List


DiffResult = Dict[str, Any]


def _build_snapshot(rows: Iterator[Dict[str, Any]], key: str) -> Dict[str, Dict[str, Any]]:
    """Index rows from an iterable by the given key column."""
    snapshot: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        k = row[key]
        snapshot[k] = row
    return snapshot


def diff_rows(
    left_rows: Iterator[Dict[str, Any]],
    right_rows: Iterator[Dict[str, Any]],
    key: str,
    columns: List[str] | None = None,
) -> Tuple[List[DiffResult], List[DiffResult], List[DiffResult]]:
    """
    Compare two sets of CSV rows by a key column.

    Returns:
        added   – rows present in right but not in left
        removed – rows present in left but not in right
        changed – rows present in both but with differing values

    Each changed entry is a dict with keys:
        'key', 'before' (dict of changed fields), 'after' (dict of changed fields)
    """
    left_snap = _build_snapshot(left_rows, key)
    right_snap = _build_snapshot(right_rows, key)

    left_keys = set(left_snap)
    right_keys = set(right_snap)

    added = [right_snap[k] for k in sorted(right_keys - left_keys)]
    removed = [left_snap[k] for k in sorted(left_keys - right_keys)]

    changed: List[DiffResult] = []
    for k in sorted(left_keys & right_keys):
        l_row = left_snap[k]
        r_row = right_snap[k]
        compare_cols = columns if columns else list(l_row.keys())
        before: Dict[str, Any] = {}
        after: Dict[str, Any] = {}
        for col in compare_cols:
            if col == key:
                continue
            l_val = l_row.get(col)
            r_val = r_row.get(col)
            if l_val != r_val:
                before[col] = l_val
                after[col] = r_val
        if before:
            changed.append({"key": k, "before": before, "after": after})

    return added, removed, changed
