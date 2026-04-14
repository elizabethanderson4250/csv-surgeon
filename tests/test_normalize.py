"""Tests for csv_surgeon/normalize.py"""

import pytest
from csv_surgeon.normalize import (
    to_slug,
    pad_left,
    pad_right,
    truncate,
    normalize_whitespace,
    remove_non_alphanumeric,
)


def make_row(**kwargs):
    return dict(kwargs)


# --- to_slug ---

def test_to_slug_basic():
    transform = to_slug("title")
    row = transform(make_row(title="Hello World"))
    assert row["title"] == "hello-world"


def test_to_slug_special_chars():
    transform = to_slug("title")
    row = transform(make_row(title="Héllo & Wörld!"))
    assert row["title"] == "hllo-wrld"


def test_to_slug_custom_separator():
    transform = to_slug("title", separator="_")
    row = transform(make_row(title="foo bar baz"))
    assert row["title"] == "foo_bar_baz"


def test_to_slug_missing_column_unchanged():
    transform = to_slug("title")
    row = transform(make_row(name="unchanged"))
    assert row == {"name": "unchanged"}


# --- pad_left ---

def test_pad_left_zero_pads():
    transform = pad_left("code", width=5)
    row = transform(make_row(code="42"))
    assert row["code"] == "00042"


def test_pad_left_already_wide_enough():
    transform = pad_left("code", width=3)
    row = transform(make_row(code="12345"))
    assert row["code"] == "12345"


def test_pad_left_custom_fillchar():
    transform = pad_left("code", width=6, fillchar="*")
    row = transform(make_row(code="hi"))
    assert row["code"] == "****hi"


# --- pad_right ---

def test_pad_right_spaces():
    transform = pad_right("label", width=8)
    row = transform(make_row(label="ok"))
    assert row["label"] == "ok      "


# --- truncate ---

def test_truncate_shortens_value():
    transform = truncate("bio", max_length=10)
    row = transform(make_row(bio="This is a long biography"))
    assert row["bio"] == "This is a "


def test_truncate_with_ellipsis():
    transform = truncate("bio", max_length=10, ellipsis=True)
    row = transform(make_row(bio="This is a long biography"))
    assert row["bio"] == "This is..."
    assert len(row["bio"]) == 10


def test_truncate_short_value_unchanged():
    transform = truncate("bio", max_length=50)
    row = transform(make_row(bio="short"))
    assert row["bio"] == "short"


# --- normalize_whitespace ---

def test_normalize_whitespace_collapses_spaces():
    transform = normalize_whitespace("text")
    row = transform(make_row(text="  hello   world  "))
    assert row["text"] == "hello world"


def test_normalize_whitespace_tabs_and_newlines():
    transform = normalize_whitespace("text")
    row = transform(make_row(text="foo\t\tbar\nbaz"))
    assert row["text"] == "foo bar baz"


# --- remove_non_alphanumeric ---

def test_remove_non_alphanumeric_strips_punctuation():
    transform = remove_non_alphanumeric("val")
    row = transform(make_row(val="hello, world!"))
    assert row["val"] == "helloworld"


def test_remove_non_alphanumeric_keep_spaces():
    transform = remove_non_alphanumeric("val", keep_spaces=True)
    row = transform(make_row(val="hello, world!"))
    assert row["val"] == "hello world"
