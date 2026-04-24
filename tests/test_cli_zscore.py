"""Integration tests for the zscore CLI sub-command."""
from __future__ import annotations

import csv
import io
import textwrap

import pytest

from csv_surgeon.cli_zscore import run_zscore


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "input.csv"
    p.write_text(textwrap.dedent("""\
        id,score
        1,10
        2,20
        3,30
        4,bad
    """))
    return str(p)


@pytest.fixture()
def output_path(tmp_path):
    return str(tmp_path / "output.csv")


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


class _Args:
    def __init__(self, **kwargs):
        defaults = dict(
            method="zscore",
            output_column=None,
            default="",
            precision=6,
            feature_range="0,1",
        )
        defaults.update(kwargs)
        for k, v in defaults.items():
            setattr(self, k, v)


def test_zscore_creates_output_file(sample_csv, output_path):
    args = _Args(input=sample_csv, output=output_path, column="score")
    run_zscore(args)
    rows = _read_csv(output_path)
    assert len(rows) == 4


def test_zscore_output_column_present(sample_csv, output_path):
    args = _Args(input=sample_csv, output=output_path, column="score")
    run_zscore(args)
    rows = _read_csv(output_path)
    assert "score_zscore" in rows[0]


def test_zscore_non_numeric_default(sample_csv, output_path):
    args = _Args(input=sample_csv, output=output_path, column="score", default="N/A")
    run_zscore(args)
    rows = _read_csv(output_path)
    bad_row = next(r for r in rows if r["score"] == "bad")
    assert bad_row["score_zscore"] == "N/A"


def test_minmax_creates_output_file(sample_csv, output_path):
    args = _Args(input=sample_csv, output=output_path, column="score", method="minmax")
    run_zscore(args)
    rows = _read_csv(output_path)
    assert len(rows) == 4


def test_minmax_output_column_present(sample_csv, output_path):
    args = _Args(input=sample_csv, output=output_path, column="score", method="minmax")
    run_zscore(args)
    rows = _read_csv(output_path)
    assert "score_scaled" in rows[0]


def test_minmax_min_is_zero(sample_csv, output_path):
    args = _Args(input=sample_csv, output=output_path, column="score", method="minmax")
    run_zscore(args)
    rows = _read_csv(output_path)
    numeric_rows = [r for r in rows if r["score"] != "bad"]
    scaled = [float(r["score_scaled"]) for r in numeric_rows]
    assert abs(min(scaled) - 0.0) < 1e-9


def test_custom_output_column_name(sample_csv, output_path):
    args = _Args(
        input=sample_csv, output=output_path, column="score", output_column="z_val"
    )
    run_zscore(args)
    rows = _read_csv(output_path)
    assert "z_val" in rows[0]
