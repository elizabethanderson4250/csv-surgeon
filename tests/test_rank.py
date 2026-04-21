"""Tests for csv_surgeon/rank.py"""
import pytest
from csv_surgeon.rank import rank_rows, row_number


def make_rows(data):
    return [dict(zip(["name", "score", "group"], row)) for row in data]


# ---------------------------------------------------------------------------
# rank_rows — dense
# ---------------------------------------------------------------------------

def test_dense_rank_ascending():
    rows = make_rows([("a", "10", "x"), ("b", "20", "x"), ("c", "10", "x")])
    result = rank_rows(rows, sort_column="score", numeric=True)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["a"] == ranks["c"] == "1"
    assert ranks["b"] == "2"


def test_dense_rank_descending():
    rows = make_rows([("a", "10", "x"), ("b", "20", "x"), ("c", "30", "x")])
    result = rank_rows(rows, sort_column="score", numeric=True, ascending=False)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["c"] == "1"
    assert ranks["b"] == "2"
    assert ranks["a"] == "3"


def test_standard_rank_ties_get_lower_rank():
    rows = make_rows([("a", "10", "x"), ("b", "10", "x"), ("c", "20", "x")])
    result = rank_rows(rows, sort_column="score", numeric=True, method="standard")
    ranks = {r["name"]: r["rank"] for r in result}
    # both tied at position 1 or 2; c is 3
    assert ranks["a"] in ("1", "2")
    assert ranks["b"] in ("1", "2")
    assert ranks["c"] == "3"


def test_percent_rank_two_rows():
    rows = make_rows([("a", "10", "x"), ("b", "20", "x")])
    result = rank_rows(rows, sort_column="score", numeric=True, method="percent")
    ranks = {r["name"]: float(r["rank"]) for r in result}
    assert ranks["a"] == 0.0
    assert ranks["b"] == 1.0


def test_percent_rank_single_row():
    rows = make_rows([("a", "10", "x")])
    result = rank_rows(rows, sort_column="score", numeric=True, method="percent")
    assert result[0]["rank"] == "0.0"


def test_rank_preserves_original_order():
    rows = make_rows([("a", "30", "x"), ("b", "10", "x"), ("c", "20", "x")])
    result = rank_rows(rows, sort_column="score", numeric=True)
    names = [r["name"] for r in result]
    assert names == ["a", "b", "c"]


def test_rank_with_group_by_resets_per_group():
    rows = [
        {"name": "a", "score": "10", "group": "g1"},
        {"name": "b", "score": "20", "group": "g1"},
        {"name": "c", "score": "5", "group": "g2"},
        {"name": "d", "score": "15", "group": "g2"},
    ]
    result = rank_rows(rows, sort_column="score", numeric=True, group_by="group")
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["a"] == "1"
    assert ranks["b"] == "2"
    assert ranks["c"] == "1"
    assert ranks["d"] == "2"


def test_rank_empty_input():
    assert rank_rows([], sort_column="score") == []


def test_rank_invalid_method():
    rows = make_rows([("a", "10", "x")])
    with pytest.raises(ValueError, match="Unknown rank method"):
        rank_rows(rows, sort_column="score", method="bad")


def test_rank_custom_output_column():
    rows = make_rows([("a", "10", "x")])
    result = rank_rows(rows, sort_column="score", output_column="my_rank")
    assert "my_rank" in result[0]
    assert "rank" not in result[0]


def test_rank_non_numeric_string_sort():
    rows = [{"name": "banana"}, {"name": "apple"}, {"name": "cherry"}]
    result = rank_rows(rows, sort_column="name", numeric=False)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["apple"] == "1"
    assert ranks["banana"] == "2"
    assert ranks["cherry"] == "3"


# ---------------------------------------------------------------------------
# row_number
# ---------------------------------------------------------------------------

def test_row_number_sequential():
    rows = [{"x": str(i)} for i in range(5)]
    result = list(row_number(rows))
    nums = [r["row_number"] for r in result]
    assert nums == ["1", "2", "3", "4", "5"]


def test_row_number_custom_start():
    rows = [{"x": "a"}, {"x": "b"}]
    result = list(row_number(rows, start=10))
    assert result[0]["row_number"] == "10"
    assert result[1]["row_number"] == "11"


def test_row_number_group_resets():
    rows = [
        {"g": "a", "v": "1"}, {"g": "a", "v": "2"},
        {"g": "b", "v": "3"}, {"g": "b", "v": "4"},
    ]
    result = list(row_number(rows, group_by="g"))
    nums = [r["row_number"] for r in result]
    assert nums == ["1", "2", "1", "2"]


def test_row_number_custom_column():
    rows = [{"x": "a"}]
    result = list(row_number(rows, output_column="#"))
    assert "#" in result[0]
