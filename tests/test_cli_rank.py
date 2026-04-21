"""Integration tests for csv_surgeon/cli_rank.py"""
import csv
import io
import textwrap
from pathlib import Path
import pytest

from csv_surgeon.cli_rank import run_rank


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(textwrap.dedent("""\
        name,score,group
        alice,30,a
        bob,10,a
        carol,20,b
        dave,10,b
        eve,30,a
    """).lstrip())
    return p


@pytest.fixture()
def output_path(tmp_path: Path) -> Path:
    return tmp_path / "out.csv"


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class _Args:
    def __init__(self, **kw):
        defaults = dict(
            sort_column="score",
            output_column="rank",
            method="dense",
            descending=False,
            numeric=True,
            group_by=None,
            row_number=False,
            start=1,
            output=None,
        )
        defaults.update(kw)
        self.__dict__.update(defaults)


def test_rank_output_file_created(sample_csv, output_path):
    args = _Args(input=str(sample_csv), output=str(output_path))
    run_rank(args)
    assert output_path.exists()


def test_rank_output_row_count(sample_csv, output_path):
    args = _Args(input=str(sample_csv), output=str(output_path))
    run_rank(args)
    rows = _read_csv(output_path)
    assert len(rows) == 5


def test_rank_column_present(sample_csv, output_path):
    args = _Args(input=str(sample_csv), output=str(output_path))
    run_rank(args)
    rows = _read_csv(output_path)
    assert "rank" in rows[0]


def test_rank_ties_same_dense_rank(sample_csv, output_path):
    args = _Args(input=str(sample_csv), output=str(output_path))
    run_rank(args)
    rows = _read_csv(output_path)
    by_name = {r["name"]: r["rank"] for r in rows}
    assert by_name["bob"] == by_name["dave"]
    assert by_name["alice"] == by_name["eve"]


def test_rank_descending(sample_csv, output_path):
    args = _Args(input=str(sample_csv), output=str(output_path), descending=True)
    run_rank(args)
    rows = _read_csv(output_path)
    by_name = {r["name"]: r["rank"] for r in rows}
    assert by_name["alice"] == "1"
    assert by_name["bob"] == "3"


def test_row_number_mode(sample_csv, output_path):
    args = _Args(input=str(sample_csv), output=str(output_path),
                 row_number=True, output_column="rn")
    run_rank(args)
    rows = _read_csv(output_path)
    nums = [r["rn"] for r in rows]
    assert nums == ["1", "2", "3", "4", "5"]


def test_row_number_group_by(sample_csv, output_path):
    args = _Args(input=str(sample_csv), output=str(output_path),
                 row_number=True, output_column="rn", group_by="group")
    run_rank(args)
    rows = _read_csv(output_path)
    # group 'a' has alice, bob, eve => rn 1,2,3; group 'b' has carol, dave => rn 1,2
    by_name = {r["name"]: r["rn"] for r in rows}
    assert by_name["alice"] == "1"
    assert by_name["bob"] == "2"
    assert by_name["eve"] == "3"
    assert by_name["carol"] == "1"
    assert by_name["dave"] == "2"
