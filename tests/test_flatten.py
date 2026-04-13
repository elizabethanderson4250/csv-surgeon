"""Tests for csv_surgeon/flatten.py."""
import pytest
from csv_surgeon.flatten import flatten_column, merge_columns, split_column


# ---------------------------------------------------------------------------
# flatten_column
# ---------------------------------------------------------------------------

def test_flatten_column_basic():
    rows = [{"id": "1", "tags": "a|b|c"}]
    result = list(flatten_column(rows, "tags"))
    assert len(result) == 3
    assert [r["tags"] for r in result] == ["a", "b", "c"]


def test_flatten_column_preserves_other_fields():
    rows = [{"id": "42", "tags": "x|y"}]
    result = list(flatten_column(rows, "tags"))
    assert all(r["id"] == "42" for r in result)


def test_flatten_column_custom_separator():
    rows = [{"id": "1", "vals": "1,2,3"}]
    result = list(flatten_column(rows, "vals", separator=","))
    assert len(result) == 3


def test_flatten_column_strips_whitespace():
    rows = [{"id": "1", "tags": " a | b "}]
    result = list(flatten_column(rows, "tags"))
    assert result[0]["tags"] == "a"
    assert result[1]["tags"] == "b"


def test_flatten_column_no_strip():
    rows = [{"id": "1", "tags": " a | b "}]
    result = list(flatten_column(rows, "tags", strip=False))
    assert result[0]["tags"] == " a "


def test_flatten_column_empty_value_yields_row_as_is():
    rows = [{"id": "1", "tags": ""}]
    result = list(flatten_column(rows, "tags"))
    assert result == rows


def test_flatten_column_missing_column_yields_row_as_is():
    rows = [{"id": "1"}]
    result = list(flatten_column(rows, "tags"))
    assert result == rows


def test_flatten_column_single_value_yields_one_row():
    rows = [{"id": "1", "tags": "only"}]
    result = list(flatten_column(rows, "tags"))
    assert len(result) == 1
    assert result[0]["tags"] == "only"


# ---------------------------------------------------------------------------
# merge_columns
# ---------------------------------------------------------------------------

def test_merge_columns_basic():
    rows = [{"first": "John", "last": "Doe"}]
    result = list(merge_columns(rows, ["first", "last"], into="full_name"))
    assert result[0]["full_name"] == "John Doe"


def test_merge_columns_drops_originals_by_default():
    rows = [{"first": "John", "last": "Doe"}]
    result = list(merge_columns(rows, ["first", "last"], into="full_name"))
    assert "first" not in result[0]
    assert "last" not in result[0]


def test_merge_columns_keeps_originals_when_requested():
    rows = [{"first": "John", "last": "Doe"}]
    result = list(merge_columns(rows, ["first", "last"], into="full_name", drop_originals=False))
    assert "first" in result[0]
    assert "last" in result[0]


def test_merge_columns_custom_separator():
    rows = [{"a": "foo", "b": "bar"}]
    result = list(merge_columns(rows, ["a", "b"], into="c", separator="-"))
    assert result[0]["c"] == "foo-bar"


# ---------------------------------------------------------------------------
# split_column
# ---------------------------------------------------------------------------

def test_split_column_basic():
    rows = [{"full_name": "John Doe"}]
    result = list(split_column(rows, "full_name", into=["first", "last"]))
    assert result[0]["first"] == "John"
    assert result[0]["last"] == "Doe"


def test_split_column_drops_original_by_default():
    rows = [{"full_name": "John Doe"}]
    result = list(split_column(rows, "full_name", into=["first", "last"]))
    assert "full_name" not in result[0]


def test_split_column_keeps_original_when_requested():
    rows = [{"full_name": "John Doe"}]
    result = list(split_column(rows, "full_name", into=["first", "last"], drop_original=False))
    assert "full_name" in result[0]


def test_split_column_fewer_parts_fills_empty():
    rows = [{"name": "Solo"}]
    result = list(split_column(rows, "name", into=["first", "last"]))
    assert result[0]["first"] == "Solo"
    assert result[0]["last"] == ""


def test_split_column_custom_separator():
    rows = [{"date": "2024-01-15"}]
    result = list(split_column(rows, "date", into=["year", "month", "day"], separator="-"))
    assert result[0]["year"] == "2024"
    assert result[0]["month"] == "01"
    assert result[0]["day"] == "15"
