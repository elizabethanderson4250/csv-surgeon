"""Tests for csv_surgeon/stats.py"""

import pytest
from csv_surgeon.stats import column_stats, value_counts, null_counts


def make_rows(data):
    """Helper to produce an iterator of dicts."""
    return iter(data)


NUMERIC_ROWS = [
    {"name": "Alice", "score": "90"},
    {"name": "Bob",   "score": "80"},
    {"name": "Carol", "score": "100"},
    {"name": "Dave",  "score": "70"},
]

MIXED_ROWS = [
    {"name": "Alice", "score": "90"},
    {"name": "Bob",   "score": "not_a_number"},
    {"name": "Carol", "score": ""},
    {"name": "Dave",  "score": "70"},
]


def test_column_stats_count():
    stats = column_stats(make_rows(NUMERIC_ROWS), "score")
    assert stats["count"] == 4


def test_column_stats_sum():
    stats = column_stats(make_rows(NUMERIC_ROWS), "score")
    assert stats["sum"] == pytest.approx(340.0)


def test_column_stats_mean():
    stats = column_stats(make_rows(NUMERIC_ROWS), "score")
    assert stats["mean"] == pytest.approx(85.0)


def test_column_stats_min_max():
    stats = column_stats(make_rows(NUMERIC_ROWS), "score")
    assert stats["min"] == pytest.approx(70.0)
    assert stats["max"] == pytest.approx(100.0)


def test_column_stats_std_dev():
    stats = column_stats(make_rows(NUMERIC_ROWS), "score")
    assert stats["std_dev"] is not None
    assert stats["std_dev"] > 0


def test_column_stats_parse_errors():
    stats = column_stats(make_rows(MIXED_ROWS), "score")
    assert stats["parse_errors"] == 2  # "not_a_number" and ""
    assert stats["count"] == 2


def test_column_stats_empty_iterator():
    stats = column_stats(iter([]), "score")
    assert stats["count"] == 0
    assert stats["mean"] is None
    assert stats["min"] is None
    assert stats["max"] is None


def test_value_counts_basic():
    rows = [
        {"city": "NYC"},
        {"city": "LA"},
        {"city": "NYC"},
        {"city": "Chicago"},
        {"city": "LA"},
        {"city": "NYC"},
    ]
    counts = value_counts(iter(rows), "city")
    assert counts["NYC"] == 3
    assert counts["LA"] == 2
    assert counts["Chicago"] == 1


def test_value_counts_missing_column():
    rows = [{"other": "x"}, {"other": "y"}]
    counts = value_counts(iter(rows), "city")
    assert counts.get("", 0) == 2


def test_null_counts_basic():
    rows = [
        {"a": "1",  "b": ""},
        {"a": "",   "b": "hello"},
        {"a": "3",  "b": ""},
    ]
    result = null_counts(iter(rows), ["a", "b"])
    assert result["a"] == 1
    assert result["b"] == 2


def test_null_counts_no_nulls():
    rows = [{"x": "1"}, {"x": "2"}, {"x": "3"}]
    result = null_counts(iter(rows), ["x"])
    assert result["x"] == 0
