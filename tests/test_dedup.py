"""Tests for csv_surgeon.dedup module."""
import pytest
from csv_surgeon.dedup import dedup_by_columns, dedup_by_key_func


def make_rows():
    return [
        {"id": "1", "name": "Alice", "dept": "Eng"},
        {"id": "2", "name": "Bob",   "dept": "HR"},
        {"id": "1", "name": "Alice", "dept": "Eng"},  # duplicate of row 0
        {"id": "3", "name": "Carol", "dept": "Eng"},
        {"id": "2", "name": "Bob",   "dept": "HR"},   # duplicate of row 1
        {"id": "4", "name": "Dave",  "dept": "Eng"},
    ]


def test_dedup_by_columns_keep_first():
    rows = list(dedup_by_columns(make_rows(), columns=["id"]))
    assert len(rows) == 4
    assert [r["id"] for r in rows] == ["1", "2", "3", "4"]


def test_dedup_by_columns_keep_last():
    rows = list(dedup_by_columns(make_rows(), columns=["id"], keep="last"))
    assert len(rows) == 4
    # order of first occurrence is preserved; value comes from last seen
    assert rows[0]["id"] == "1"
    assert rows[1]["id"] == "2"


def test_dedup_by_multiple_columns():
    rows = list(dedup_by_columns(make_rows(), columns=["name", "dept"]))
    assert len(rows) == 4


def test_dedup_no_duplicates_unchanged():
    data = [
        {"id": "1", "val": "a"},
        {"id": "2", "val": "b"},
        {"id": "3", "val": "c"},
    ]
    result = list(dedup_by_columns(data, columns=["id"]))
    assert result == data


def test_dedup_all_duplicates_keeps_one():
    data = [{"id": "1", "val": str(i)} for i in range(5)]
    result = list(dedup_by_columns(data, columns=["id"]))
    assert len(result) == 1
    assert result[0]["val"] == "0"  # first


def test_dedup_all_duplicates_keep_last():
    data = [{"id": "1", "val": str(i)} for i in range(5)]
    result = list(dedup_by_columns(data, columns=["id"], keep="last"))
    assert len(result) == 1
    assert result[0]["val"] == "4"  # last


def test_dedup_invalid_keep_raises():
    with pytest.raises(ValueError, match="keep must be"):
        list(dedup_by_columns(make_rows(), columns=["id"], keep="middle"))


def test_dedup_by_key_func_keep_first():
    rows = list(
        dedup_by_key_func(make_rows(), key_func=lambda r: r["dept"])
    )
    assert len(rows) == 2  # 'Eng' and 'HR'
    depts = [r["dept"] for r in rows]
    assert "Eng" in depts and "HR" in depts


def test_dedup_by_key_func_keep_last():
    rows = list(
        dedup_by_key_func(make_rows(), key_func=lambda r: r["dept"], keep="last")
    )
    assert len(rows) == 2
    eng_row = next(r for r in rows if r["dept"] == "Eng")
    assert eng_row["name"] == "Dave"  # last Eng row


def test_dedup_by_key_func_invalid_keep_raises():
    with pytest.raises(ValueError):
        list(dedup_by_key_func(make_rows(), key_func=lambda r: r["id"], keep="none"))


def test_dedup_empty_input():
    assert list(dedup_by_columns([], columns=["id"])) == []
    assert list(dedup_by_key_func([], key_func=lambda r: r["id"])) == []
