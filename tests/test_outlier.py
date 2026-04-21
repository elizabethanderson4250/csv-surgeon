"""Tests for csv_surgeon.outlier."""
from __future__ import annotations

import pytest
from csv_surgeon.outlier import (
    _quartiles,
    _mean_stddev,
    flag_outliers_iqr,
    flag_outliers_zscore,
    remove_outliers_iqr,
)


def make_rows(values: list[str], col: str = "val") -> list[dict]:
    return [{col: v, "id": str(i)} for i, v in enumerate(values)]


# --- unit helpers ---

def test_mean_stddev_basic():
    mean, std = _mean_stddev([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert abs(mean - 5.0) < 1e-9
    assert abs(std - 2.0) < 1e-9


def test_mean_stddev_empty():
    assert _mean_stddev([]) == (0.0, 0.0)


def test_quartiles_even():
    q1, q3 = _quartiles([1.0, 2.0, 3.0, 4.0])
    assert q1 == 1.5
    assert q3 == 3.5


def test_quartiles_odd():
    q1, q3 = _quartiles([1.0, 2.0, 3.0, 4.0, 5.0])
    assert q1 == 1.5
    assert q3 == 4.5


# --- IQR flagging ---

def test_iqr_flags_extreme_high():
    rows = make_rows(["1", "2", "2", "3", "3", "3", "4", "100"])
    result = list(flag_outliers_iqr(rows, "val"))
    assert result[-1]["is_outlier"] == "1"


def test_iqr_flags_extreme_low():
    rows = make_rows(["-100", "2", "2", "3", "3", "3", "4", "4"])
    result = list(flag_outliers_iqr(rows, "val"))
    assert result[0]["is_outlier"] == "1"


def test_iqr_no_outlier_in_normal_data():
    rows = make_rows(["10", "11", "12", "13", "14", "15"])
    result = list(flag_outliers_iqr(rows, "val"))
    assert all(r["is_outlier"] == "0" for r in result)


def test_iqr_non_numeric_flagged_false():
    rows = make_rows(["1", "2", "abc", "3", "3", "3", "4", "4"])
    result = list(flag_outliers_iqr(rows, "val"))
    assert result[2]["is_outlier"] == "0"


def test_iqr_custom_output_column():
    rows = make_rows(["1", "2", "2", "3", "3", "100"])
    result = list(flag_outliers_iqr(rows, "val", output_column="outlier_flag"))
    assert "outlier_flag" in result[0]
    assert "is_outlier" not in result[0]


def test_iqr_too_few_rows_all_false():
    rows = make_rows(["1", "2", "3"])
    result = list(flag_outliers_iqr(rows, "val"))
    assert all(r["is_outlier"] == "0" for r in result)


# --- Z-score flagging ---

def test_zscore_flags_extreme_value():
    rows = make_rows(["10", "10", "10", "10", "10", "10", "10", "100"])
    result = list(flag_outliers_zscore(rows, "val", threshold=2.0))
    assert result[-1]["is_outlier"] == "1"


def test_zscore_normal_values_not_flagged():
    rows = make_rows(["10", "11", "12", "13", "14", "15"])
    result = list(flag_outliers_zscore(rows, "val", threshold=3.0))
    assert all(r["is_outlier"] == "0" for r in result)


def test_zscore_zero_stddev_all_false():
    rows = make_rows(["5", "5", "5", "5"])
    result = list(flag_outliers_zscore(rows, "val"))
    assert all(r["is_outlier"] == "0" for r in result)


def test_zscore_preserves_other_columns():
    rows = make_rows(["10", "10", "10", "100"])
    result = list(flag_outliers_zscore(rows, "val"))
    assert all("id" in r for r in result)


# --- remove outliers ---

def test_remove_outliers_filters_row():
    rows = make_rows(["1", "2", "2", "3", "3", "3", "4", "100"])
    result = list(remove_outliers_iqr(rows, "val"))
    values = [r["val"] for r in result]
    assert "100" not in values


def test_remove_outliers_keeps_normal_rows():
    rows = make_rows(["10", "11", "12", "13", "14", "15"])
    result = list(remove_outliers_iqr(rows, "val"))
    assert len(result) == 6


def test_remove_outliers_no_tmp_column():
    rows = make_rows(["1", "2", "2", "3", "3", "3", "4", "4"])
    result = list(remove_outliers_iqr(rows, "val"))
    assert all("__outlier_tmp" not in r for r in result)
