"""Tests for csv_surgeon.rolling_stats."""
from __future__ import annotations

import pytest

from csv_surgeon.rolling_stats import (
    cumulative_max,
    cumulative_mean,
    cumulative_min,
    cumulative_sum,
)


def make_rows(values: list[str]) -> list[dict]:
    return [{"val": v, "name": "x"} for v in values]


# ---------------------------------------------------------------------------
# cumulative_sum
# ---------------------------------------------------------------------------

def test_cumsum_basic_values():
    rows = make_rows(["1", "2", "3"])
    result = list(cumulative_sum(rows, "val"))
    assert [r["val_cumsum"] for r in result] == ["1.0", "3.0", "6.0"]


def test_cumsum_custom_output_column():
    rows = make_rows(["10", "20"])
    result = list(cumulative_sum(rows, "val", output_column="running_total"))
    assert "running_total" in result[0]
    assert result[-1]["running_total"] == "30.0"


def test_cumsum_non_numeric_uses_default():
    rows = make_rows(["1", "abc", "2"])
    result = list(cumulative_sum(rows, "val", default="N/A"))
    assert result[1]["val_cumsum"] == "N/A"
    assert result[2]["val_cumsum"] == "3.0"


def test_cumsum_preserves_other_columns():
    rows = make_rows(["5", "10"])
    result = list(cumulative_sum(rows, "val"))
    assert all(r["name"] == "x" for r in result)


def test_cumsum_empty_input():
    result = list(cumulative_sum([], "val"))
    assert result == []


# ---------------------------------------------------------------------------
# cumulative_mean
# ---------------------------------------------------------------------------

def test_cummean_basic_values():
    rows = make_rows(["2", "4", "6"])
    result = list(cumulative_mean(rows, "val"))
    means = [float(r["val_cummean"]) for r in result]
    assert means == pytest.approx([2.0, 3.0, 4.0])


def test_cummean_single_row():
    rows = make_rows(["7"])
    result = list(cumulative_mean(rows, "val"))
    assert float(result[0]["val_cummean"]) == pytest.approx(7.0)


def test_cummean_non_numeric_skipped_in_average():
    rows = make_rows(["4", "bad", "8"])
    result = list(cumulative_mean(rows, "val"))
    # row 0: mean of [4] = 4.0
    # row 1: non-numeric -> default
    # row 2: mean of [4, 8] = 6.0
    assert float(result[0]["val_cummean"]) == pytest.approx(4.0)
    assert result[1]["val_cummean"] == ""
    assert float(result[2]["val_cummean"]) == pytest.approx(6.0)


# ---------------------------------------------------------------------------
# cumulative_max
# ---------------------------------------------------------------------------

def test_cummax_increasing_sequence():
    rows = make_rows(["1", "3", "2", "5"])
    result = list(cumulative_max(rows, "val"))
    maxes = [float(r["val_cummax"]) for r in result]
    assert maxes == pytest.approx([1.0, 3.0, 3.0, 5.0])


def test_cummax_all_same():
    rows = make_rows(["4", "4", "4"])
    result = list(cumulative_max(rows, "val"))
    assert all(float(r["val_cummax"]) == pytest.approx(4.0) for r in result)


# ---------------------------------------------------------------------------
# cumulative_min
# ---------------------------------------------------------------------------

def test_cummin_decreasing_sequence():
    rows = make_rows(["10", "7", "9", "3"])
    result = list(cumulative_min(rows, "val"))
    mins = [float(r["val_cummin"]) for r in result]
    assert mins == pytest.approx([10.0, 7.0, 7.0, 3.0])


def test_cummin_non_numeric_uses_default():
    rows = make_rows(["5", "x", "2"])
    result = list(cumulative_min(rows, "val", default="-"))
    assert result[1]["val_cummin"] == "-"
    assert float(result[2]["val_cummin"]) == pytest.approx(2.0)
