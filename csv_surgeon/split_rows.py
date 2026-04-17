"""Row splitting utilities: split one row into multiple based on a column value."""
from typing import Iterable, Iterator, List, Optional


def split_rows(
    rows: Iterable[dict],
    column: str,
    separator: str = ",",
    strip: bool = True,
    keep_empty: bool = False,
) -> Iterator[dict]:
    """Yield one row per token found in *column* after splitting on *separator*.

    Other columns are preserved unchanged.  If the column is missing the row
    is yielded as-is.
    """
    for row in rows:
        if column not in row:
            yield row
            continue
        raw = row[column]
        tokens: List[str] = raw.split(separator)
        if strip:
            tokens = [t.strip() for t in tokens]
        if not keep_empty:
            tokens = [t for t in tokens if t]
        if not tokens:
            if keep_empty:
                yield {**row, column: ""}
            continue
        for token in tokens:
            yield {**row, column: token}


def explode_rows(
    rows: Iterable[dict],
    column: str,
    separator: str = ",",
    new_column: Optional[str] = None,
    strip: bool = True,
) -> Iterator[dict]:
    """Like split_rows but optionally writes tokens to a *new_column* leaving
    the original column intact.
    """
    target = new_column if new_column else column
    for row in rows:
        if column not in row:
            yield row
            continue
        tokens = [t.strip() if strip else t for t in row[column].split(separator)]
        tokens = [t for t in tokens if t]
        if not tokens:
            continue
        for token in tokens:
            new_row = dict(row)
            new_row[target] = token
            yield new_row
