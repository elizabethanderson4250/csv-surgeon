"""Column value classification — assign a category label based on membership lists or regex patterns."""
from __future__ import annotations
import re
from typing import Dict, Iterable, Iterator, List, Optional


def classify_by_map(
    rows: Iterable[Dict[str, str]],
    column: str,
    mapping: Dict[str, str],
    output_column: str = "category",
    default: str = "",
    case_sensitive: bool = True,
) -> Iterator[Dict[str, str]]:
    """Assign a label by exact-value lookup in *mapping* {value: label}."""
    if not case_sensitive:
        mapping = {k.lower(): v for k, v in mapping.items()}
    for row in rows:
        raw = row.get(column, "")
        key = raw if case_sensitive else raw.lower()
        out = {**row, output_column: mapping.get(key, default)}
        yield out


def classify_by_patterns(
    rows: Iterable[Dict[str, str]],
    column: str,
    patterns: List[tuple],  # list of (regex_str, label)
    output_column: str = "category",
    default: str = "",
    flags: int = 0,
) -> Iterator[Dict[str, str]]:
    """Assign the label of the first matching regex pattern.

    *patterns* is an ordered list of ``(pattern, label)`` tuples.
    """
    compiled = [(re.compile(p, flags), label) for p, label in patterns]
    for row in rows:
        value = row.get(column, "")
        matched = default
        for regex, label in compiled:
            if regex.search(value):
                matched = label
                break
        yield {**row, output_column: matched}


def classify_by_ranges(
    rows: Iterable[Dict[str, str]],
    column: str,
    ranges: List[tuple],  # list of (low, high, label) inclusive
    output_column: str = "category",
    default: str = "",
) -> Iterator[Dict[str, str]]:
    """Assign a label based on numeric range membership.

    *ranges* is an ordered list of ``(low, high, label)`` tuples (inclusive).
    """
    for row in rows:
        raw = row.get(column, "")
        matched = default
        try:
            val = float(raw)
            for low, high, label in ranges:
                if low <= val <= high:
                    matched = label
                    break
        except (ValueError, TypeError):
            pass
        yield {**row, output_column: matched}
