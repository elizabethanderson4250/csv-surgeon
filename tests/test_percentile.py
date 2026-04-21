"""Tests for csv_surgeon/percentile.py"""

from __future__ import annotations

import pytest

from csv_surgeon.percentile import (
    _percentile,
    compute_percentiles,
    flag_percentile_band,
)


def make_rows(values: list[str], col: str = "score") -> list[dict]:
    return [{col: v} for v in values]


# --- _percentile ---

def test_percentile_0_returns_min():
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 0) == 1.0


def test_percentile_100_returns_max():
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 100) == 5.0


def test_percentile_50_returns_median_odd():
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 50) == 3.0


def test_percentile_50_returns_median_even():
    assert _percentile([1.0, 2.0, 3.0, 4.0], 50) == 2.5


def test_percentile_single_element():
    assert _percentile([42.0], 25) == 42.0


def test_percentile_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        _percentile([], 50)


def test_percentile_out_of_range_raises():
    with pytest.raises(ValueError, match="Percentile"):
        _percentile([1.0, 2.0], 101)


# --- compute_percentiles ---

def test_compute_percentiles_basic():
    rows = make_rows(["10", "20", "30", "40", "50"])
    result = compute_percentiles(rows, "score", [0, 50, 100])
    assert result["p0"] == pytest.approx(10.0)
    assert result["p50"] == pytest.approx(30.0)
    assert result["p100"] == pytest.approx(50.0)


def test_compute_percentiles_skips_non_numeric():
    rows = make_rows(["10", "N/A", "30", "", "50"])
    result = compute_percentiles(rows, "score", [50])
    assert result["p50"] == pytest.approx(30.0)


def test_compute_percentiles_missing_column_skipped():
    rows = [{"other": "x"}, {"other": "y"}]
    result = compute_percentiles(rows, "score", [50])
    # No values collected — percentile of empty raises ValueError
    with pytest.raises(ValueError):
        compute_percentiles(rows, "score", [50])


def test_compute_percentiles_returns_all_requested():
    rows = make_rows([str(i) for i in range(1, 101)])
    result = compute_percentiles(rows, "score", [25, 50, 75])
    assert set(result.keys()) == {"p25", "p50", "p75"}


# --- flag_percentile_band ---

def test_band_labels_low_mid_high():
    rows = make_rows(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
    result = list(flag_percentile_band(rows, "score", lower=25, upper=75))
    labels = [r["percentile_band"] for r in result]
    assert "low" in labels
    assert "mid" in labels
    assert "high" in labels


def test_band_non_numeric_gets_empty_label():
    rows = make_rows(["1", "abc", "3"])
    result = list(flag_percentile_band(rows, "score", lower=25, upper=75))
    assert result[1]["percentile_band"] == ""


def test_band_custom_output_column():
    rows = make_rows(["1", "5", "10"])
    result = list(flag_percentile_band(rows, "score", lower=25, upper=75, output_column="tier"))
    assert "tier" in result[0]
    assert "percentile_band" not in result[0]


def test_band_preserves_other_columns():
    rows = [{"score": "5", "name": "Alice"}, {"score": "10", "name": "Bob"}]
    result = list(flag_percentile_band(rows, "score", lower=25, upper=75))
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"


def test_band_no_numeric_values_all_empty():
    rows = make_rows(["a", "b", "c"])
    result = list(flag_percentile_band(rows, "score", lower=25, upper=75))
    assert all(r["percentile_band"] == "" for r in result)
