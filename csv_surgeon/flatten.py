"""Utilities for flattening/exploding rows with multi-valued cells."""
from typing import Iterable, Iterator, List, Optional


def flatten_column(
    rows: Iterable[dict],
    column: str,
    separator: str = "|",
    strip: bool = True,
) -> Iterator[dict]:
    """Explode a delimited column so each value gets its own row.

    Args:
        rows:      Input rows as dicts.
        column:    Name of the column to flatten.
        separator: Delimiter used to split values (default ``|``).
        strip:     Strip whitespace from each split value when True.

    Yields:
        One dict per split value; all other fields are copied unchanged.
        Rows where the column is missing or empty are yielded as-is.
    """
    for row in rows:
        raw = row.get(column, "")
        if not raw:
            yield row
            continue
        parts = raw.split(separator)
        for part in parts:
            value = part.strip() if strip else part
            yield {**row, column: value}


def merge_columns(
    rows: Iterable[dict],
    columns: List[str],
    into: str,
    separator: str = " ",
    drop_originals: bool = True,
) -> Iterator[dict]:
    """Merge multiple columns into a single new column.

    Args:
        rows:           Input rows as dicts.
        columns:        Ordered list of column names to merge.
        into:           Name of the resulting merged column.
        separator:      String placed between values (default space).
        drop_originals: Remove the source columns from the output when True.

    Yields:
        Rows with the merged column added (and originals optionally removed).
    """
    for row in rows:
        parts = [str(row.get(col, "")) for col in columns]
        merged = separator.join(parts)
        new_row = dict(row)
        new_row[into] = merged
        if drop_originals:
            for col in columns:
                new_row.pop(col, None)
        yield new_row


def split_column(
    rows: Iterable[dict],
    column: str,
    into: List[str],
    separator: str = " ",
    strip: bool = True,
    drop_original: bool = True,
) -> Iterator[dict]:
    """Split a single column into multiple named columns.

    If there are fewer parts than target columns the extras are empty strings.
    Extra parts beyond the number of target columns are discarded.

    Args:
        rows:          Input rows as dicts.
        column:        Source column to split.
        into:          Ordered list of new column names.
        separator:     Delimiter (default space).
        strip:         Strip whitespace from each part when True.
        drop_original: Remove the source column when True.

    Yields:
        Rows with the split columns added.
    """
    for row in rows:
        raw = row.get(column, "")
        parts = raw.split(separator, maxsplit=len(into) - 1)
        if strip:
            parts = [p.strip() for p in parts]
        new_row = dict(row)
        for i, name in enumerate(into):
            new_row[name] = parts[i] if i < len(parts) else ""
        if drop_original:
            new_row.pop(column, None)
        yield new_row
