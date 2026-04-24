"""Column reshaping utilities: widen, narrow, and stack/unstack rows."""
from typing import Iterator, List, Dict, Any, Optional


def widen(
    rows: Iterator[Dict[str, Any]],
    index_col: str,
    key_col: str,
    value_col: str,
) -> List[Dict[str, Any]]:
    """Pivot long-format rows into wide format.

    Groups by *index_col*, using *key_col* values as new column names
    and *value_col* values as cell values.
    """
    buckets: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for row in rows:
        idx = row[index_col]
        if idx not in buckets:
            buckets[idx] = {index_col: idx}
            order.append(idx)
        buckets[idx][row[key_col]] = row[value_col]
    return [buckets[k] for k in order]


def narrow(
    rows: Iterator[Dict[str, Any]],
    index_col: str,
    value_columns: List[str],
    key_col: str = "key",
    value_col: str = "value",
) -> Iterator[Dict[str, Any]]:
    """Melt wide-format rows into long format.

    For each row, emits one output row per column listed in *value_columns*.
    All other columns are carried forward unchanged.
    """
    for row in rows:
        base = {k: v for k, v in row.items() if k not in value_columns}
        for col in value_columns:
            if col in row:
                yield {**base, key_col: col, value_col: row[col]}


def stack_columns(
    rows: Iterator[Dict[str, Any]],
    columns: List[str],
    output_col: str = "value",
    label_col: Optional[str] = "source",
) -> Iterator[Dict[str, Any]]:
    """Stack multiple columns into a single column.

    Emits one row per source column per input row.  If *label_col* is not
    None a column recording the original column name is added.
    """
    for row in rows:
        rest = {k: v for k, v in row.items() if k not in columns}
        for col in columns:
            out = {**rest, output_col: row.get(col, "")}
            if label_col is not None:
                out[label_col] = col
            yield out


def unstack_column(
    rows: Iterator[Dict[str, Any]],
    label_col: str,
    value_col: str,
    index_col: str,
) -> List[Dict[str, Any]]:
    """Inverse of stack_columns: spread a label+value pair back into columns."""
    buckets: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for row in rows:
        idx = row[index_col]
        if idx not in buckets:
            buckets[idx] = {index_col: idx}
            order.append(idx)
        buckets[idx][row[label_col]] = row[value_col]
    return [buckets[k] for k in order]
