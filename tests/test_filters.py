"""Tests for csv_surgeon.filters module."""

import pytest
from csv_surgeon.filters import (
    equals,
    not_equals,
    contains,
    matches,
    greater_than,
    less_than,
    combine_and,
    combine_or,
    apply_filters,
)


SAMPLE_ROWS = [
    {"name": "Alice", "age": "30", "city": "New York"},
    {"name": "Bob", "age": "25", "city": "Los Angeles"},
    {"name": "Charlie", "age": "35", "city": "New York"},
    {"name": "Diana", "age": "28", "city": "Chicago"},
    {"name": "Eve", "age": "22", "city": "Los Angeles"},
]


def test_equals_filter():
    f = equals("city", "New York")
    result = [r for r in SAMPLE_ROWS if f(r)]
    assert len(result) == 2
    assert all(r["city"] == "New York" for r in result)


def test_not_equals_filter():
    f = not_equals("city", "New York")
    result = [r for r in SAMPLE_ROWS if f(r)]
    assert len(result) == 3
    assert all(r["city"] != "New York" for r in result)


def test_contains_filter():
    f = contains("name", "li")
    result = [r for r in SAMPLE_ROWS if f(r)]
    names = [r["name"] for r in result]
    assert "Alice" in names
    assert "Charlie" in names


def test_matches_filter():
    f = matches("name", r"^[AB]")
    result = [r for r in SAMPLE_ROWS if f(r)]
    names = [r["name"] for r in result]
    assert "Alice" in names
    assert "Bob" in names
    assert len(result) == 2


def test_greater_than_filter():
    f = greater_than("age", 28)
    result = [r for r in SAMPLE_ROWS if f(r)]
    assert all(float(r["age"]) > 28 for r in result)
    assert len(result) == 2


def test_less_than_filter():
    f = less_than("age", 28)
    result = [r for r in SAMPLE_ROWS if f(r)]
    assert all(float(r["age"]) < 28 for r in result)
    assert len(result) == 2


def test_greater_than_non_numeric_returns_false():
    f = greater_than("name", 10)
    assert f({"name": "Alice"}) is False


def test_combine_and():
    f = combine_and(equals("city", "New York"), greater_than("age", 30))
    result = [r for r in SAMPLE_ROWS if f(r)]
    assert len(result) == 1
    assert result[0]["name"] == "Charlie"


def test_combine_or():
    f = combine_or(equals("city", "Chicago"), less_than("age", 23))
    result = [r for r in SAMPLE_ROWS if f(r)]
    names = [r["name"] for r in result]
    assert "Diana" in names
    assert "Eve" in names


def test_apply_filters_generator():
    result = list(apply_filters(iter(SAMPLE_ROWS), equals("city", "Los Angeles")))
    assert len(result) == 2
    assert all(r["city"] == "Los Angeles" for r in result)


def test_apply_filters_multiple():
    result = list(
        apply_filters(
            iter(SAMPLE_ROWS),
            equals("city", "Los Angeles"),
            less_than("age", 24),
        )
    )
    assert len(result) == 1
    assert result[0]["name"] == "Eve"
