"""Column value formatting transforms."""
import re
from typing import Callable, Optional


def _formatter(col: str, func: Callable[[str], str]) -> Callable[[dict], dict]:
    def _transform(row: dict) -> dict:
        if col not in row:
            return row
        result = dict(row)
        result[col] = func(row[col])
        return result
    return _transform


def zero_pad(col: str, width: int) -> Callable[[dict], dict]:
    """Left-pad numeric strings with zeros to a given width."""
    return _formatter(col, lambda v: v.zfill(width))


def title_case(col: str) -> Callable[[dict], dict]:
    """Convert column value to title case."""
    return _formatter(col, str.title)


def wrap(col: str, prefix: str = "", suffix: str = "") -> Callable[[dict], dict]:
    """Wrap column value with a prefix and/or suffix."""
    return _formatter(col, lambda v: f"{prefix}{v}{suffix}")


def number_format(col: str, decimals: int = 2, thousands_sep: bool = False) -> Callable[[dict], dict]:
    """Format a numeric column value to a fixed number of decimal places."""
    def _fmt(v: str) -> str:
        try:
            num = float(v)
            if thousands_sep:
                return f"{num:,.{decimals}f}"
            return f"{num:.{decimals}f}"
        except (ValueError, TypeError):
            return v
    return _formatter(col, _fmt)


def strip_chars(col: str, chars: Optional[str] = None) -> Callable[[dict], dict]:
    """Strip leading/trailing characters from column value."""
    return _formatter(col, lambda v: v.strip(chars))


def remove_non_alphanumeric(col: str, keep_spaces: bool = False) -> Callable[[dict], dict]:
    """Remove non-alphanumeric characters from column value."""
    def _clean(v: str) -> str:
        pattern = r'[^a-zA-Z0-9 ]' if keep_spaces else r'[^a-zA-Z0-9]'
        return re.sub(pattern, '', v)
    return _formatter(col, _clean)
