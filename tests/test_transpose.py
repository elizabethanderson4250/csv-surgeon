"""Tests for csv_surgeon/transpose.py"""
import pytest
from csv_surgeon.transpose import transpose_to_rows, transpose_to_columns, flip


def make_wide_rows():
    return [
        {"name": "Alice", "age": "30", "city": "NY"},
        {"name": "Bob", "age": "25", "city": "LA"},
    ]


def make_kv_rows():
    return [
        {"field": "name", "value": "Alice"},
        {"field": "age", "value": "30"},
        {"field": "city", "value": "NY"},
    ]


def test_transpose_to_rows_count():
    rows = make_wide_rows()
    result = transpose_to_rows(rows)
    assert len(result) == 6  # 2 rows * 3 cols


def test_transpose_to_rows_keys():
    rows = [{"name": "Alice", "age": "30"}]
    result = transpose_to_rows(rows)
    fields = [r["field"] for r in result]
    assert "name" in fields
    assert "age" in fields


def test_transpose_to_rows_values():
    rows = [{"name": "Alice"}]
    result = transpose_to_rows(rows)
    assert result[0]["value"] == "Alice"


def test_transpose_to_rows_custom_col_names():
    rows = [{"x": "1"}]
    result = transpose_to_rows(rows, key_col="k", value_col="v")
    assert "k" in result[0]
    assert "v" in result[0]


def test_transpose_to_rows_empty():
    assert transpose_to_rows([]) == []


def test_transpose_to_columns_roundtrip():
    wide = [{"name": "Alice", "age": "30"}]
    kv = transpose_to_rows(wide)
    back = transpose_to_columns(kv, key_col="field", value_col="value")
    assert back[0]["name"] == "Alice"
    assert back[0]["age"] == "30"


def test_transpose_to_columns_empty():
    assert transpose_to_columns([], "field", "value") == []


def test_flip_returns_one_row_per_column():
    rows = make_wide_rows()
    result = flip(rows)
    assert len(result) == 3  # name, age, city


def test_flip_column_name_field():
    rows = [{"x": "1", "y": "2"}]
    result = flip(rows)
    cols = [r["column"] for r in result]
    assert "x" in cols
    assert "y" in cols


def test_flip_values_correct():
    rows = [{"score": "99"}]
    result = flip(rows)
    assert result[0]["0"] == "99"


def test_flip_empty():
    assert flip([]) == []
