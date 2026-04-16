"""Column annotation: add row numbers, timestamps, or hash fingerprints."""
from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from typing import Iterable, Iterator


def add_row_number(rows: Iterable[dict], column: str = "_row_num", start: int = 1) -> Iterator[dict]:
    """Yield rows with a sequential row number added."""
    for i, row in enumerate(rows, start=start):
        yield {**row, column: str(i)}


def add_timestamp(rows: Iterable[dict], column: str = "_timestamp", fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> Iterator[dict]:
    """Yield rows with a UTC timestamp added (same value for all rows)."""
    ts = datetime.now(tz=timezone.utc).strftime(fmt)
    for row in rows:
        yield {**row, column: ts}


def add_hash(rows: Iterable[dict], column: str = "_hash", fields: list[str] | None = None, algorithm: str = "md5") -> Iterator[dict]:
    """Yield rows with a hash fingerprint of selected (or all) fields."""
    hasher_factory = getattr(hashlib, algorithm, None)
    if hasher_factory is None:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    for row in rows:
        keys = fields if fields is not None else sorted(row.keys())
        payload = "|".join(f"{k}={row.get(k, '')}" for k in keys)
        digest = hasher_factory(payload.encode()).hexdigest()
        yield {**row, column: digest}


def add_constant(rows: Iterable[dict], column: str, value: str) -> Iterator[dict]:
    """Yield rows with a constant value added to every row."""
    for row in rows:
        yield {**row, column: value}
