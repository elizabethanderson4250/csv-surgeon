"""Tests for csv_surgeon/compute.py."""
import pytest
from csv_surgeon.compute import (
    add_column,
    compute_expression,
    copy_column,
    drop_column,
)


def make_rows():
    return [
        {"name": "apple", "price": "1.50", "qty": "4"},
        {"name": "banana", "price": "0.75", "qty": "10"},
        {"name": "cherry", "price": "3.00", "qty": "2"},
    ]


# --- add_column ---

def test_add_column_appends_new_key():
    rows = make_rows()
    result = list(add_column(rows, "upper_name", lambda r: r["name"].upper()))
    assert all("upper_name" in r for r in result)


def test_add_column_correct_values():
    rows = make_rows()
    result = list(add_column(rows, "upper_name", lambda r: r["name"].upper()))
    assert result[0]["upper_name"] == "APPLE"
    assert result[1]["upper_name"] == "BANANA"


def test_add_column_does_not_mutate_original():
    rows = make_rows()
    _ = list(add_column(rows, "x", lambda r: "1"))
    assert "x" not in rows[0]


# --- compute_expression ---

def test_compute_expression_multiplication():
    rows = make_rows()
    result = list(compute_expression(rows, "total", "price * qty"))
    assert result[0]["total"] == "6"   # 1.5 * 4 = 6.0 -> "6"
    assert result[1]["total"] == "7.5"


def test_compute_expression_addition():
    rows = [{"a": "3", "b": "4"}]
    result = list(compute_expression(rows, "sum", "a + b"))
    assert result[0]["sum"] == "7"


def test_compute_expression_subtraction():
    rows = [{"a": "10", "b": "3"}]
    result = list(compute_expression(rows, "diff", "a - b"))
    assert result[0]["diff"] == "7"


def test_compute_expression_division():
    rows = [{"a": "9", "b": "2"}]
    result = list(compute_expression(rows, "div", "a / b"))
    assert result[0]["div"] == "4.5"


def test_compute_expression_modulo():
    rows = [{"a": "10", "b": "3"}]
    result = list(compute_expression(rows, "mod", "a % b"))
    assert result[0]["mod"] == "1"


def test_compute_expression_invalid_column_yields_empty():
    rows = [{"a": "5"}]
    result = list(compute_expression(rows, "bad", "a + nonexistent"))
    assert result[0]["bad"] == ""


def test_compute_expression_non_numeric_yields_empty():
    rows = [{"a": "hello", "b": "2"}]
    result = list(compute_expression(rows, "out", "a + b"))
    assert result[0]["out"] == ""


# --- copy_column ---

def test_copy_column_creates_dest():
    rows = make_rows()
    result = list(copy_column(rows, "name", "label"))
    assert all("label" in r for r in result)


def test_copy_column_values_match_source():
    rows = make_rows()
    result = list(copy_column(rows, "name", "label"))
    for orig, new in zip(rows, result):
        assert new["label"] == orig["name"]


def test_copy_column_missing_source_yields_empty():
    rows = [{"a": "1"}]
    result = list(copy_column(rows, "missing", "dest"))
    assert result[0]["dest"] == ""


# --- drop_column ---

def test_drop_column_removes_key():
    rows = make_rows()
    result = list(drop_column(rows, "price"))
    assert all("price" not in r for r in result)


def test_drop_column_preserves_other_keys():
    rows = make_rows()
    result = list(drop_column(rows, "price"))
    assert all("name" in r and "qty" in r for r in result)


def test_drop_column_missing_column_no_error():
    rows = make_rows()
    result = list(drop_column(rows, "nonexistent"))
    assert len(result) == len(rows)
