"""Streaming CSV join utilities for csv-surgeon."""

from typing import Dict, Iterable, Iterator, List, Optional


def _build_lookup(
    rows: Iterable[Dict[str, str]],
    key_column: str,
    keep_last: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Build an in-memory lookup dict from the *smaller* (right) dataset."""
    lookup: Dict[str, Dict[str, str]] = {}
    for row in rows:
        key = row.get(key_column, "")
        if key not in lookup or keep_last:
            lookup[key] = row
    return lookup


def inner_join(
    left_rows: Iterable[Dict[str, str]],
    right_rows: Iterable[Dict[str, str]],
    left_on: str,
    right_on: str,
    right_prefix: str = "right_",
) -> Iterator[Dict[str, str]]:
    """Yield rows that have a matching key in both left and right datasets."""
    lookup = _build_lookup(right_rows, right_on)
    for row in left_rows:
        key = row.get(left_on, "")
        if key in lookup:
            merged = dict(row)
            for k, v in lookup[key].items():
                if k == right_on:
                    continue
                merged_key = f"{right_prefix}{k}" if k in row else k
                merged[merged_key] = v
            yield merged


def left_join(
    left_rows: Iterable[Dict[str, str]],
    right_rows: Iterable[Dict[str, str]],
    left_on: str,
    right_on: str,
    right_prefix: str = "right_",
    fill_value: str = "",
) -> Iterator[Dict[str, str]]:
    """Yield all left rows, enriched with right data where available."""
    lookup = _build_lookup(right_rows, right_on)
    # Collect right-side column names (excluding join key)
    right_cols: List[str] = []
    if lookup:
        sample = next(iter(lookup.values()))
        right_cols = [k for k in sample if k != right_on]

    for row in left_rows:
        key = row.get(left_on, "")
        merged = dict(row)
        right_row = lookup.get(key, {})
        for k in right_cols:
            merged_key = f"{right_prefix}{k}" if k in row else k
            merged[merged_key] = right_row.get(k, fill_value)
        yield merged
