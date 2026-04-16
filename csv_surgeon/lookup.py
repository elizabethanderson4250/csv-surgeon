"""Column value lookup/enrichment from a reference CSV."""
from __future__ import annotations
from typing import Iterable, Iterator
import csv
import io


def _build_lookup(ref_rows: Iterable[dict], key_col: str, value_col: str) -> dict:
    """Build a {key: value} mapping from reference rows."""
    lookup: dict = {}
    for row in ref_rows:
        k = row.get(key_col)
        if k is not None:
            lookup[k] = row.get(value_col, "")
    return lookup


def lookup_enrich(
    rows: Iterable[dict],
    ref_rows: Iterable[dict],
    src_col: str,
    ref_key_col: str,
    ref_value_col: str,
    dest_col: str | None = None,
    default: str = "",
) -> Iterator[dict]:
    """Enrich each row by looking up src_col in ref_rows.

    Args:
        rows: primary rows to enrich.
        ref_rows: reference rows used to build the lookup table.
        src_col: column in primary rows whose value is used as the lookup key.
        ref_key_col: column in reference rows that acts as the key.
        ref_value_col: column in reference rows whose value is fetched.
        dest_col: destination column name; defaults to ref_value_col.
        default: value to use when no match is found.
    """
    mapping = _build_lookup(ref_rows, ref_key_col, ref_value_col)
    out_col = dest_col or ref_value_col
    for row in rows:
        new_row = dict(row)
        key = row.get(src_col, "")
        new_row[out_col] = mapping.get(key, default)
        yield new_row


def lookup_filter(
    rows: Iterable[dict],
    ref_rows: Iterable[dict],
    src_col: str,
    ref_key_col: str,
    exclude: bool = False,
) -> Iterator[dict]:
    """Keep (or exclude) rows whose src_col value exists in ref_rows key set."""
    key_set = {row.get(ref_key_col) for row in ref_rows if row.get(ref_key_col) is not None}
    for row in rows:
        present = row.get(src_col) in key_set
        if (present and not exclude) or (not present and exclude):
            yield row
