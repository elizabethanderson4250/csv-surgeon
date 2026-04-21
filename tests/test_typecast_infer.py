"""Tests for csv_surgeon.typecast_infer."""
import pytest
from csv_surgeon.typecast_infer import (
    infer_column_types,
    cast_row,
    auto_cast_rows,
)


def make_rows(*dicts):
    return list(dicts)


# --- infer_column_types ---

def test_infer_integer_column():
    rows = make_rows({"age": "25"}, {"age": "30"}, {"age": "0"})
    result = infer_column_types(rows)
    assert result["age"] == "int"


def test_infer_float_column():
    rows = make_rows({"score": "1.5"}, {"score": "2.0"})
    result = infer_column_types(rows)
    assert result["score"] == "float"


def test_infer_bool_column():
    rows = make_rows({"active": "true"}, {"active": "false"}, {"active": "yes"})
    result = infer_column_types(rows)
    assert result["active"] == "bool"


def test_infer_string_column():
    rows = make_rows({"name": "Alice"}, {"name": "Bob"})
    result = infer_column_types(rows)
    assert result["name"] == "string"


def test_infer_mixed_int_float_becomes_float():
    rows = make_rows({"val": "1"}, {"val": "2.5"})
    result = infer_column_types(rows)
    assert result["val"] == "float"


def test_infer_empty_values_ignored():
    rows = make_rows({"x": ""}, {"x": "3"}, {"x": "7"})
    result = infer_column_types(rows)
    assert result["x"] == "int"


def test_infer_all_empty_stays_int():
    rows = make_rows({"x": ""}, {"x": ""})
    result = infer_column_types(rows)
    # no evidence to downgrade, stays at default 'int'
    assert result["x"] == "int"


def test_infer_empty_rows_returns_empty():
    assert infer_column_types([]) == {}


# --- cast_row ---

def test_cast_row_int():
    row = {"n": "42"}
    result = cast_row(row, {"n": "int"})
    assert result["n"] == 42


def test_cast_row_float():
    row = {"n": "3.14"}
    result = cast_row(row, {"n": "float"})
    assert abs(result["n"] - 3.14) < 1e-9


def test_cast_row_bool_true():
    row = {"flag": "yes"}
    result = cast_row(row, {"flag": "bool"})
    assert result["flag"] is True


def test_cast_row_bool_false():
    row = {"flag": "0"}
    result = cast_row(row, {"flag": "bool"})
    assert result["flag"] is False


def test_cast_row_string_unchanged():
    row = {"name": "Alice"}
    result = cast_row(row, {"name": "string"})
    assert result["name"] == "Alice"


def test_cast_row_empty_becomes_none():
    row = {"n": ""}
    result = cast_row(row, {"n": "int"})
    assert result["n"] is None


def test_cast_row_does_not_mutate_original():
    row = {"n": "5"}
    cast_row(row, {"n": "int"})
    assert row["n"] == "5"


# --- auto_cast_rows ---

def test_auto_cast_rows_basic():
    raw = [{"age": "10", "name": "Alice"}, {"age": "20", "name": "Bob"}]
    result = list(auto_cast_rows(iter(raw)))
    assert result[0]["age"] == 10
    assert result[1]["age"] == 20
    assert result[0]["name"] == "Alice"


def test_auto_cast_rows_overflow_sample():
    """Rows beyond sample_size should still be cast correctly."""
    raw = [{"n": str(i)} for i in range(10)]
    result = list(auto_cast_rows(iter(raw), sample_size=3))
    assert all(isinstance(r["n"], int) for r in result)


def test_auto_cast_rows_empty():
    result = list(auto_cast_rows(iter([])))
    assert result == []
