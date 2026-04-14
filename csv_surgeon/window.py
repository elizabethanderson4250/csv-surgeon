"""Window/rolling operations on streaming CSV rows."""
from collections import deque
from typing import Callable, Dict, Generator, Iterable, List, Optional


def rolling_window(
    rows: Iterable[Dict[str, str]],
    size: int,
) -> Generator[List[Dict[str, str]], None, None]:
    """Yield successive overlapping windows of `size` rows."""
    if size < 1:
        raise ValueError("Window size must be at least 1")
    buf: deque = deque(maxlen=size)
    for row in rows:
        buf.append(row)
        if len(buf) == size:
            yield list(buf)


def rolling_aggregate(
    rows: Iterable[Dict[str, str]],
    column: str,
    size: int,
    func: Callable[[List[float]], float],
    output_column: Optional[str] = None,
) -> Generator[Dict[str, str], None, None]:
    """Apply a rolling aggregate function over a numeric column.

    Rows that don't yet have a full window emit an empty string for the
    output column.
    """
    if size < 1:
        raise ValueError("Window size must be at least 1")
    out_col = output_column or f"{column}_rolling"
    buf: deque = deque(maxlen=size)
    for row in rows:
        raw = row.get(column, "")
        try:
            buf.append(float(raw))
        except (ValueError, TypeError):
            buf.append(None)  # type: ignore[arg-type]
        new_row = dict(row)
        if len(buf) == size and all(v is not None for v in buf):
            new_row[out_col] = str(func(list(buf)))  # type: ignore[arg-type]
        else:
            new_row[out_col] = ""
        yield new_row


def lag(
    rows: Iterable[Dict[str, str]],
    column: str,
    periods: int = 1,
    output_column: Optional[str] = None,
    fill_value: str = "",
) -> Generator[Dict[str, str], None, None]:
    """Add a lagged version of *column* shifted back by *periods* rows."""
    if periods < 1:
        raise ValueError("periods must be at least 1")
    out_col = output_column or f"{column}_lag{periods}"
    buf: deque = deque(maxlen=periods)
    for row in rows:
        new_row = dict(row)
        if len(buf) < periods:
            new_row[out_col] = fill_value
        else:
            new_row[out_col] = buf[0]
        buf.append(row.get(column, fill_value))
        yield new_row
