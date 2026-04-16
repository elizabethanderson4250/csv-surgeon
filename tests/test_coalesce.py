import pytest
from csv_surgeon.coalesce import coalesce, first_valid, _is_empty


def make_rows(*dicts):
    return list(dicts)


def test_is_empty_empty_string():
    assert _is_empty("") is True


def test_is_empty_whitespace():
    assert _is_empty("   ") is True


def test_is_empty_none():
    assert _is_empty(None) is True


def test_is_empty_valid_value():
    assert _is_empty("hello") is False


def test_coalesce_picks_first_non_empty():
    rows = make_rows({"a": "", "b": "hello", "c": "world"})
    result = list(coalesce(rows, ["a", "b", "c"], "out"))
    assert result[0]["out"] == "hello"


def test_coalesce_picks_first_column_when_all_filled():
    rows = make_rows({"a": "first", "b": "second"})
    result = list(coalesce(rows, ["a", "b"], "out"))
    assert result[0]["out"] == "first"


def test_coalesce_uses_default_when_all_empty():
    rows = make_rows({"a": "", "b": "  "})
    result = list(coalesce(rows, ["a", "b"], "out", default="N/A"))
    assert result[0]["out"] == "N/A"


def test_coalesce_default_is_empty_string():
    rows = make_rows({"a": ""})
    result = list(coalesce(rows, ["a"], "out"))
    assert result[0]["out"] == ""


def test_coalesce_does_not_mutate_original():
    row = {"a": "", "b": "val"}
    list(coalesce([row], ["a", "b"], "out"))
    assert "out" not in row


def test_coalesce_preserves_other_columns():
    rows = make_rows({"a": "", "b": "x", "extra": "keep"})
    result = list(coalesce(rows, ["a", "b"], "out"))
    assert result[0]["extra"] == "keep"


def test_coalesce_target_can_overwrite_existing_column():
    rows = make_rows({"a": "new", "b": "old"})
    result = list(coalesce(rows, ["a"], "b"))
    assert result[0]["b"] == "new"


def test_coalesce_multiple_rows():
    rows = [
        {"a": "", "b": "one"},
        {"a": "two", "b": "three"},
        {"a": "", "b": ""},
    ]
    result = list(coalesce(rows, ["a", "b"], "out", default="none"))
    assert result[0]["out"] == "one"
    assert result[1]["out"] == "two"
    assert result[2]["out"] == "none"


def test_first_valid_returns_first_non_empty():
    row = {"x": "", "y": "yes", "z": "no"}
    assert first_valid(row, ["x", "y", "z"]) == "yes"


def test_first_valid_missing_key_treated_as_empty():
    row = {"y": "found"}
    assert first_valid(row, ["x", "y"]) == "found"


def test_first_valid_all_empty_returns_default():
    row = {"a": "", "b": ""}
    assert first_valid(row, ["a", "b"], default="fallback") == "fallback"
