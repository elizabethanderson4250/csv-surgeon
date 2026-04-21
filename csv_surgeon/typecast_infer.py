"""Automatic type inference and casting for CSV columns."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Optional


_BOOL_TRUE = {"true", "yes", "1", "t", "y"}
_BOOL_FALSE = {"false", "no", "0", "f", "n"}


def _try_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _try_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _try_bool(value: str) -> Optional[bool]:
    lower = value.strip().lower()
    if lower in _BOOL_TRUE:
        return True
    if lower in _BOOL_FALSE:
        return False
    return None


def infer_column_types(rows: List[Dict[str, str]]) -> Dict[str, str]:
    """Scan rows and return a mapping of column -> inferred type.

    Possible types: 'int', 'float', 'bool', 'string'.
    """
    if not rows:
        return {}

    columns = list(rows[0].keys())
    candidates: Dict[str, str] = {col: "int" for col in columns}

    _order = ["int", "float", "bool", "string"]

    def _downgrade(current: str, to: str) -> str:
        return to if _order.index(to) > _order.index(current) else current

    for row in rows:
        for col in columns:
            val = row.get(col, "").strip()
            if val == "":
                continue
            current = candidates[col]
            if current == "string":
                continue
            if current == "int" and _try_int(val) is None:
                candidates[col] = _downgrade(current, "float")
                current = candidates[col]
            if current == "float" and _try_float(val) is None:
                candidates[col] = _downgrade(current, "bool")
                current = candidates[col]
            if current == "bool" and _try_bool(val) is None:
                candidates[col] = "string"

    return candidates


def cast_row(row: Dict[str, str], type_map: Dict[str, str]) -> Dict[str, Any]:
    """Return a new row with values cast according to *type_map*."""
    out: Dict[str, Any] = {}
    for col, val in row.items():
        t = type_map.get(col, "string")
        stripped = val.strip()
        if stripped == "":
            out[col] = None
        elif t == "int":
            out[col] = _try_int(stripped) if _try_int(stripped) is not None else stripped
        elif t == "float":
            out[col] = _try_float(stripped) if _try_float(stripped) is not None else stripped
        elif t == "bool":
            b = _try_bool(stripped)
            out[col] = b if b is not None else stripped
        else:
            out[col] = val
    return out


def auto_cast_rows(
    rows: Iterable[Dict[str, str]],
    sample_size: int = 200,
) -> Iterator[Dict[str, Any]]:
    """Infer types from the first *sample_size* rows then cast all rows."""
    buffer: List[Dict[str, str]] = []
    rest: List[Dict[str, str]] = []
    for i, row in enumerate(rows):
        if i < sample_size:
            buffer.append(row)
        else:
            rest.append(row)

    type_map = infer_column_types(buffer)
    for row in buffer:
        yield cast_row(row, type_map)
    for row in rest:
        yield cast_row(row, type_map)
