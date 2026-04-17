"""Integration tests for the bin CLI subcommand."""
import csv
import io
import pytest
from csv_surgeon.cli_bin_column import run_bin_column


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,score\nalice,5\nbob,15\ncarol,25\ndave,bad\n")
    return str(p)


@pytest.fixture
def output_path(tmp_path):
    return str(tmp_path / "out.csv")


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_fixed_bins_creates_output(sample_csv, output_path):
    args = _Args(
        input=sample_csv,
        output=output_path,
        column="score",
        output_column=None,
        default="",
        edges=[0, 10, 20, 30],
        labels=["low", "mid", "high"],
        quantiles=None,
    )
    run_bin_column(args)
    rows = _read_csv(output_path)
    assert len(rows) == 4


def test_fixed_bins_correct_labels(sample_csv, output_path):
    args = _Args(
        input=sample_csv,
        output=output_path,
        column="score",
        output_column=None,
        default="OOB",
        edges=[0, 10, 20, 30],
        labels=["low", "mid", "high"],
        quantiles=None,
    )
    run_bin_column(args)
    rows = _read_csv(output_path)
    bins = {r["name"]: r["score_bin"] for r in rows}
    assert bins["alice"] == "low"
    assert bins["bob"] == "mid"
    assert bins["carol"] == "high"
    assert bins["dave"] == "OOB"


def test_quantile_bins_creates_output(sample_csv, output_path):
    args = _Args(
        input=sample_csv,
        output=output_path,
        column="score",
        output_column="tier",
        default="",
        edges=None,
        labels=None,
        quantiles=2,
    )
    run_bin_column(args)
    rows = _read_csv(output_path)
    assert all("tier" in r for r in rows)


def test_custom_output_column_name(sample_csv, output_path):
    args = _Args(
        input=sample_csv,
        output=output_path,
        column="score",
        output_column="bucket",
        default="",
        edges=[0, 30],
        labels=["all"],
        quantiles=None,
    )
    run_bin_column(args)
    rows = _read_csv(output_path)
    assert "bucket" in rows[0]
    assert "score_bin" not in rows[0]
