"""Fill and impute missing/empty values in CSV columns."""

from typing import Iterable, Iterator, Callable, Optional


def fill_constant(
    rows: Iterable[dict],
    column: str,
    value: str,
    overwrite: bool = False,
) -> Iterator[dict]:
    """Replace empty/missing values in *column* with a constant *value*.

    Args:
        rows: Iterable of row dicts.
        column: Column name to fill.
        value: Constant fill value.
        overwrite: If True, overwrite non-empty values as well.
    """
    for row in rows:
        row = dict(row)
        current = row.get(column, "")
        if overwrite or current is None or str(current).strip() == "":
            row[column] = value
        yield row


def fill_forward(
    rows: Iterable[dict],
    column: str,
) -> Iterator[dict]:
    """Propagate the last seen non-empty value forward (forward-fill)."""
    last_seen: Optional[str] = None
    for row in rows:
        row = dict(row)
        current = row.get(column, "")
        if current is not None and str(current).strip() != "":
            last_seen = current
        elif last_seen is not None:
            row[column] = last_seen
        yield row


def fill_with_func(
    rows: Iterable[dict],
    column: str,
    func: Callable[[dict], str],
    overwrite: bool = False,
) -> Iterator[dict]:
    """Fill empty values using a callable that receives the full row.

    Args:
        rows: Iterable of row dicts.
        column: Column name to fill.
        func: Callable(row) -> str that produces the fill value.
        overwrite: If True, apply func to every row regardless.
    """
    for row in rows:
        row = dict(row)
        current = row.get(column, "")
        if overwrite or current is None or str(current).strip() == "":
            row[column] = func(row)
        yield row


def drop_empty_rows(
    rows: Iterable[dict],
    columns: Optional[list] = None,
) -> Iterator[dict]:
    """Drop rows where any of the specified columns (or all columns) are empty.

    Args:
        rows: Iterable of row dicts.
        columns: List of column names to check. If None, checks all columns.
    """
    for row in rows:
        check_cols = columns if columns is not None else list(row.keys())
        if all(
            row.get(col) is not None and str(row.get(col, "")).strip() != ""
            for col in check_cols
        ):
            yield row
