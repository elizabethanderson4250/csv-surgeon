"""Tests for csv_surgeon.sort module."""

import pytest
from csv_surgeon.sort import sort_rows, sort_by_key_func


def make_rows():
    return [
        {"name": "Charlie", "age": "30", "score": "88.5"},
        {"name": "Alice", "age": "25", "score": "95.0"},
        {"name": "Bob", "age": "25", "score": "70.0"},
        {"name": "Diana", "age": "35", "score": "88.5"},
    ]


def test_sort_single_column_ascending():
    rows = make_rows()
    result = list(sort_rows(rows, key_columns=["name"]))
    names = [r["name"] for r in result]
    assert names == ["Alice", "Bob", "Charlie", "Diana"]


def test_sort_single_column_descending():
    rows = make_rows()
    result = list(sort_rows(rows, key_columns=["name"], reverse=True))
    names = [r["name"] for r in result]
    assert names == ["Diana", "Charlie", "Bob", "Alice"]


def test_sort_numeric():
    rows = make_rows()
    result = list(sort_rows(rows, key_columns=["age"], numeric=True))
    ages = [r["age"] for r in result]
    assert ages == ["25", "25", "30", "35"]


def test_sort_multi_column():
    rows = make_rows()
    # Sort by age (numeric) then name
    result = list(sort_rows(rows, key_columns=["age", "name"], numeric=False))
    # age is string-compared: '25' < '30' < '35'
    assert result[0]["age"] == "25"
    assert result[1]["age"] == "25"
    # Within age=25, Alice < Bob alphabetically
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"


def test_sort_numeric_descending():
    rows = make_rows()
    result = list(sort_rows(rows, key_columns=["score"], numeric=True, reverse=True))
    scores = [float(r["score"]) for r in result]
    assert scores == sorted(scores, reverse=True)


def test_sort_empty_rows():
    result = list(sort_rows([], key_columns=["name"]))
    assert result == []


def test_sort_no_key_columns_raises():
    with pytest.raises(ValueError, match="At least one key column"):
        list(sort_rows(make_rows(), key_columns=[]))


def test_sort_missing_key_falls_back_gracefully():
    rows = [
        {"name": "Zara"},
        {"name": "Anna"},
    ]
    # 'score' column missing from rows — should not raise
    result = list(sort_rows(rows, key_columns=["score", "name"]))
    names = [r["name"] for r in result]
    assert names == ["Anna", "Zara"]


def test_sort_by_key_func():
    rows = make_rows()
    result = list(sort_by_key_func(rows, key_func=lambda r: r["name"]))
    names = [r["name"] for r in result]
    assert names == sorted(names)


def test_sort_by_key_func_reverse():
    rows = make_rows()
    result = list(sort_by_key_func(rows, key_func=lambda r: r["name"], reverse=True))
    names = [r["name"] for r in result]
    assert names == sorted(names, reverse=True)


def test_sort_preserves_all_fields():
    rows = make_rows()
    result = list(sort_rows(rows, key_columns=["name"]))
    assert all("age" in r and "score" in r for r in result)


def test_sort_stable_preserves_original_order_for_equal_keys():
    """Verify that sort_rows is stable: rows with equal keys retain their original order."""
    rows = [
        {"name": "Alice", "age": "25", "score": "95.0"},
        {"name": "Bob", "age": "25", "score": "70.0"},
        {"name": "Charlie", "age": "30", "score": "88.5"},
    ]
    # Both Alice and Bob share age="25"; stable sort should keep Alice before Bob.
    result = list(sort_rows(rows, key_columns=["age"], numeric=True))
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"
