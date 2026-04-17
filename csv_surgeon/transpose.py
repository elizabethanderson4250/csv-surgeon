"""Transpose and pivot-style row/column swap utilities."""
from typing import Iterator, List, Dict


def transpose_to_rows(rows: List[Dict[str, str]], key_col: str = "field", value_col: str = "value") -> List[Dict[str, str]]:
    """Convert a single wide row into multiple key-value rows."""
    result = []
    for row in rows:
        for field, value in row.items():
            result.append({key_col: field, value_col: value})
    return result


def transpose_to_columns(rows: List[Dict[str, str]], key_col: str, value_col: str) -> List[Dict[str, str]]:
    """Convert key-value rows back into a single wide row.
    
    Groups by all columns except key_col and value_col, then pivots.
    """
    if not rows:
        return []
    other_cols = [c for c in rows[0] if c not in (key_col, value_col)]
    groups: Dict[tuple, Dict[str, str]] = {}
    for row in rows:
        group_key = tuple(row.get(c, "") for c in other_cols)
        if group_key not in groups:
            groups[group_key] = {c: row[c] for c in other_cols}
        groups[group_key][row[key_col]] = row[value_col]
    return list(groups.values())


def flip(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Flip rows and columns: each original column becomes a row.
    
    Column names become the first field; each row's value fills subsequent fields.
    """
    if not rows:
        return []
    headers = list(rows[0].keys())
    row_keys = [str(i) for i in range(len(rows))]
    result = []
    for h in headers:
        new_row: Dict[str, str] = {"column": h}
        for i, row in enumerate(rows):
            new_row[str(i)] = row.get(h, "")
        result.append(new_row)
    return result
