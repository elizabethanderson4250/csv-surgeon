"""Tests for csv_surgeon.window"""
import pytest
from csv_surgeon.window import lag, rolling_aggregate, rolling_window


def make_rows(values, col="value"):
    return [{col: str(v)} for v in values]


# ── rolling_window ────────────────────────────────────────────────────────────

def test_rolling_window_basic():
    rows = make_rows([1, 2, 3, 4])
    windows = list(rolling_window(rows, 2))
    assert len(windows) == 3
    assert windows[0] == [{"value": "1"}, {"value": "2"}]
    assert windows[-1] == [{"value": "3"}, {"value": "4"}]


def test_rolling_window_size_equals_len():
    rows = make_rows([10, 20, 30])
    windows = list(rolling_window(rows, 3))
    assert len(windows) == 1
    assert windows[0] == rows


def test_rolling_window_size_larger_than_rows():
    rows = make_rows([1, 2])
    windows = list(rolling_window(rows, 5))
    assert windows == []


def test_rolling_window_invalid_size():
    with pytest.raises(ValueError):
        list(rolling_window(make_rows([1, 2, 3]), 0))


# ── rolling_aggregate ─────────────────────────────────────────────────────────

def test_rolling_aggregate_mean():
    import statistics
    rows = make_rows([1, 2, 3, 4, 5])
    result = list(rolling_aggregate(rows, "value", 3, statistics.mean, "roll_mean"))
    assert len(result) == 5
    assert result[0]["roll_mean"] == ""
    assert result[1]["roll_mean"] == ""
    assert float(result[2]["roll_mean"]) == pytest.approx(2.0)
    assert float(result[4]["roll_mean"]) == pytest.approx(4.0)


def test_rolling_aggregate_sum():
    rows = make_rows([10, 20, 30])
    result = list(rolling_aggregate(rows, "value", 2, sum, "roll_sum"))
    assert result[0]["roll_sum"] == ""
    assert float(result[1]["roll_sum"]) == pytest.approx(30.0)
    assert float(result[2]["roll_sum"]) == pytest.approx(50.0)


def test_rolling_aggregate_default_output_column():
    rows = make_rows([1, 2, 3])
    result = list(rolling_aggregate(rows, "value", 2, sum))
    assert "value_rolling" in result[0]


def test_rolling_aggregate_non_numeric_skips():
    rows = [{"value": "a"}, {"value": "1"}, {"value": "2"}]
    result = list(rolling_aggregate(rows, "value", 2, sum, "out"))
    assert result[0]["out"] == ""
    assert result[1]["out"] == ""


def test_rolling_aggregate_invalid_size():
    with pytest.raises(ValueError):
        list(rolling_aggregate(make_rows([1, 2]), "value", 0, sum))


# ── lag ───────────────────────────────────────────────────────────────────────

def test_lag_single_period():
    rows = make_rows([10, 20, 30])
    result = list(lag(rows, "value", periods=1, output_column="prev"))
    assert result[0]["prev"] == ""
    assert result[1]["prev"] == "10"
    assert result[2]["prev"] == "20"


def test_lag_two_periods():
    rows = make_rows([1, 2, 3, 4])
    result = list(lag(rows, "value", periods=2, output_column="lag2"))
    assert result[0]["lag2"] == ""
    assert result[1]["lag2"] == ""
    assert result[2]["lag2"] == "1"
    assert result[3]["lag2"] == "2"


def test_lag_custom_fill_value():
    rows = make_rows([5, 10])
    result = list(lag(rows, "value", periods=1, fill_value="N/A"))
    assert result[0]["value_lag1"] == "N/A"


def test_lag_invalid_periods():
    with pytest.raises(ValueError):
        list(lag(make_rows([1, 2]), "value", periods=0))


def test_lag_preserves_other_columns():
    rows = [{"id": "1", "value": "100"}, {"id": "2", "value": "200"}]
    result = list(lag(rows, "value", periods=1, output_column="prev_value"))
    assert result[1]["id"] == "2"
    assert result[1]["prev_value"] == "100"
