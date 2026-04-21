"""Integration tests for the interpolate CLI sub-command."""
from __future__ import annotations

import csv
import io
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.cli_interpolate import run_interpolate


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "input.csv"
    p.write_text(
        textwrap.dedent("""\
        id,value,label
        1,10,a
        2,,b
        3,,c
        4,40,d
        """)
    )
    return p


@pytest.fixture()
def output_path(tmp_path: Path) -> Path:
    return tmp_path / "output.csv"


def _read_csv(path: Path):
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


class _Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_linear_interpolation_fills_gaps(sample_csv, output_path):
    args = _Args(
        input=str(sample_csv),
        output=str(output_path),
        column="value",
        method="linear",
        output_column=None,
        fill_leading=False,
        fill_trailing=False,
    )
    run_interpolate(args)
    rows = _read_csv(output_path)
    assert rows[1]["value"] == "20.0"
    assert rows[2]["value"] == "30.0"


def test_forward_fill_propagates_value(sample_csv, output_path):
    args = _Args(
        input=str(sample_csv),
        output=str(output_path),
        column="value",
        method="forward",
        output_column=None,
        fill_leading=False,
        fill_trailing=False,
    )
    run_interpolate(args)
    rows = _read_csv(output_path)
    assert rows[1]["value"] == "10"
    assert rows[2]["value"] == "10"


def test_backward_fill_propagates_value(sample_csv, output_path):
    args = _Args(
        input=str(sample_csv),
        output=str(output_path),
        column="value",
        method="backward",
        output_column=None,
        fill_leading=False,
        fill_trailing=False,
    )
    run_interpolate(args)
    rows = _read_csv(output_path)
    assert rows[1]["value"] == "40"
    assert rows[2]["value"] == "40"


def test_output_column_added_to_headers(sample_csv, output_path):
    args = _Args(
        input=str(sample_csv),
        output=str(output_path),
        column="value",
        method="linear",
        output_column="value_filled",
        fill_leading=False,
        fill_trailing=False,
    )
    run_interpolate(args)
    rows = _read_csv(output_path)
    assert "value_filled" in rows[0]
    assert rows[0]["value"] == "10"
    assert rows[1]["value_filled"] == "20.0"


def test_all_rows_written(sample_csv, output_path):
    args = _Args(
        input=str(sample_csv),
        output=str(output_path),
        column="value",
        method="linear",
        output_column=None,
        fill_leading=False,
        fill_trailing=False,
    )
    run_interpolate(args)
    rows = _read_csv(output_path)
    assert len(rows) == 4
