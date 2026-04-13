"""Column statistics for CSV files without loading fully into memory."""

from collections import Counter
from typing import Iterator, Dict, Any, Optional
import math


def column_stats(rows: Iterator[Dict[str, Any]], column: str) -> Dict[str, Any]:
    """Compute descriptive statistics for a numeric column."""
    count = 0
    total = 0.0
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    sum_sq = 0.0
    errors = 0

    for row in rows:
        raw = row.get(column, "").strip()
        try:
            val = float(raw)
        except (ValueError, AttributeError):
            errors += 1
            continue
        count += 1
        total += val
        sum_sq += val * val
        if min_val is None or val < min_val:
            min_val = val
        if max_val is None or val > max_val:
            max_val = val

    mean = total / count if count else None
    variance = (sum_sq / count - mean ** 2) if count and mean is not None else None
    std_dev = math.sqrt(variance) if variance is not None and variance >= 0 else None

    return {
        "column": column,
        "count": count,
        "sum": total if count else None,
        "mean": mean,
        "min": min_val,
        "max": max_val,
        "std_dev": std_dev,
        "parse_errors": errors,
    }


def value_counts(rows: Iterator[Dict[str, Any]], column: str) -> Dict[str, int]:
    """Count occurrences of each unique value in a column."""
    counter: Counter = Counter()
    for row in rows:
        val = row.get(column, "").strip()
        counter[val] += 1
    return dict(counter.most_common())


def null_counts(rows: Iterator[Dict[str, Any]], columns: list) -> Dict[str, int]:
    """Count empty/missing values per column."""
    counts = {col: 0 for col in columns}
    for row in rows:
        for col in columns:
            if row.get(col, "").strip() == "":
                counts[col] += 1
    return counts
