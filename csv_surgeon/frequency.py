"""Frequency analysis: compute value frequencies and percentages for a column."""
from __future__ import annotations

from collections import Counter
from typing import Iterable


def value_frequency(
    rows: Iterable[dict],
    column: str,
    normalize: bool = False,
    top_n: int | None = None,
    sort_by: str = "count",  # "count" | "value"
) -> list[dict]:
    """Return frequency table rows for *column*.

    Each output row has keys: ``value``, ``count``, ``percent``.

    Args:
        rows:       Iterable of dicts (streaming-friendly).
        column:     Column name to analyse.
        normalize:  If True, also compute percentage share.
        top_n:      Keep only the top-N most frequent values (None = all).
        sort_by:    Primary sort key – ``'count'`` (desc) or ``'value'`` (asc).

    Returns:
        List of dicts with keys ``value``, ``count``, ``percent``.
    """
    counter: Counter = Counter()
    total = 0
    for row in rows:
        val = row.get(column, "")
        counter[val] += 1
        total += 1

    if sort_by == "value":
        items = sorted(counter.items(), key=lambda kv: kv[0])
    else:
        items = counter.most_common()  # descending by count

    if top_n is not None:
        # when sorted by value we still want top-N by count
        if sort_by == "value":
            items = sorted(items, key=lambda kv: kv[1], reverse=True)[:top_n]
            items = sorted(items, key=lambda kv: kv[0])
        else:
            items = items[:top_n]

    result = []
    for value, count in items:
        pct = round(count / total * 100, 4) if total > 0 else 0.0
        row_out: dict = {"value": value, "count": str(count)}
        if normalize:
            row_out["percent"] = str(pct)
        result.append(row_out)
    return result


def cumulative_frequency(
    freq_rows: list[dict],
) -> list[dict]:
    """Add a ``cumulative_count`` and ``cumulative_percent`` field to already-computed
    frequency rows (must include ``count`` and ``percent``).

    Mutates and returns *freq_rows* in place.
    """
    running_count = 0
    running_pct = 0.0
    for row in freq_rows:
        running_count += int(row["count"])
        row["cumulative_count"] = str(running_count)
        if "percent" in row:
            running_pct += float(row["percent"])
            row["cumulative_percent"] = str(round(running_pct, 4))
    return freq_rows
