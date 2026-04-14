"""Tests for csv_surgeon/fill.py"""

import pytest
from csv_surgeon.fill import (
    fill_constant,
    fill_forward,
    fill_with_func,
    drop_empty_rows,
)


def make_rows(*dicts):
    return list(dicts)


# ---------------------------------------------------------------------------
# fill_constant
# ---------------------------------------------------------------------------

def test_fill_constant_replaces_empty_string():
    rows = make_rows({"a": "", "b": "x"}, {"a": "hello", "b": "y"})
    result = list(fill_constant(rows, "a", "DEFAULT"))
    assert result[0]["a"] == "DEFAULT"
    assert result[1]["a"] == "hello"


def test_fill_constant_replaces_whitespace_only():
    rows = make_rows({"a": "   "})
    result = list(fill_constant(rows, "a", "N/A"))
    assert result[0]["a"] == "N/A"


def test_fill_constant_does_not_overwrite_by_default():
    rows = make_rows({"a": "keep"})
    result = list(fill_constant(rows, "a", "REPLACED"))
    assert result[0]["a"] == "keep"


def test_fill_constant_overwrites_when_flag_set():
    rows = make_rows({"a": "keep"})
    result = list(fill_constant(rows, "a", "REPLACED", overwrite=True))
    assert result[0]["a"] == "REPLACED"


def test_fill_constant_missing_column_gets_value():
    rows = make_rows({"b": "1"})
    result = list(fill_constant(rows, "a", "FILL"))
    assert result[0]["a"] == "FILL"


# ---------------------------------------------------------------------------
# fill_forward
# ---------------------------------------------------------------------------

def test_fill_forward_propagates_last_value():
    rows = make_rows(
        {"a": "first"},
        {"a": ""},
        {"a": ""},
        {"a": "second"},
        {"a": ""},
    )
    result = list(fill_forward(rows, "a"))
    assert result[1]["a"] == "first"
    assert result[2]["a"] == "first"
    assert result[4]["a"] == "second"


def test_fill_forward_no_previous_value_stays_empty():
    rows = make_rows({"a": ""}, {"a": "value"})
    result = list(fill_forward(rows, "a"))
    assert result[0]["a"] == ""


def test_fill_forward_does_not_mutate_input():
    original = {"a": "x"}
    rows = [original]
    list(fill_forward(rows, "a"))
    assert original["a"] == "x"


# ---------------------------------------------------------------------------
# fill_with_func
# ---------------------------------------------------------------------------

def test_fill_with_func_uses_callable():
    rows = make_rows({"a": "", "b": "hello"})
    result = list(fill_with_func(rows, "a", lambda row: row["b"].upper()))
    assert result[0]["a"] == "HELLO"


def test_fill_with_func_skips_non_empty_by_default():
    rows = make_rows({"a": "keep", "b": "other"})
    result = list(fill_with_func(rows, "a", lambda row: "REPLACED"))
    assert result[0]["a"] == "keep"


def test_fill_with_func_overwrite_applies_to_all():
    rows = make_rows({"a": "keep", "b": "src"})
    result = list(fill_with_func(rows, "a", lambda row: "NEW", overwrite=True))
    assert result[0]["a"] == "NEW"


# ---------------------------------------------------------------------------
# drop_empty_rows
# ---------------------------------------------------------------------------

def test_drop_empty_rows_removes_rows_with_empty_column():
    rows = make_rows({"a": "1", "b": ""}, {"a": "2", "b": "ok"})
    result = list(drop_empty_rows(rows, columns=["b"]))
    assert len(result) == 1
    assert result[0]["a"] == "2"


def test_drop_empty_rows_checks_all_columns_when_none_specified():
    rows = make_rows({"a": "", "b": "ok"}, {"a": "1", "b": "2"})
    result = list(drop_empty_rows(rows))
    assert len(result) == 1


def test_drop_empty_rows_keeps_all_when_no_empties():
    rows = make_rows({"a": "1"}, {"a": "2"}, {"a": "3"})
    result = list(drop_empty_rows(rows))
    assert len(result) == 3
