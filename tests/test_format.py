"""Tests for csv_surgeon/format.py"""
import pytest
from csv_surgeon.format import (
    zero_pad, title_case, wrap, number_format, strip_chars, remove_non_alphanumeric
)


def make_row(**kwargs):
    return dict(kwargs)


def test_zero_pad_pads_short_value():
    t = zero_pad("id", 5)
    assert t(make_row(id="42"))["id"] == "00042"


def test_zero_pad_leaves_long_value_unchanged():
    t = zero_pad("id", 3)
    assert t(make_row(id="12345"))["id"] == "12345"


def test_zero_pad_missing_column_unchanged():
    t = zero_pad("id", 5)
    row = make_row(name="Alice")
    assert t(row) == row


def test_title_case_converts_value():
    t = title_case("name")
    assert t(make_row(name="hello world"))["name"] == "Hello World"


def test_title_case_missing_column_unchanged():
    t = title_case("name")
    row = make_row(city="london")
    assert t(row) == row


def test_wrap_adds_prefix_and_suffix():
    t = wrap("code", prefix="[", suffix="]")
    assert t(make_row(code="ABC"))["code"] == "[ABC]"


def test_wrap_prefix_only():
    t = wrap("code", prefix=">>")
    assert t(make_row(code="X"))["code"] == ">>X"


def test_wrap_missing_column_unchanged():
    t = wrap("code", prefix="[", suffix="]")
    row = make_row(name="test")
    assert t(row) == row


def test_number_format_two_decimals():
    t = number_format("price", decimals=2)
    assert t(make_row(price="3.14159"))["price"] == "3.14"


def test_number_format_zero_decimals():
    t = number_format("price", decimals=0)
    assert t(make_row(price="9.99"))["price"] == "10"


def test_number_format_thousands_sep():
    t = number_format("amount", decimals=2, thousands_sep=True)
    assert t(make_row(amount="1234567.8"))["amount"] == "1,234,567.80"


def test_number_format_invalid_value_unchanged():
    t = number_format("price", decimals=2)
    assert t(make_row(price="N/A"))["price"] == "N/A"


def test_strip_chars_removes_whitespace():
    t = strip_chars("name")
    assert t(make_row(name="  Alice  "))["name"] == "Alice"


def test_strip_chars_custom_chars():
    t = strip_chars("val", chars="*")
    assert t(make_row(val="***hello***"))["val"] == "hello"


def test_remove_non_alphanumeric_basic():
    t = remove_non_alphanumeric("val")
    assert t(make_row(val="hello, world!"))["val"] == "helloworld"


def test_remove_non_alphanumeric_keep_spaces():
    t = remove_non_alphanumeric("val", keep_spaces=True)
    assert t(make_row(val="hello, world!"))["val"] == "hello world"


def test_does_not_mutate_original_row():
    t = title_case("name")
    row = make_row(name="alice")
    result = t(row)
    assert row["name"] == "alice"
    assert result["name"] == "Alice"
