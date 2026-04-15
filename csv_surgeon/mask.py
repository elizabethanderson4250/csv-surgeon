"""Column masking and redaction utilities for sensitive data."""

import re
from typing import Callable, Dict, Iterable, Iterator


def _masker(func: Callable[[str], str]):
    """Wrap a masking function to operate on a named column in a row dict."""
    def _transform(col: str, **kwargs):
        def apply(row: dict) -> dict:
            if col not in row:
                return row
            new_row = dict(row)
            new_row[col] = func(row[col], **kwargs)
            return new_row
        return apply
    return _transform


@_masker
def redact(value: str, replacement: str = "***") -> str:
    """Replace the entire value with a fixed replacement string."""
    if not value or not value.strip():
        return value
    return replacement


@_masker
def mask_chars(value: str, char: str = "*", keep_last: int = 0) -> str:
    """Mask all characters, optionally revealing the last N characters."""
    if not value:
        return value
    if keep_last <= 0:
        return char * len(value)
    visible = value[-keep_last:]
    return char * (len(value) - keep_last) + visible


@_masker
def mask_regex(value: str, pattern: str, replacement: str = "***") -> str:
    """Replace regex matches within a value with a replacement string."""
    return re.sub(pattern, replacement, value)


@_masker
def truncate_mask(value: str, visible_start: int = 2, visible_end: int = 2, char: str = "*") -> str:
    """Show only the first and last N characters, masking the middle."""
    n = len(value)
    if n <= visible_start + visible_end:
        return value
    middle_len = n - visible_start - visible_end
    return value[:visible_start] + char * middle_len + value[n - visible_end:]


def apply_masks(
    rows: Iterable[dict],
    masks: list
) -> Iterator[dict]:
    """Apply a list of mask transform functions to each row."""
    for row in rows:
        for mask_fn in masks:
            row = mask_fn(row)
        yield row
