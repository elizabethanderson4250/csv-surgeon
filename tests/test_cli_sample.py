"""Integration tests for the 'sample' CLI sub-command."""

import argparse
import csv
import io
import textwrap

import pytest

from csv_surgeon.cli_sample import add_sample_subparser, run_sample


@pytest.fixture()
def sample_csv(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text(
        textwrap.dedent("""\
            id,name,score
            1,Alice,90
            2,Bob,85
            3,Carol,78
            4,Dave,92
            5,Eve,88
            6,Frank,74
            7,Grace,95
            8,Heidi,81
            9,Ivan,67
            10,Judy,77
        """)
    )
    return str(path)


@pytest.fixture()
def output_path(tmp_path):
    return str(tmp_path / "out.csv")


def _make_args(**kwargs):
    base = dict(input=None, output=None, head=None, reservoir=None, fraction=None, seed=None)
    base.update(kwargs)
    ns = argparse.Namespace(**base)
    ns.func = run_sample
    return ns


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_head_writes_first_n(sample_csv, output_path):
    args = _make_args(input=sample_csv, output=output_path, head=3)
    run_sample(args)
    rows = _read_csv(output_path)
    assert len(rows) == 3
    assert rows[0]["id"] == "1"
    assert rows[2]["id"] == "3"


def test_reservoir_writes_n_rows(sample_csv, output_path):
    args = _make_args(input=sample_csv, output=output_path, reservoir=5, seed=0)
    run_sample(args)
    rows = _read_csv(output_path)
    assert len(rows) == 5


def test_fraction_writes_header(sample_csv, output_path):
    args = _make_args(input=sample_csv, output=output_path, fraction=1.0, seed=1)
    run_sample(args)
    rows = _read_csv(output_path)
    assert len(rows) == 10
    assert "name" in rows[0]


def test_subparser_registered():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_sample_subparser(sub)
    args = parser.parse_args(["sample", "in.csv", "out.csv", "--head", "5"])
    assert args.head == 5
    assert args.input == "in.csv"
