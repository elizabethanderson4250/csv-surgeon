"""Tests for csv_surgeon.join module."""

import pytest
from csv_surgeon.join import inner_join, left_join


LEFT_ROWS = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Carol"},
]

RIGHT_ROWS = [
    {"user_id": "1", "city": "London"},
    {"user_id": "2", "city": "Paris"},
    {"user_id": "4", "city": "Berlin"},
]


def test_inner_join_returns_only_matching_rows():
    result = list(inner_join(LEFT_ROWS, RIGHT_ROWS, left_on="id", right_on="user_id"))
    assert len(result) == 2
    ids = {r["id"] for r in result}
    assert ids == {"1", "2"}


def test_inner_join_merges_columns():
    result = list(inner_join(LEFT_ROWS, RIGHT_ROWS, left_on="id", right_on="user_id"))
    alice = next(r for r in result if r["id"] == "1")
    assert alice["city"] == "London"
    assert alice["name"] == "Alice"


def test_inner_join_right_key_excluded():
    result = list(inner_join(LEFT_ROWS, RIGHT_ROWS, left_on="id", right_on="user_id"))
    for row in result:
        assert "user_id" not in row


def test_inner_join_empty_right():
    result = list(inner_join(LEFT_ROWS, [], left_on="id", right_on="user_id"))
    assert result == []


def test_inner_join_empty_left():
    result = list(inner_join([], RIGHT_ROWS, left_on="id", right_on="user_id"))
    assert result == []


def test_left_join_returns_all_left_rows():
    result = list(left_join(LEFT_ROWS, RIGHT_ROWS, left_on="id", right_on="user_id"))
    assert len(result) == 3


def test_left_join_fills_missing_with_empty_string():
    result = list(left_join(LEFT_ROWS, RIGHT_ROWS, left_on="id", right_on="user_id"))
    carol = next(r for r in result if r["id"] == "3")
    assert carol["city"] == ""


def test_left_join_custom_fill_value():
    result = list(
        left_join(LEFT_ROWS, RIGHT_ROWS, left_on="id", right_on="user_id", fill_value="N/A")
    )
    carol = next(r for r in result if r["id"] == "3")
    assert carol["city"] == "N/A"


def test_left_join_matched_rows_have_data():
    result = list(left_join(LEFT_ROWS, RIGHT_ROWS, left_on="id", right_on="user_id"))
    bob = next(r for r in result if r["id"] == "2")
    assert bob["city"] == "Paris"


def test_right_prefix_applied_on_column_name_clash():
    left = [{"id": "1", "city": "Madrid"}]
    right = [{"user_id": "1", "city": "London"}]
    result = list(inner_join(left, right, left_on="id", right_on="user_id", right_prefix="r_"))
    assert result[0]["city"] == "Madrid"
    assert result[0]["r_city"] == "London"
