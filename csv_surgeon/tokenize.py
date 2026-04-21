"""tokenize.py — Split column values into tokens and compute token-level statistics."""
from __future__ import annotations

import re
from typing import Iterable, Iterator, List, Optional


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _split(value: str, sep: Optional[str], pattern: Optional[str]) -> List[str]:
    """Return non-empty tokens from *value* using separator or regex pattern."""
    if pattern:
        parts = re.split(pattern, value)
    elif sep is not None:
        parts = value.split(sep)
    else:
        parts = value.split()  # whitespace split
    return [t.strip() for t in parts if t.strip()]


# ---------------------------------------------------------------------------
# Row-level transforms
# ---------------------------------------------------------------------------

def tokenize_column(
    rows: Iterable[dict],
    column: str,
    output_column: Optional[str] = None,
    sep: Optional[str] = None,
    pattern: Optional[str] = None,
) -> Iterator[dict]:
    """Add a new column containing the list of tokens from *column*.

    The tokens are stored as a pipe-separated string so the output remains
    a flat CSV-friendly value.
    """
    dest = output_column or f"{column}_tokens"
    for row in rows:
        value = row.get(column, "")
        tokens = _split(value, sep, pattern)
        yield {**row, dest: "|".join(tokens)}


def token_count(
    rows: Iterable[dict],
    column: str,
    output_column: Optional[str] = None,
    sep: Optional[str] = None,
    pattern: Optional[str] = None,
) -> Iterator[dict]:
    """Add a column with the number of tokens found in *column*."""
    dest = output_column or f"{column}_token_count"
    for row in rows:
        value = row.get(column, "")
        tokens = _split(value, sep, pattern)
        yield {**row, dest: str(len(tokens))}


def token_contains(
    rows: Iterable[dict],
    column: str,
    token: str,
    output_column: Optional[str] = None,
    case_sensitive: bool = True,
    sep: Optional[str] = None,
    pattern: Optional[str] = None,
) -> Iterator[dict]:
    """Add a boolean column indicating whether any token matches *token*."""
    dest = output_column or f"{column}_has_{token}"
    needle = token if case_sensitive else token.lower()
    for row in rows:
        value = row.get(column, "")
        tokens = _split(value, sep, pattern)
        if not case_sensitive:
            tokens = [t.lower() for t in tokens]
        yield {**row, dest: str(needle in tokens)}
