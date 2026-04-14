"""Tests for csv_surgeon.cast module."""

import pytest
from csv_surgeon.cast import to_int, to_float, to_bool, to_str, apply_casts


def make_row(**kwargs):
    return {k: str(v) for k, v in kwargs.items()}


# --- to_int ---

def test_to_int_converts_valid_value():
    row = make_row(age="42")
    result = to_int("age")(row)
    assert result["age"] == 42
    assert isinstance(result["age"], int)


def test_to_int_invalid_uses_default():
    row = make_row(age="not_a_number")
    result = to_int("age", default=-1)(row)
    assert result["age"] == -1


def test_to_int_missing_column_unchanged():
    row = make_row(name="Alice")
    result = to_int("age")(row)
    assert "age" not in result


# --- to_float ---

def test_to_float_converts_valid_value():
    row = make_row(score="3.14")
    result = to_float("score")(row)
    assert abs(result["score"] - 3.14) < 1e-9


def test_to_float_invalid_uses_default():
    row = make_row(score="n/a")
    result = to_float("score", default=0.0)(row)
    assert result["score"] == 0.0


# --- to_bool ---

@pytest.mark.parametrize("val", ["true", "True", "TRUE", "1", "yes", "YES", "y"])
def test_to_bool_true_values(val):
    row = {"active": val}
    result = to_bool("active")(row)
    assert result["active"] is True


@pytest.mark.parametrize("val", ["false", "False", "FALSE", "0", "no", "NO", "n"])
def test_to_bool_false_values(val):
    row = {"active": val}
    result = to_bool("active")(row)
    assert result["active"] is False


def test_to_bool_invalid_uses_default():
    row = {"active": "maybe"}
    result = to_bool("active", default=None)(row)
    assert result["active"] is None


# --- to_str ---

def test_to_str_strips_whitespace():
    row = {"name": "  Alice  "}
    result = to_str("name")(row)
    assert result["name"] == "Alice"


def test_to_str_numeric_to_string():
    row = {"count": "007"}
    result = to_str("count")(row)
    assert result["count"] == "007"


# --- apply_casts ---

def test_apply_casts_multiple_columns():
    row = {"age": "30", "score": "9.5", "active": "true"}
    casts = [to_int("age"), to_float("score"), to_bool("active")]
    result = apply_casts(row, casts)
    assert result["age"] == 30
    assert abs(result["score"] - 9.5) < 1e-9
    assert result["active"] is True


def test_apply_casts_empty_list_unchanged():
    row = {"age": "30"}
    result = apply_casts(row, [])
    assert result == {"age": "30"}
