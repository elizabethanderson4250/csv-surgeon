"""Tests for csv_surgeon/truncate.py"""

import pytest
from csv_surgeon.truncate import (
    truncate_left,
    truncate_right,
    pad_left,
    pad_right,
    apply,
)


def make_row(value: str) -> dict:
    return {"name": value, "other": "unchanged"}


# --- truncate_right ---

def test_truncate_right_shortens_long_value():
    t = truncate_right("name", 5)
    assert t(make_row("HelloWorld"))["name"] == "Hello"


def test_truncate_right_leaves_short_value_unchanged():
    t = truncate_right("name", 10)
    assert t(make_row("Hi"))["name"] == "Hi"


def test_truncate_right_with_ellipsis():
    t = truncate_right("name", 8, ellipsis=True)
    assert t(make_row("HelloWorld"))["name"] == "Hello..."


def test_truncate_right_ellipsis_short_value_unchanged():
    t = truncate_right("name", 8, ellipsis=True)
    assert t(make_row("Hi"))["name"] == "Hi"


def test_truncate_right_zero_max_len():
    t = truncate_right("name", 0)
    assert t(make_row("Hello"))["name"] == ""


def test_truncate_right_invalid_max_len():
    with pytest.raises(ValueError):
        truncate_right("name", -1)


def test_truncate_right_exact_length_unchanged():
    t = truncate_right("name", 5)
    assert t(make_row("Hello"))["name"] == "Hello"


# --- truncate_left ---

def test_truncate_left_shortens_long_value():
    t = truncate_left("name", 5)
    assert t(make_row("HelloWorld"))["name"] == "World"


def test_truncate_left_leaves_short_value_unchanged():
    t = truncate_left("name", 10)
    assert t(make_row("Hi"))["name"] == "Hi"


def test_truncate_left_with_ellipsis():
    t = truncate_left("name", 8, ellipsis=True)
    assert t(make_row("HelloWorld"))["name"] == "...World"


def test_truncate_left_invalid_max_len():
    with pytest.raises(ValueError):
        truncate_left("name", -3)


def test_truncate_left_exact_length_unchanged():
    t = truncate_left("name", 5)
    assert t(make_row("Hello"))["name"] == "Hello"


# --- pad_right ---

def test_pad_right_pads_short_value():
    t = pad_right("name", 8)
    assert t(make_row("Hi"))["name"] == "Hi      "


def test_pad_right_does_not_truncate_long_value():
    t = pad_right("name", 3)
    assert t(make_row("Hello"))["name"] == "Hello"


def test_pad_right_custom_char():
    t = pad_right("name", 5, char="-")
    assert t(make_row("Hi"))["name"] == "Hi---"


def test_pad_right_invalid_char():
    with pytest.raises(ValueError):
        pad_right("name", 5, char="--")


def test_pad_right_exact_length_unchanged():
    t = pad_right("name", 5)
    assert t(make_row("Hello"))["name"] == "Hello"


# --- pad_left ---

def test_pad_left_pads_short_value():
    t = pad_left("name", 6, char="0")
    assert t(make_row("42"))["name"] == "000042"


def test_pad_left_does_not_truncate_long_value():
    t = pad_left("name", 3)
    assert t(make_row("Hello"))["name"] == "Hello"


# --- missing column ---

def test_transform_missing_column_unchanged():
    t = truncate_right("missing", 3)
    row = {"name": "Hello"}
    assert t(row) == {"name": "Hello"}


def test_other_columns_not_affected():
    t = truncate_right("name", 3)
    result = t(make_row("Hello"))
    assert result["other"] == "unchanged"


# --- apply ---

def test_apply_multiple_transforms():
    rows = [
        {"code": "ABC", "label": "HelloWorld"},
        {"code": "XY", "label": "Short"},
    ]
    transforms = [
        truncate_right("label", 5)
