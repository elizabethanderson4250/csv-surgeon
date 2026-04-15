"""Computed column support: derive new columns from existing ones."""
from __future__ import annotations

import ast
import operator
from typing import Callable, Dict, Iterable, Iterator


_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}


def add_column(
    rows: Iterable[Dict[str, str]],
    name: str,
    func: Callable[[Dict[str, str]], str],
) -> Iterator[Dict[str, str]]:
    """Yield rows with a new column *name* whose value is produced by *func*."""
    for row in rows:
        new_row = dict(row)
        new_row[name] = str(func(row))
        yield new_row


def compute_expression(
    rows: Iterable[Dict[str, str]],
    name: str,
    expression: str,
) -> Iterator[Dict[str, str]]:
    """Yield rows with a new column *name* = result of a simple arithmetic
    expression referencing other column names, e.g. ``"price * quantity"``.

    Only numeric literals, column references, and the operators +, -, *, /, %
    are supported (no builtins, no attribute access).
    """
    for row in rows:
        new_row = dict(row)
        try:
            result = _eval_expr(expression, row)
            # Render as int string when result is a whole number
            new_row[name] = str(int(result)) if result == int(result) else str(result)
        except Exception:
            new_row[name] = ""
        yield new_row


def copy_column(
    rows: Iterable[Dict[str, str]],
    source: str,
    dest: str,
) -> Iterator[Dict[str, str]]:
    """Yield rows with column *dest* copied from *source*."""
    for row in rows:
        new_row = dict(row)
        new_row[dest] = row.get(source, "")
        yield new_row


def drop_column(
    rows: Iterable[Dict[str, str]],
    name: str,
) -> Iterator[Dict[str, str]]:
    """Yield rows with column *name* removed."""
    for row in rows:
        new_row = {k: v for k, v in row.items() if k != name}
        yield new_row


# ---------------------------------------------------------------------------
# Internal safe expression evaluator
# ---------------------------------------------------------------------------

def _eval_expr(expr: str, row: Dict[str, str]) -> float:
    tree = ast.parse(expr, mode="eval")
    return _eval_node(tree.body, row)


def _eval_node(node: ast.AST, row: Dict[str, str]) -> float:
    if isinstance(node, ast.Constant):
        return float(node.value)
    if isinstance(node, ast.Name):
        return float(row[node.id])
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"Unsupported operator: {op_type}")
        left = _eval_node(node.left, row)
        right = _eval_node(node.right, row)
        return _SAFE_OPS[op_type](left, right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_node(node.operand, row)
    raise ValueError(f"Unsupported AST node: {type(node)}")
