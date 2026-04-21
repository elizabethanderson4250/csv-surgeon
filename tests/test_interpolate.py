"""Tests for csv_surgeon.interpolate."""
from __future__ import annotations

import pytest
from csv_surgeon.interpolate import backward_fill, forward_fill, linear_interpolate


def make_rows(values):
    return [{"x": str(v) if v is not None else "", "tag": "t"} for v in values]


# ---------------------------------------------------------------------------
# linear_interpolate
# ---------------------------------------------------------------------------

def test_linear_fills_single_gap():
    rows = make_rows([1, None, 3])
    result = list(linear_interpolate(rows, "x"))
    assert result[1]["x"] == "2.0"


def test_linear_fills_multiple_gaps():
    rows = make_rows([0, None, None, None, 4])
    result = list(linear_interpolate(rows, "x"))
    assert result[1]["x"] == "1.0"
    assert result[2]["x"] == "2.0"
    assert result[3]["x"] == "3.0"


def test_linear_leading_gap_empty_by_default():
    rows = make_rows([None, None, 4])
    result = list(linear_interpolate(rows, "x"))
    assert result[0]["x"] == ""
    assert result[1]["x"] == ""


def test_linear_leading_gap_filled_when_flag_set():
    rows = make_rows([None, None, 4])
    result = list(linear_interpolate(rows, "x", fill_leading=True))
    assert result[0]["x"] == "4.0"
    assert result[1]["x"] == "4.0"


def test_linear_trailing_gap_empty_by_default():
    rows = make_rows([1, None, None])
    result = list(linear_interpolate(rows, "x"))
    assert result[1]["x"] == ""
    assert result[2]["x"] == ""


def test_linear_trailing_gap_filled_when_flag_set():
    rows = make_rows([1, None, None])
    result = list(linear_interpolate(rows, "x", fill_trailing=True))
    assert result[1]["x"] == "1.0"
    assert result[2]["x"] == "1.0"


def test_linear_output_column_does_not_overwrite_source():
    rows = make_rows([1, None, 3])
    result = list(linear_interpolate(rows, "x", output_column="x_filled"))
    assert result[1]["x"] == ""
    assert result[1]["x_filled"] == "2.0"


def test_linear_preserves_other_columns():
    rows = make_rows([1, None, 3])
    result = list(linear_interpolate(rows, "x"))
    assert all(r["tag"] == "t" for r in result)


def test_linear_no_gaps_unchanged():
    rows = make_rows([1, 2, 3])
    result = list(linear_interpolate(rows, "x"))
    assert [r["x"] for r in result] == ["1", "2", "3"]


# ---------------------------------------------------------------------------
# forward_fill
# ---------------------------------------------------------------------------

def test_forward_fill_basic():
    rows = make_rows([1, None, None, 4])
    result = list(forward_fill(rows, "x"))
    assert result[1]["x"] == "1"
    assert result[2]["x"] == "1"
    assert result[3]["x"] == "4"


def test_forward_fill_leading_gap_stays_empty():
    rows = make_rows([None, None, 3])
    result = list(forward_fill(rows, "x"))
    assert result[0]["x"] == ""
    assert result[1]["x"] == ""


def test_forward_fill_output_column():
    rows = make_rows([1, None, 3])
    result = list(forward_fill(rows, "x", output_column="x_ff"))
    assert result[1]["x"] == ""
    assert result[1]["x_ff"] == "1"


# ---------------------------------------------------------------------------
# backward_fill
# ---------------------------------------------------------------------------

def test_backward_fill_basic():
    rows = make_rows([None, None, 3, None])
    result = list(backward_fill(rows, "x"))
    assert result[0]["x"] == "3"
    assert result[1]["x"] == "3"
    assert result[3]["x"] == ""


def test_backward_fill_output_column():
    rows = make_rows([None, 2, 3])
    result = list(backward_fill(rows, "x", output_column="x_bk"))
    assert result[0]["x"] == ""
    assert result[0]["x_bk"] == "2"
