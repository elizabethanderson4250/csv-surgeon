"""Cross-join and semi-join utilities for CSV rows."""
from typing import Iterable, Iterator, Set


def cross_join(
    left: Iterable[dict],
    right: Iterable[dict],
) -> Iterator[dict]:
    """Cartesian product of two row iterables."""
    right_rows = list(right)
    for left_row in left:
        for right_row in right_rows:
            merged = {**left_row}
            for k, v in right_row.items():
                if k in merged:
                    merged[f"right_{k}"] = v
                else:
                    merged[k] = v
            yield merged


def semi_join(
    left: Iterable[dict],
    right: Iterable[dict],
    left_key: str,
    right_key: str,
    negate: bool = False,
) -> Iterator[dict]:
    """Keep left rows whose key value exists (or not) in right.

    Args:
        left: left row iterable.
        right: right row iterable.
        left_key: column name in left to match on.
        right_key: column name in right to match on.
        negate: if True, perform an anti-join (keep rows NOT in right).
    """
    right_keys: Set[str] = {row[right_key] for row in right if right_key in row}
    for row in left:
        val = row.get(left_key)
        if negate:
            if val not in right_keys:
                yield row
        else:
            if val in right_keys:
                yield row
