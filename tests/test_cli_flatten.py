"""Integration tests for the flatten CLI sub-commands."""
import csv
import io
import os
import tempfile
from types import SimpleNamespace

import pytest

from csv_surgeon.cli_flatten import run_flatten


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "input.csv"
    p.write_text("id,tags,first,last\n1,a|b|c,John,Doe\n2,x,Jane,Smith\n")
    return str(p)


@pytest.fixture()
def output_path(tmp_path):
    return str(tmp_path / "output.csv")


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_explode_creates_extra_rows(sample_csv, output_path):
    args = SimpleNamespace(
        input=sample_csv,
        output=output_path,
        flatten_cmd="explode",
        column="tags",
        separator="|",
        no_strip=False,
    )
    run_flatten(args)
    rows = _read_csv(output_path)
    # row 1 has 3 tags, row 2 has 1 → total 4
    assert len(rows) == 4


def test_explode_preserves_other_columns(sample_csv, output_path):
    args = SimpleNamespace(
        input=sample_csv,
        output=output_path,
        flatten_cmd="explode",
        column="tags",
        separator="|",
        no_strip=False,
    )
    run_flatten(args)
    rows = _read_csv(output_path)
    assert all("id" in r for r in rows)


def test_merge_combines_columns(sample_csv, output_path):
    args = SimpleNamespace(
        input=sample_csv,
        output=output_path,
        flatten_cmd="merge",
        columns=["first", "last"],
        into="full_name",
        separator=" ",
        keep_originals=False,
    )
    run_flatten(args)
    rows = _read_csv(output_path)
    assert rows[0]["full_name"] == "John Doe"
    assert "first" not in rows[0]


def test_merge_keeps_originals(sample_csv, output_path):
    args = SimpleNamespace(
        input=sample_csv,
        output=output_path,
        flatten_cmd="merge",
        columns=["first", "last"],
        into="full_name",
        separator=" ",
        keep_originals=True,
    )
    run_flatten(args)
    rows = _read_csv(output_path)
    assert "first" in rows[0]
    assert "full_name" in rows[0]


def test_split_creates_new_columns(sample_csv, output_path):
    args = SimpleNamespace(
        input=sample_csv,
        output=output_path,
        flatten_cmd="split",
        column="tags",
        into=["tag1"],
        separator="|",
        keep_original=False,
    )
    run_flatten(args)
    rows = _read_csv(output_path)
    assert "tag1" in rows[0]
    assert "tags" not in rows[0]
