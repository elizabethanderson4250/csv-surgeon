"""Conditional column transformations: set a column value based on conditions."""

from typing import Any, Callable, Dict, Iterable, Iterator, Optional


def if_else(
    column: str,
    condition: Callable[[Dict[str, str]], bool],
    true_value: Any,
    false_value: Any,
) -> Callable[[Dict[str, str]], Dict[str, str]]:
    """Return a transform that sets *column* based on *condition*.

    If condition(row) is truthy the cell is set to *true_value*, otherwise
    *false_value*.  Both values are coerced to ``str``.
    """

    def _transform(row: Dict[str, str]) -> Dict[str, str]:
        out = dict(row)
        out[column] = str(true_value) if condition(row) else str(false_value)
        return out

    return _transform


def set_if(
    column: str,
    condition: Callable[[Dict[str, str]], bool],
    value: Any,
) -> Callable[[Dict[str, str]], Dict[str, str]]:
    """Set *column* to *value* only when *condition* is met; leave it unchanged otherwise."""

    def _transform(row: Dict[str, str]) -> Dict[str, str]:
        out = dict(row)
        if condition(row):
            out[column] = str(value)
        return out

    return _transform


def case(
    column: str,
    cases: list,  # list of (condition_callable, value) tuples
    default: Optional[Any] = None,
) -> Callable[[Dict[str, str]], Dict[str, str]]:
    """Multi-branch conditional transform (SQL CASE-like).

    *cases* is a list of ``(condition, value)`` pairs evaluated in order.
    The first matching condition wins.  If none match, *default* is used;
    when *default* is ``None`` the column is left unchanged.
    """

    def _transform(row: Dict[str, str]) -> Dict[str, str]:
        out = dict(row)
        for condition, value in cases:
            if condition(row):
                out[column] = str(value)
                return out
        if default is not None:
            out[column] = str(default)
        return out

    return _transform


def apply_conditional(
    rows: Iterable[Dict[str, str]],
    transform: Callable[[Dict[str, str]], Dict[str, str]],
) -> Iterator[Dict[str, str]]:
    """Apply a conditional transform to every row in *rows*."""
    for row in rows:
        yield transform(row)
