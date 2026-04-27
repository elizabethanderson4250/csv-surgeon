"""Unit tests for csv_surgeon.regex_filter."""
import pytest
from csv_surgeon.regex_filter import (
    filter_all_columns,
    filter_any_column,
    filter_by_regex,
)


def make_rows():
    return [
        {"name": "Alice", "city": "Amsterdam", "score": "90"},
        {"name": "Bob", "city": "Berlin", "score": "75"},
        {"name": "Charlie", "city": "amsterdam", "score": "88"},
        {"name": "Diana", "city": "Dublin", "score": "55"},
    ]


def test_filter_by_regex_basic_match():
    result = list(filter_by_regex(make_rows(), "city", r"^Ber"))
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


def test_filter_by_regex_no_match_returns_empty():
    result = list(filter_by_regex(make_rows(), "city", r"^ZZZ"))
    assert result == []


def test_filter_by_regex_ignore_case():
    result = list(filter_by_regex(make_rows(), "city", r"amsterdam", ignore_case=True))
    assert len(result) == 2
    names = {r["name"] for r in result}
    assert names == {"Alice", "Charlie"}


def test_filter_by_regex_case_sensitive_by_default():
    result = list(filter_by_regex(make_rows(), "city", r"amsterdam"))
    assert len(result) == 1
    assert result[0]["name"] == "Charlie"


def test_filter_by_regex_invert():
    result = list(filter_by_regex(make_rows(), "city", r"^Ber", invert=True))
    assert len(result) == 3
    assert all(r["city"] != "Berlin" for r in result)


def test_filter_by_regex_missing_column_treated_as_empty():
    rows = [{"name": "X"}, {"name": "Y", "city": "York"}]
    result = list(filter_by_regex(rows, "city", r"York"))
    assert len(result) == 1
    assert result[0]["name"] == "Y"


def test_filter_any_column_matches_any_field():
    result = list(filter_any_column(make_rows(), r"^9"))
    assert len(result) == 1
    assert result[0]["name"] == "Alice"


def test_filter_any_column_invert():
    result = list(filter_any_column(make_rows(), r"^9", invert=True))
    assert len(result) == 3


def test_filter_any_column_ignore_case():
    result = list(filter_any_column(make_rows(), r"alice", ignore_case=True))
    assert len(result) == 1
    assert result[0]["name"] == "Alice"


def test_filter_all_columns_requires_all_match():
    rows = [
        {"a": "foo", "b": "foobar"},
        {"a": "foo", "b": "baz"},
        {"a": "bar", "b": "baz"},
    ]
    result = list(filter_all_columns(rows, ["a", "b"], r"foo"))
    assert len(result) == 1
    assert result[0]["b"] == "foobar"


def test_filter_all_columns_empty_columns_list_yields_all():
    result = list(filter_all_columns(make_rows(), [], r"anything"))
    assert len(result) == len(make_rows())
