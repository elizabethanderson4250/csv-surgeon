"""Sampling utilities for large CSV streams."""

import random
from typing import Iterator, List, Optional


def sample_rows(
    rows: Iterator[dict],
    n: int,
    seed: Optional[int] = None,
) -> List[dict]:
    """Reservoir sampling — returns exactly n rows (or fewer if stream is smaller).

    Uses Algorithm R so the full dataset never needs to be held in memory.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    rng = random.Random(seed)
    reservoir: List[dict] = []

    for i, row in enumerate(rows):
        if i < n:
            reservoir.append(row)
        else:
            j = rng.randint(0, i)
            if j < n:
                reservoir[j] = row

    return reservoir


def sample_fraction(
    rows: Iterator[dict],
    fraction: float,
    seed: Optional[int] = None,
) -> List[dict]:
    """Return each row with probability *fraction* (Bernoulli sampling).

    Args:
        rows: iterable of row dicts.
        fraction: probability in (0, 1] that any given row is kept.
        seed: optional RNG seed for reproducibility.
    """
    if not (0 < fraction <= 1.0):
        raise ValueError("fraction must be in the range (0, 1]")

    rng = random.Random(seed)
    return [row for row in rows if rng.random() < fraction]


def head(rows: Iterator[dict], n: int = 10) -> List[dict]:
    """Return the first *n* rows from the stream."""
    if n <= 0:
        raise ValueError("n must be a positive integer")
    result: List[dict] = []
    for row in rows:
        if len(result) >= n:
            break
        result.append(row)
    return result
