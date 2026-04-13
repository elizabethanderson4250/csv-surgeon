"""Tests for csv_surgeon.validate module."""

import pytest
from csv_surgeon.validate import (
    required,
    is_numeric,
    max_length,
    matches_pattern,
    validate_rows,
)


def make_row(**kwargs):
    return dict(kwargs)


# --- required ---

def test_required_passes_non_empty():
    v = required("name")
    assert v(make_row(name="Alice")) is None


def test_required_fails_empty_string():
    v = required("name")
    assert v(make_row(name="")) is not None


def test_required_fails_whitespace_only():
    v = required("name")
    assert v(make_row(name="   ")) is not None


def test_required_fails_missing_key():
    v = required("name")
    assert v({}) is not None


# --- is_numeric ---

def test_is_numeric_passes_integer_string():
    v = is_numeric("age")
    assert v(make_row(age="42")) is None


def test_is_numeric_passes_float_string():
    v = is_numeric("score")
    assert v(make_row(score="3.14")) is None


def test_is_numeric_fails_alpha():
    v = is_numeric("age")
    assert v(make_row(age="old")) is not None


def test_is_numeric_fails_empty():
    v = is_numeric("age")
    assert v(make_row(age="")) is not None


# --- max_length ---

def test_max_length_passes_within_limit():
    v = max_length("code", 5)
    assert v(make_row(code="ABC")) is None


def test_max_length_passes_exact_limit():
    v = max_length("code", 3)
    assert v(make_row(code="ABC")) is None


def test_max_length_fails_over_limit():
    v = max_length("code", 3)
    assert v(make_row(code="ABCD")) is not None


# --- matches_pattern ---

def test_matches_pattern_passes():
    v = matches_pattern("email", r".+@.+\..+")
    assert v(make_row(email="user@example.com")) is None


def test_matches_pattern_fails():
    v = matches_pattern("email", r".+@.+\..+")
    assert v(make_row(email="not-an-email")) is not None


# --- validate_rows ---

def test_validate_rows_yields_valid_only():
    rows = [
        {"name": "Alice", "age": "30"},
        {"name": "", "age": "25"},
        {"name": "Bob", "age": "abc"},
        {"name": "Carol", "age": "22"},
    ]
    validators = [required("name"), is_numeric("age")]
    result = list(validate_rows(rows, validators))
    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Carol"


def test_validate_rows_fail_fast_raises():
    rows = [
        {"name": "", "age": "30"},
    ]
    validators = [required("name")]
    with pytest.raises(ValueError, match="Validation failed"):
        list(validate_rows(rows, validators, fail_fast=True))


def test_validate_rows_no_validators_yields_all():
    rows = [{"x": "1"}, {"x": "2"}]
    result = list(validate_rows(rows, []))
    assert result == rows
