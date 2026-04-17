"""Tests for csv_surgeon.split_rows"""
import pytest
from csv_surgeon.split_rows import split_rows, explode_rows


def make_rows():
    return [
        {"id": "1", "tags": "a,b,c", "name": "Alice"},
        {"id": "2", "tags": "x", "name": "Bob"},
        {"id": "3", "tags": "", "name": "Carol"},
        {"id": "4", "tags": " d , e ", "name": "Dave"},
    ]


def test_split_rows_basic_count():
    result = list(split_rows(make_rows(), "tags"))
    # row1->3, row2->1, row3->0 (empty dropped), row4->2
    assert len(result) == 6


def test_split_rows_values_correct():
    result = list(split_rows([{"id": "1", "tags": "a,b,c"}], "tags"))
    assert [r["tags"] for r in result] == ["a", "b", "c"]


def test_split_rows_other_columns_preserved():
    result = list(split_rows([{"id": "1", "tags": "a,b"}], "tags"))
    assert all(r["id"] == "1" for r in result)


def test_split_rows_strips_whitespace():
    result = list(split_rows([{"id": "1", "tags": " a , b "}], "tags"))
    assert [r["tags"] for r in result] == ["a", "b"]


def test_split_rows_no_strip():
    result = list(split_rows([{"id": "1", "tags": " a , b "}], "tags", strip=False))
    assert result[0]["tags"] == " a "


def test_split_rows_keep_empty():
    result = list(split_rows([{"id": "1", "tags": ""}], "tags", keep_empty=True))
    assert len(result) == 1
    assert result[0]["tags"] == ""


def test_split_rows_missing_column_passthrough():
    rows = [{"id": "1", "other": "x"}]
    result = list(split_rows(rows, "tags"))
    assert result == rows


def test_split_rows_custom_separator():
    result = list(split_rows([{"id": "1", "tags": "a|b|c"}], "tags", separator="|"))
    assert len(result) == 3


def test_explode_rows_new_column_added():
    result = list(explode_rows([{"id": "1", "tags": "a,b"}], "tags", new_column="tag"))
    assert all("tag" in r for r in result)
    assert all("tags" in r for r in result)


def test_explode_rows_original_preserved():
    result = list(explode_rows([{"id": "1", "tags": "a,b"}], "tags", new_column="tag"))
    assert all(r["tags"] == "a,b" for r in result)


def test_explode_rows_new_column_values():
    result = list(explode_rows([{"id": "1", "tags": "x,y"}], "tags", new_column="tag"))
    assert [r["tag"] for r in result] == ["x", "y"]


def test_explode_rows_no_new_column_overwrites():
    result = list(explode_rows([{"id": "1", "tags": "p,q"}], "tags"))
    assert [r["tags"] for r in result] == ["p", "q"]
