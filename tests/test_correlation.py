"""Tests for csv_surgeon.correlation."""
from __future__ import annotations

import math
import pytest

from csv_surgeon.correlation import (
    _pearson,
    _safe_float,
    correlate_columns,
    correlation_matrix,
)


def make_rows(pairs: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"x": a, "y": b} for a, b in pairs]


# ---------------------------------------------------------------------------
# _safe_float
# ---------------------------------------------------------------------------

def test_safe_float_valid():
    assert _safe_float("3.14") == pytest.approx(3.14)


def test_safe_float_invalid_returns_none():
    assert _safe_float("abc") is None


def test_safe_float_empty_returns_none():
    assert _safe_float("") is None


# ---------------------------------------------------------------------------
# _pearson
# ---------------------------------------------------------------------------

def test_pearson_perfect_positive():
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [2.0, 4.0, 6.0, 8.0]
    assert _pearson(xs, ys) == pytest.approx(1.0)


def test_pearson_perfect_negative():
    xs = [1.0, 2.0, 3.0]
    ys = [6.0, 4.0, 2.0]
    assert _pearson(xs, ys) == pytest.approx(-1.0)


def test_pearson_no_correlation():
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [5.0, 5.0, 5.0, 5.0]  # zero std_y
    assert _pearson(xs, ys) is None


def test_pearson_too_few_points():
    assert _pearson([1.0], [2.0]) is None


def test_pearson_empty():
    assert _pearson([], []) is None


# ---------------------------------------------------------------------------
# correlate_columns
# ---------------------------------------------------------------------------

def test_correlate_columns_perfect_positive():
    rows = make_rows([("1", "2"), ("2", "4"), ("3", "6")])
    r = correlate_columns(iter(rows), "x", "y")
    assert r == pytest.approx(1.0)


def test_correlate_columns_skips_non_numeric():
    rows = make_rows([("1", "2"), ("N/A", "4"), ("3", "6")])
    r = correlate_columns(iter(rows), "x", "y")
    # Only two valid pairs: (1,2) and (3,6) — still perfect positive
    assert r == pytest.approx(1.0)


def test_correlate_columns_missing_column_returns_none():
    rows = [{"a": "1", "b": "2"}]
    r = correlate_columns(iter(rows), "a", "z")
    assert r is None


def test_correlate_columns_all_non_numeric_returns_none():
    rows = make_rows([("x", "y"), ("a", "b")])
    r = correlate_columns(iter(rows), "x", "y")
    assert r is None


# ---------------------------------------------------------------------------
# correlation_matrix
# ---------------------------------------------------------------------------

def test_correlation_matrix_keys():
    rows = [{"a": "1", "b": "2", "c": "3"}, {"a": "2", "b": "4", "c": "6"}]
    matrix = correlation_matrix(rows, ["a", "b", "c"])
    assert ("a", "b") in matrix
    assert ("b", "a") in matrix
    assert ("a", "a") in matrix


def test_correlation_matrix_symmetric():
    rows = [{"a": str(i), "b": str(i * 2)} for i in range(1, 6)]
    matrix = correlation_matrix(rows, ["a", "b"])
    assert matrix[("a", "b")] == pytest.approx(matrix[("b", "a")])


def test_correlation_matrix_self_correlation_is_one():
    rows = [{"a": str(i)} for i in range(1, 5)]
    matrix = correlation_matrix(rows, ["a"])
    assert matrix[("a", "a")] == pytest.approx(1.0)
