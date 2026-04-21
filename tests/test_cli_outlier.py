"""Integration tests for the outlier CLI sub-command."""
from __future__ import annotations

import csv
import io
import textwrap
from pathlib import Path

import pytest
from csv_surgeon.cli_outlier import run_outlier


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        id,score
        1,10
        2,11
        3,12
        4,13
        5,14
        6,15
        7,200
    """)
    p = tmp_path / "input.csv"
    p.write_text(content)
    return p


@pytest.fixture()
def output_path(tmp_path: Path) -> Path:
    return tmp_path / "output.csv"


def _read_csv(path: Path) -> list[dict]:
    return list(csv.DictReader(path.read_text().splitlines()))


class _Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_flag_iqr_creates_output(sample_csv, output_path):
    args = _Args(
        input=str(sample_csv),
        output=str(output_path),
        column="score",
        method="iqr",
        multiplier=1.5,
        threshold=3.0,
        action="flag",
        output_column="is_outlier",
    )
    run_outlier(args)
    assert output_path.exists()


def test_flag_iqr_adds_column(sample_csv, output_path):
    args = _Args(
        input=str(sample_csv),
        output=str(output_path),
        column="score",
        method="iqr",
        multiplier=1.5,
        threshold=3.0,
        action="flag",
        output_column="is_outlier",
    )
    run_outlier(args)
    rows = _read_csv(output_path)
    assert all("is_outlier" in r for r in rows)


def test_flag_iqr_marks_extreme_value(sample_csv, output_path):
    args = _Args(
        input=str(sample_csv),
        output=str(output_path),
        column="score",
        method="iqr",
        multiplier=1.5,
        threshold=3.0,
        action="flag",
        output_column="is_outlier",
    )
    run_outlier(args)
    rows = _read_csv(output_path)
    flagged = [r for r in rows if r["is_outlier"] == "1"]
    assert any(r["score"] == "200" for r in flagged)


def test_remove_action_excludes_outlier(sample_csv, output_path):
    args = _Args(
        input=str(sample_csv),
        output=str(output_path),
        column="score",
        method="iqr",
        multiplier=1.5,
        threshold=3.0,
        action="remove",
        output_column="is_outlier",
    )
    run_outlier(args)
    rows = _read_csv(output_path)
    assert all(r["score"] != "200" for r in rows)


def test_flag_zscore_method(sample_csv, output_path):
    args = _Args(
        input=str(sample_csv),
        output=str(output_path),
        column="score",
        method="zscore",
        multiplier=1.5,
        threshold=2.0,
        action="flag",
        output_column="is_outlier",
    )
    run_outlier(args)
    rows = _read_csv(output_path)
    flagged = [r for r in rows if r["is_outlier"] == "1"]
    assert len(flagged) >= 1
