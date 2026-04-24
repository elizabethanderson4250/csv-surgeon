"""Tests for csv_surgeon.zscore."""
from __future__ import annotations

import math
import pytest

from csv_surgeon.zscore import zscore_column, minmax_scale_column


def make_rows(values: list[str]) -> list[dict]:
    return [{"id": str(i), "val": v} for i, v in enumerate(values)]


# ---------------------------------------------------------------------------
# zscore_column
# ---------------------------------------------------------------------------

def test_zscore_adds_output_column():
    rows = make_rows(["1", "2", "3"])
    result = list(zscore_column(rows, "val"))
    assert all("val_zscore" in r for r in result)


def test_zscore_custom_output_column():
    rows = make_rows(["1", "2", "3"])
    result = list(zscore_column(rows, "val", output_column="z"))
    assert all("z" in r for r in result)


def test_zscore_mean_zero_std_one():
    rows = make_rows(["1", "2", "3", "4", "5"])
    result = list(zscore_column(rows, "val"))
    zscores = [float(r["val_zscore"]) for r in result]
    assert abs(sum(zscores)) < 1e-9
    # population std of z-scores should be 1
    mean_z = sum(zscores) / len(zscores)
    var_z = sum((z - mean_z) ** 2 for z in zscores) / len(zscores)
    assert abs(math.sqrt(var_z) - 1.0) < 1e-9


def test_zscore_non_numeric_uses_default():
    rows = make_rows(["1", "abc", "3"])
    result = list(zscore_column(rows, "val", default="N/A"))
    assert result[1]["val_zscore"] == "N/A"


def test_zscore_constant_column_returns_zero():
    rows = make_rows(["5", "5", "5"])
    result = list(zscore_column(rows, "val"))
    assert all(r["val_zscore"] == "0.0" for r in result)


def test_zscore_precision():
    rows = make_rows(["10", "20", "30"])
    result = list(zscore_column(rows, "val", precision=2))
    for r in result:
        parts = r["val_zscore"].split(".")
        assert len(parts[1]) == 2


def test_zscore_preserves_other_columns():
    rows = make_rows(["1", "2"])
    result = list(zscore_column(rows, "val"))
    assert all("id" in r for r in result)


# ---------------------------------------------------------------------------
# minmax_scale_column
# ---------------------------------------------------------------------------

def test_minmax_adds_output_column():
    rows = make_rows(["0", "5", "10"])
    result = list(minmax_scale_column(rows, "val"))
    assert all("val_scaled" in r for r in result)


def test_minmax_range_zero_to_one():
    rows = make_rows(["0", "5", "10"])
    result = list(minmax_scale_column(rows, "val"))
    scaled = [float(r["val_scaled"]) for r in result]
    assert abs(scaled[0] - 0.0) < 1e-9
    assert abs(scaled[-1] - 1.0) < 1e-9


def test_minmax_custom_range():
    rows = make_rows(["0", "10"])
    result = list(minmax_scale_column(rows, "val", feature_range=(-1.0, 1.0)))
    scaled = [float(r["val_scaled"]) for r in result]
    assert abs(scaled[0] - (-1.0)) < 1e-9
    assert abs(scaled[1] - 1.0) < 1e-9


def test_minmax_non_numeric_uses_default():
    rows = make_rows(["0", "bad", "10"])
    result = list(minmax_scale_column(rows, "val", default="?"))
    assert result[1]["val_scaled"] == "?"


def test_minmax_constant_column_returns_range_min():
    rows = make_rows(["7", "7", "7"])
    result = list(minmax_scale_column(rows, "val", feature_range=(0.0, 1.0)))
    assert all(r["val_scaled"] == "0.000000" for r in result)


def test_minmax_custom_output_column():
    rows = make_rows(["1", "2"])
    result = list(minmax_scale_column(rows, "val", output_column="norm"))
    assert all("norm" in r for r in result)
