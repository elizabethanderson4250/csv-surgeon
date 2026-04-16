"""Tests for csv_surgeon.crossjoin."""
import pytest
from csv_surgeon.crossjoin import cross_join, semi_join


def left():
    return [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]


def right():
    return [{"color": "red"}, {"color": "blue"}]


def test_cross_join_row_count():
    result = list(cross_join(left(), right()))
    assert len(result) == 4


def test_cross_join_merges_columns():
    result = list(cross_join(left(), right()))
    assert "id" in result[0]
    assert "color" in result[0]


def test_cross_join_conflict_prefixed():
    l = [{"id": "1", "color": "green"}]
    r = [{"color": "red"}]
    result = list(cross_join(l, r))
    assert result[0]["color"] == "green"
    assert result[0]["right_color"] == "red"


def test_cross_join_empty_right():
    result = list(cross_join(left(), []))
    assert result == []


def test_cross_join_empty_left():
    result = list(cross_join([], right()))
    assert result == []


def test_semi_join_keeps_matching():
    l = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    r = [{"ref": "1"}, {"ref": "3"}]
    result = list(semi_join(l, r, "id", "ref"))
    assert len(result) == 2
    assert all(row["id"] in {"1", "3"} for row in result)


def test_semi_join_no_matches():
    l = [{"id": "9"}]
    r = [{"ref": "1"}]
    result = list(semi_join(l, r, "id", "ref"))
    assert result == []


def test_anti_join_excludes_matching():
    l = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    r = [{"ref": "1"}, {"ref": "3"}]
    result = list(semi_join(l, r, "id", "ref", negate=True))
    assert len(result) == 1
    assert result[0]["id"] == "2"


def test_semi_join_missing_left_key():
    l = [{"x": "1"}]
    r = [{"ref": "1"}]
    result = list(semi_join(l, r, "id", "ref"))
    assert result == []
