"""Column fingerprinting: cardinality, uniqueness ratio, sample values."""
from __future__ import annotations
from typing import Iterable, Iterator
import hashlib


def fingerprint_columns(
    rows: Iterable[dict],
    sample_limit: int = 5,
) -> dict[str, dict]:
    """Return fingerprint stats per column.

    Each column entry contains:
      - count: total non-empty values
      - nulls: empty/whitespace-only count
      - cardinality: number of distinct values
      - uniqueness: cardinality / (count + nulls)
      - samples: up to *sample_limit* distinct example values
      - checksum: md5 of sorted distinct values (for change detection)
    """
    counts: dict[str, int] = {}
    nulls: dict[str, int] = {}
    distinct: dict[str, set] = {}

    for row in rows:
        for col, val in row.items():
            if col not in counts:
                counts[col] = 0
                nulls[col] = 0
                distinct[col] = set()
            if val is None or str(val).strip() == "":
                nulls[col] += 1
            else:
                counts[col] += 1
                distinct[col].add(str(val))

    result: dict[str, dict] = {}
    for col in counts:
        total = counts[col] + nulls[col]
        card = len(distinct[col])
        uniqueness = card / total if total > 0 else 0.0
        sorted_vals = sorted(distinct[col])
        checksum = hashlib.md5("|".join(sorted_vals).encode()).hexdigest()
        result[col] = {
            "count": counts[col],
            "nulls": nulls[col],
            "cardinality": card,
            "uniqueness": round(uniqueness, 4),
            "samples": sorted_vals[:sample_limit],
            "checksum": checksum,
        }
    return result


def fingerprint_rows(rows: Iterable[dict], key_columns: list[str]) -> Iterator[dict]:
    """Annotate each row with a per-row hash of *key_columns* values."""
    for row in rows:
        key = "|".join(str(row.get(c, "")) for c in key_columns)
        row_hash = hashlib.md5(key.encode()).hexdigest()
        yield {**row, "_row_hash": row_hash}
