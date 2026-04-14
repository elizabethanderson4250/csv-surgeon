"""Column type casting transformations for CSV rows."""

from typing import Callable, Dict, Any, Optional


def _caster(col: str, cast_fn: Callable[[str], Any], default: Optional[Any] = None):
    """Return a transform function that casts a column value using cast_fn."""
    def _transform(row: Dict[str, str]) -> Dict[str, Any]:
        if col not in row:
            return row
        try:
            row[col] = cast_fn(row[col])
        except (ValueError, TypeError):
            row[col] = default
        return row
    return _transform


def to_int(col: str, default: Optional[int] = None) -> Callable:
    """Cast a column's values to int."""
    return _caster(col, int, default)


def to_float(col: str, default: Optional[float] = None) -> Callable:
    """Cast a column's values to float."""
    return _caster(col, float, default)


def to_bool(col: str, true_values=None, false_values=None, default: Optional[bool] = None) -> Callable:
    """Cast a column's values to bool based on configurable true/false value sets."""
    if true_values is None:
        true_values = {"true", "1", "yes", "y"}
    if false_values is None:
        false_values = {"false", "0", "no", "n"}

    def _parse_bool(val: str) -> bool:
        normalized = val.strip().lower()
        if normalized in true_values:
            return True
        if normalized in false_values:
            return False
        raise ValueError(f"Cannot cast {val!r} to bool")

    return _caster(col, _parse_bool, default)


def to_str(col: str, default: Optional[str] = "") -> Callable:
    """Cast a column's values to str (strips whitespace)."""
    def _strip_str(val: str) -> str:
        return str(val).strip()
    return _caster(col, _strip_str, default)


def apply_casts(row: Dict[str, Any], casts: list) -> Dict[str, Any]:
    """Apply a list of cast functions to a row sequentially."""
    for cast_fn in casts:
        row = cast_fn(row)
    return row
