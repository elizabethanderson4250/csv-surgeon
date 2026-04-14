"""Integration tests for the window CLI sub-commands."""
import csv
import io
import argparse
import pytest
from csv_surgeon.cli_window import add_window_subparser, run_window


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "input.csv"
    p.write_text("id,value\n1,10\n2,20\n3,30\n4,40\n5,50\n")
    return str(p)


@pytest.fixture
def output_path(tmp_path):
    return str(tmp_path / "output.csv")


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    base = argparse.Namespace()
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


# ── rolling sub-command ───────────────────────────────────────────────────────

def test_rolling_produces_output_file(sample_csv, output_path):
    args = _make_args(
        window_cmd="rolling",
        input=sample_csv,
        output=output_path,
        column="value",
        size=2,
        func="sum",
        output_column="roll_sum",
    )
    run_window(args)
    rows = _read_csv(output_path)
    assert len(rows) == 5


def test_rolling_first_row_empty(sample_csv, output_path):
    args = _make_args(
        window_cmd="rolling",
        input=sample_csv,
        output=output_path,
        column="value",
        size=3,
        func="mean",
        output_column=None,
    )
    run_window(args)
    rows = _read_csv(output_path)
    assert rows[0]["value_rolling"] == ""
    assert rows[1]["value_rolling"] == ""


def test_rolling_correct_value(sample_csv, output_path):
    args = _make_args(
        window_cmd="rolling",
        input=sample_csv,
        output=output_path,
        column="value",
        size=2,
        func="sum",
        output_column="rs",
    )
    run_window(args)
    rows = _read_csv(output_path)
    assert float(rows[1]["rs"]) == pytest.approx(30.0)
    assert float(rows[4]["rs"]) == pytest.approx(90.0)


# ── lag sub-command ───────────────────────────────────────────────────────────

def test_lag_produces_output_file(sample_csv, output_path):
    args = _make_args(
        window_cmd="lag",
        input=sample_csv,
        output=output_path,
        column="value",
        periods=1,
        output_column="prev",
        fill_value="",
    )
    run_window(args)
    rows = _read_csv(output_path)
    assert len(rows) == 5


def test_lag_correct_values(sample_csv, output_path):
    args = _make_args(
        window_cmd="lag",
        input=sample_csv,
        output=output_path,
        column="value",
        periods=1,
        output_column="prev",
        fill_value="",
    )
    run_window(args)
    rows = _read_csv(output_path)
    assert rows[0]["prev"] == ""
    assert rows[1]["prev"] == "10"
    assert rows[4]["prev"] == "40"
