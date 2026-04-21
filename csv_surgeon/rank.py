"""Column ranking utilities: dense rank, percent rank, and row number by group."""
from __future__ import annotations

from typing import Callable, Iterable, Iterator


def _safe_numeric(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return float("nan")


def rank_rows(
    rows: Iterable[dict],
    sort_column: str,
    output_column: str = "rank",
    method: str = "dense",
    ascending: bool = True,
    group_by: str | None = None,
    numeric: bool = False,
) -> list[dict]:
    """Assign a rank to each row based on *sort_column*.

    method: 'dense' | 'standard' | 'percent'
    group_by: if set, ranks are reset per group value.
    """
    if method not in ("dense", "standard", "percent"):
        raise ValueError(f"Unknown rank method: {method!r}")

    all_rows = list(rows)
    if not all_rows:
        return []

    key_fn: Callable[[dict], float | str]
    if numeric:
        key_fn = lambda r: _safe_numeric(r.get(sort_column, ""))
    else:
        key_fn = lambda r: r.get(sort_column, "")

    groups: dict[str, list[tuple[int, dict]]] = {}
    for idx, row in enumerate(all_rows):
        g = row.get(group_by, "__all__") if group_by else "__all__"
        groups.setdefault(g, []).append((idx, row))

    result: list[tuple[int, dict]] = []
    for group_rows in groups.values():
        sorted_group = sorted(group_rows, key=lambda t: key_fn(t[1]), reverse=not ascending)
        n = len(sorted_group)
        prev_val = object()
        dense_rank = 0
        standard_rank = 0
        for pos, (orig_idx, row) in enumerate(sorted_group):
            cur_val = key_fn(row)
            standard_rank = pos + 1
            if cur_val != prev_val:
                dense_rank += 1
            prev_val = cur_val
            if method == "dense":
                assigned = dense_rank
            elif method == "standard":
                assigned = standard_rank
            else:  # percent
                assigned = round((standard_rank - 1) / (n - 1), 6) if n > 1 else 0.0
            new_row = dict(row)
            new_row[output_column] = str(assigned)
            result.append((orig_idx, new_row))

    result.sort(key=lambda t: t[0])
    return [r for _, r in result]


def row_number(
    rows: Iterable[dict],
    output_column: str = "row_number",
    start: int = 1,
    group_by: str | None = None,
) -> Iterator[dict]:
    """Assign a sequential row number, optionally resetting per group."""
    counters: dict[str, int] = {}
    for row in rows:
        g = row.get(group_by, "__all__") if group_by else "__all__"
        counters[g] = counters.get(g, start - 1) + 1
        yield {**row, output_column: str(counters[g])}
