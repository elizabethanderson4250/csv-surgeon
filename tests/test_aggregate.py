"""Tests for csv_surgeon.aggregate."""

import pytest
from csv_surgeon.aggregate import aggregate, group_by


def make_rows():
    return [
        {"dept": "eng", "name": "alice", "salary": "90000"},
        {"dept": "eng", "name": "bob",   "salary": "80000"},
        {"dept": "hr",  "name": "carol", "salary": "70000"},
        {"dept": "hr",  "name": "dave",  "salary": "75000"},
        {"dept": "eng", "name": "eve",   "salary": ""},
    ]


# --- group_by ---

def test_group_by_single_column():
    rows = make_rows()
    groups = group_by(rows, ["dept"])
    assert set(groups.keys()) == {("eng",), ("hr",)}
    assert len(groups[("eng",)]) == 3
    assert len(groups[("hr",)]) == 2


def test_group_by_multiple_columns():
    rows = [
        {"a": "x", "b": "1"},
        {"a": "x", "b": "2"},
        {"a": "y", "b": "1"},
    ]
    groups = group_by(rows, ["a", "b"])
    assert len(groups) == 3


# --- aggregate: sum ---

def test_aggregate_sum():
    result = aggregate(make_rows(), ["dept"], "salary", func="sum")
    by_dept = {r["dept"]: float(r["salary_sum"]) for r in result}
    assert by_dept["eng"] == pytest.approx(170000.0)
    assert by_dept["hr"] == pytest.approx(145000.0)


def test_aggregate_count():
    result = aggregate(make_rows(), ["dept"], "salary", func="count")
    by_dept = {r["dept"]: int(r["salary_count"]) for r in result}
    assert by_dept["eng"] == 3
    assert by_dept["hr"] == 2


def test_aggregate_mean():
    result = aggregate(make_rows(), ["dept"], "salary", func="mean")
    by_dept = {r["dept"]: float(r["salary_mean"]) for r in result}
    # eng: only 90000 and 80000 are numeric
    assert by_dept["eng"] == pytest.approx(85000.0)
    assert by_dept["hr"] == pytest.approx(72500.0)


def test_aggregate_min():
    result = aggregate(make_rows(), ["dept"], "salary", func="min")
    by_dept = {r["dept"]: float(r["salary_min"]) for r in result}
    assert by_dept["eng"] == pytest.approx(80000.0)
    assert by_dept["hr"] == pytest.approx(70000.0)


def test_aggregate_max():
    result = aggregate(make_rows(), ["dept"], "salary", func="max")
    by_dept = {r["dept"]: float(r["salary_max"]) for r in result}
    assert by_dept["eng"] == pytest.approx(90000.0)
    assert by_dept["hr"] == pytest.approx(75000.0)


def test_aggregate_custom_output_column():
    result = aggregate(make_rows(), ["dept"], "salary", func="sum", output_column="total")
    assert "total" in result[0]
    assert "salary_sum" not in result[0]


def test_aggregate_invalid_func():
    with pytest.raises(ValueError, match="Unsupported"):
        aggregate(make_rows(), ["dept"], "salary", func="median")


def test_aggregate_all_non_numeric_returns_empty_string():
    rows = [{"dept": "eng", "score": "n/a"}, {"dept": "eng", "score": ""}]
    result = aggregate(rows, ["dept"], "score", func="sum")
    assert result[0]["score_sum"] == ""


def test_aggregate_empty_input():
    result = aggregate([], ["dept"], "salary", func="sum")
    assert result == []
