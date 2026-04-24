"""Tests for csv_surgeon.reshape."""
import pytest
from csv_surgeon.reshape import widen, narrow, stack_columns, unstack_column


def make_long_rows():
    return [
        {"id": "1", "metric": "height", "val": "180"},
        {"id": "1", "metric": "weight", "val": "75"},
        {"id": "2", "metric": "height", "val": "165"},
        {"id": "2", "metric": "weight", "val": "60"},
    ]


def make_wide_rows():
    return [
        {"id": "1", "height": "180", "weight": "75"},
        {"id": "2", "height": "165", "weight": "60"},
    ]


# --- widen ---

def test_widen_row_count():
    result = widen(iter(make_long_rows()), "id", "metric", "val")
    assert len(result) == 2


def test_widen_column_names():
    result = widen(iter(make_long_rows()), "id", "metric", "val")
    assert "height" in result[0]
    assert "weight" in result[0]


def test_widen_values_correct():
    result = widen(iter(make_long_rows()), "id", "metric", "val")
    row1 = next(r for r in result if r["id"] == "1")
    assert row1["height"] == "180"
    assert row1["weight"] == "75"


def test_widen_empty_input():
    result = widen(iter([]), "id", "metric", "val")
    assert result == []


# --- narrow ---

def test_narrow_row_count():
    result = list(narrow(iter(make_wide_rows()), "id", ["height", "weight"]))
    assert len(result) == 4


def test_narrow_key_values():
    result = list(narrow(iter(make_wide_rows()), "id", ["height", "weight"]))
    keys = {r["key"] for r in result}
    assert keys == {"height", "weight"}


def test_narrow_value_correct():
    result = list(narrow(iter(make_wide_rows()), "id", ["height", "weight"]))
    row = next(r for r in result if r["id"] == "1" and r["key"] == "height")
    assert row["value"] == "180"


def test_narrow_custom_col_names():
    result = list(narrow(iter(make_wide_rows()), "id", ["height"], key_col="attr", value_col="data"))
    assert "attr" in result[0]
    assert "data" in result[0]


def test_narrow_index_preserved():
    result = list(narrow(iter(make_wide_rows()), "id", ["height", "weight"]))
    assert all("id" in r for r in result)


# --- stack_columns ---

def test_stack_row_count():
    rows = make_wide_rows()
    result = list(stack_columns(iter(rows), ["height", "weight"]))
    assert len(result) == 4


def test_stack_label_col_present():
    rows = make_wide_rows()
    result = list(stack_columns(iter(rows), ["height", "weight"]))
    assert all("source" in r for r in result)


def test_stack_no_label_col():
    rows = make_wide_rows()
    result = list(stack_columns(iter(rows), ["height"], label_col=None))
    assert "source" not in result[0]


def test_stack_value_correct():
    rows = make_wide_rows()
    result = list(stack_columns(iter(rows), ["height", "weight"]))
    r = next(x for x in result if x["source"] == "height" and x["id"] == "1")
    assert r["value"] == "180"


# --- unstack_column ---

def test_unstack_row_count():
    long_rows = make_long_rows()
    result = unstack_column(iter(long_rows), "metric", "val", "id")
    assert len(result) == 2


def test_unstack_columns_present():
    long_rows = make_long_rows()
    result = unstack_column(iter(long_rows), "metric", "val", "id")
    assert "height" in result[0]
    assert "weight" in result[0]


def test_unstack_values_correct():
    long_rows = make_long_rows()
    result = unstack_column(iter(long_rows), "metric", "val", "id")
    row = next(r for r in result if r["id"] == "2")
    assert row["height"] == "165"
    assert row["weight"] == "60"


def test_unstack_empty_input():
    result = unstack_column(iter([]), "metric", "val", "id")
    assert result == []
