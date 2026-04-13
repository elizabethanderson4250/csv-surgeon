"""Integration tests for the dedup CLI sub-command."""
import csv
import io
import os
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.cli_dedup import run_dedup


CSV_CONTENT = textwrap.dedent("""\
    id,name,dept
    1,Alice,Eng
    2,Bob,HR
    1,Alice,Eng
    3,Carol,Eng
    2,Bob,HR
    4,Dave,Eng
""").strip()


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(CSV_CONTENT)
    return str(p)


@pytest.fixture()
def output_path(tmp_path):
    return str(tmp_path / "out.csv")


def _make_args(**kwargs):
    import argparse
    defaults = {"keep": "first", "output": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_dedup_removes_duplicates(sample_csv, output_path):
    args = _make_args(input=sample_csv, columns="id", output=output_path)
    run_dedup(args)
    rows = _read_csv(output_path)
    assert len(rows) == 4
    ids = [r["id"] for r in rows]
    assert ids == ["1", "2", "3", "4"]


def test_dedup_keep_last(sample_csv, output_path):
    args = _make_args(input=sample_csv, columns="id", output=output_path, keep="last")
    run_dedup(args)
    rows = _read_csv(output_path)
    assert len(rows) == 4


def test_dedup_multi_column(sample_csv, output_path):
    args = _make_args(input=sample_csv, columns="name,dept", output=output_path)
    run_dedup(args)
    rows = _read_csv(output_path)
    assert len(rows) == 4


def test_dedup_missing_column_exits(sample_csv, capsys):
    import argparse
    args = _make_args(input=sample_csv, columns="nonexistent")
    with pytest.raises(SystemExit) as exc_info:
        run_dedup(args)
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "nonexistent" in captured.err


def test_dedup_empty_columns_exits(sample_csv, capsys):
    args = _make_args(input=sample_csv, columns="  ,  ")
    with pytest.raises(SystemExit) as exc_info:
        run_dedup(args)
    assert exc_info.value.code == 1


def test_dedup_stdout_output(sample_csv, capsys):
    args = _make_args(input=sample_csv, columns="id", output=None)
    run_dedup(args)
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    rows = list(reader)
    assert len(rows) == 4
