"""Integration tests for the join CLI subcommand."""

import csv
import io
import argparse
import pytest
from pathlib import Path
from csv_surgeon.cli_join import run_join


@pytest.fixture
def left_csv(tmp_path: Path) -> Path:
    p = tmp_path / "left.csv"
    p.write_text("id,name\n1,Alice\n2,Bob\n3,Carol\n")
    return p


@pytest.fixture
def right_csv(tmp_path: Path) -> Path:
    p = tmp_path / "right.csv"
    p.write_text("user_id,city\n1,London\n2,Paris\n4,Berlin\n")
    return p


@pytest.fixture
def output_path(tmp_path: Path) -> Path:
    return tmp_path / "output.csv"


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"how": "inner", "right_prefix": "right_", "output": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _read_csv(path: Path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_inner_join_cli_row_count(left_csv, right_csv, output_path):
    args = _make_args(left=str(left_csv), right=str(right_csv),
                      left_on="id", right_on="user_id", output=str(output_path))
    run_join(args)
    rows = _read_csv(output_path)
    assert len(rows) == 2


def test_inner_join_cli_correct_ids(left_csv, right_csv, output_path):
    args = _make_args(left=str(left_csv), right=str(right_csv),
                      left_on="id", right_on="user_id", output=str(output_path))
    run_join(args)
    rows = _read_csv(output_path)
    ids = {r["id"] for r in rows}
    assert ids == {"1", "2"}


def test_inner_join_cli_merged_column(left_csv, right_csv, output_path):
    args = _make_args(left=str(left_csv), right=str(right_csv),
                      left_on="id", right_on="user_id", output=str(output_path))
    run_join(args)
    rows = _read_csv(output_path)
    alice = next(r for r in rows if r["id"] == "1")
    assert alice["city"] == "London"


def test_left_join_cli_row_count(left_csv, right_csv, output_path):
    args = _make_args(left=str(left_csv), right=str(right_csv),
                      left_on="id", right_on="user_id", how="left",
                      output=str(output_path))
    run_join(args)
    rows = _read_csv(output_path)
    assert len(rows) == 3


def test_left_join_cli_missing_fill(left_csv, right_csv, output_path):
    args = _make_args(left=str(left_csv), right=str(right_csv),
                      left_on="id", right_on="user_id", how="left",
                      output=str(output_path))
    run_join(args)
    rows = _read_csv(output_path)
    carol = next(r for r in rows if r["id"] == "3")
    assert carol["city"] == ""


def test_inner_join_no_matches_creates_empty_file(left_csv, tmp_path, output_path):
    right = tmp_path / "no_match.csv"
    right.write_text("user_id,city\n99,Nowhere\n")
    args = _make_args(left=str(left_csv), right=str(right),
                      left_on="id", right_on="user_id", output=str(output_path))
    run_join(args)
    assert output_path.exists()
