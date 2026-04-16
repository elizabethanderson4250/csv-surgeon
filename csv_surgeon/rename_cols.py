"""Column renaming utilities for csv-surgeon."""
from typing import Dict, Iterable, Iterator


def rename_columns(
    rows: Iterable[Dict[str, str]],
    mapping: Dict[str, str],
    strict: bool = False,
) -> Iterator[Dict[str, str]]:
    """Yield rows with columns renamed according to *mapping*.

    Parameters
    ----------
    rows:
        Iterable of row dicts.
    mapping:
        ``{old_name: new_name}`` pairs.  Keys not present in a row are
        silently ignored unless *strict* is ``True``.
    strict:
        When ``True``, raise ``KeyError`` if a mapped column is absent from
        the first row encountered.
    """
    _validated = False
    for row in rows:
        if not _validated and strict:
            missing = [k for k in mapping if k not in row]
            if missing:
                raise KeyError(
                    f"rename_columns: columns not found in data: {missing}"
                )
            _validated = True
        yield {
            mapping.get(key, key): value
            for key, value in row.items()
        }


def reorder_columns(
    rows: Iterable[Dict[str, str]],
    order: list,
    fill_value: str = "",
) -> Iterator[Dict[str, str]]:
    """Yield rows with keys reordered (and optionally pruned / padded).

    Columns in *order* that are missing from a row are filled with
    *fill_value*.  Columns present in the row but absent from *order* are
    dropped.
    """
    for row in rows:
        yield {col: row.get(col, fill_value) for col in order}


def drop_columns(
    rows: Iterable[Dict[str, str]],
    columns: list,
) -> Iterator[Dict[str, str]]:
    """Yield rows with the specified *columns* removed."""
    drop_set = set(columns)
    for row in rows:
        yield {k: v for k, v in row.items() if k not in drop_set}


def select_columns(
    rows: Iterable[Dict[str, str]],
    columns: list,
    fill_value: str = "",
) -> Iterator[Dict[str, str]]:
    """Yield rows containing only the specified *columns* (in that order)."""
    for row in rows:
        yield {col: row.get(col, fill_value) for col in columns}
