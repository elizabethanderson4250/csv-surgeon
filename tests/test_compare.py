"""Tests for csv_surgeon.compare module."""
import pytest
from csv_surgeon.compare import compare_column, flag_changed, diff_columns


def rows_from(data):
    return iter(data)


# --- compare_column ---

def test_compare_column_less_than():
    rows = [{"a": "1", "b": "2"}]
    result = list(compare_column(rows_from(rows), "a", "b"))
    assert result[0]["_cmp"] == "-1"


def test_compare_column_equal():
    rows = [{"a": "5", "b": "5"}]
    result = list(compare_column(rows_from(rows), "a", "b"))
    assert result[0]["_cmp"] == "0"


def test_compare_column_greater_than():
    rows = [{"a": "10", "b": "3"}]
    result = list(compare_column(rows_from(rows), "a", "b"))
    assert result[0]["_cmp"] == "1"


def test_compare_column_lexicographic_fallback():
    rows = [{"a": "apple", "b": "banana"}]
    result = list(compare_column(rows_from(rows), "a", "b"))
    assert result[0]["_cmp"] == "-1"


def test_compare_column_custom_result_col():
    rows = [{"x": "3", "y": "1"}]
    result = list(compare_column(rows_from(rows), "x", "y", result_col="cmp_out"))
    assert "cmp_out" in result[0]
    assert result[0]["cmp_out"] == "1"


def test_compare_column_preserves_other_fields():
    rows = [{"a": "1", "b": "2", "extra": "hello"}]
    result = list(compare_column(rows_from(rows), "a", "b"))
    assert result[0]["extra"] == "hello"


# --- flag_changed ---

def test_flag_changed_first_row_not_flagged():
    rows = [{"a": "1"}, {"a": "2"}]
    result = list(flag_changed(rows_from(rows), ["a"]))
    assert result[0]["_changed"] == "0"


def test_flag_changed_detects_change():
    rows = [{"a": "1"}, {"a": "2"}]
    result = list(flag_changed(rows_from(rows), ["a"]))
    assert result[1]["_changed"] == "1"


def test_flag_changed_no_change():
    rows = [{"a": "1"}, {"a": "1"}]
    result = list(flag_changed(rows_from(rows), ["a"]))
    assert result[1]["_changed"] == "0"


def test_flag_changed_multiple_columns():
    rows = [{"a": "1", "b": "x"}, {"a": "1", "b": "y"}]
    result = list(flag_changed(rows_from(rows), ["a", "b"]))
    assert result[1]["_changed"] == "1"


# --- diff_columns ---

def test_diff_columns_basic():
    rows = [{"a": "10", "b": "3"}]
    result = list(diff_columns(rows_from(rows), "a", "b"))
    assert float(result[0]["_diff"]) == pytest.approx(7.0)


def test_diff_columns_negative():
    rows = [{"a": "2", "b": "5"}]
    result = list(diff_columns(rows_from(rows), "a", "b"))
    assert float(result[0]["_diff"]) == pytest.approx(-3.0)


def test_diff_columns_non_numeric_uses_default():
    rows = [{"a": "foo", "b": "bar"}]
    result = list(diff_columns(rows_from(rows), "a", "b", default="N/A"))
    assert result[0]["_diff"] == "N/A"


def test_diff_columns_custom_result_col():
    rows = [{"a": "9", "b": "4"}]
    result = list(diff_columns(rows_from(rows), "a", "b", result_col="delta"))
    assert "delta" in result[0]
