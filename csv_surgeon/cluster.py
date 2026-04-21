"""Cluster rows by column similarity using simple bucketing strategies."""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Iterable, Iterator


def _fingerprint_soundex(value: str) -> str:
    """Very lightweight Soundex-inspired fingerprint for clustering."""
    value = value.upper().strip()
    if not value:
        return ""
    codes = {
        "BFPV": "1", "CGJKQSXYZ": "2", "DT": "3",
        "L": "4", "MN": "5", "R": "6",
    }
    result = [value[0]]
    for ch in value[1:]:
        for letters, code in codes.items():
            if ch in letters:
                if code != result[-1]:
                    result.append(code)
                break
        else:
            pass  # vowels / H / W ignored
    return "".join(result)[:4].ljust(4, "0")


def cluster_by_value(
    rows: Iterable[dict],
    column: str,
    output_column: str = "cluster_key",
    key_func: Callable[[str], str] | None = None,
) -> Iterator[dict]:
    """Annotate each row with a cluster key derived from *column*.

    Parameters
    ----------
    rows:
        Iterable of row dicts.
    column:
        The column whose value is used to generate the cluster key.
    output_column:
        Name of the new column that receives the cluster key.
    key_func:
        Optional callable ``(value: str) -> str``.  Defaults to lowercased,
        whitespace-stripped value (exact-match bucketing).
    """
    if key_func is None:
        key_func = lambda v: v.strip().lower()  # noqa: E731

    for row in rows:
        new_row = dict(row)
        raw = row.get(column, "")
        new_row[output_column] = key_func(str(raw) if raw is not None else "")
        yield new_row


def cluster_by_soundex(
    rows: Iterable[dict],
    column: str,
    output_column: str = "cluster_key",
) -> Iterator[dict]:
    """Annotate each row with a Soundex cluster key."""
    return cluster_by_value(rows, column, output_column, key_func=_fingerprint_soundex)


def collect_clusters(
    rows: Iterable[dict],
    cluster_column: str,
) -> dict[str, list[dict]]:
    """Group rows into a dict keyed by their cluster value.

    Useful for inspection / reporting; loads all rows into memory.
    """
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        key = row.get(cluster_column, "")
        buckets[key].append(row)
    return dict(buckets)
