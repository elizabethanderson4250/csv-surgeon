"""Integration tests for the regex-filter CLI subcommand."""
import csv
import io
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.cli_regex_filter import run_regex_filter


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "input.csv"
    p.write_text(
        textwrap.dedent("""\
            name,city,score
            Alice,Amsterdam,90
            Bob,Berlin,75
            Charlie,amsterdam,88
            Diana,Dublin,55
        """)
    )
    return p


@pytest.fixture()
def output_path(tmp_path: Path) -> Path:
    return tmp_path / "output.csv"


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class _Args:
    def __init__(self, input, output, column, pattern, ignore_case=False, invert=False):
        self.input = input
        self.output = output
        self.column = column
        self.pattern = pattern
        self.ignore_case = ignore_case
        self.invert = invert


def test_filter_single_column(sample_csv, output_path):
    args = _Args(str(sample_csv), str(output_path), "city", r"^Ber")
    run_regex_filter(args)
    rows = _read_csv(output_path)
    assert len(rows) == 1
    assert rows[0]["name"] == "Bob"


def test_filter_ignore_case(sample_csv, output_path):
    args = _Args(str(sample_csv), str(output_path), "city", r"amsterdam", ignore_case=True)
    run_regex_filter(args)
    rows = _read_csv(output_path)
    assert len(rows) == 2


def test_filter_invert(sample_csv, output_path):
    args = _Args(str(sample_csv), str(output_path), "city", r"^Ber", invert=True)
    run_regex_filter(args)
    rows = _read_csv(output_path)
    assert len(rows) == 3
    assert all(r["city"] != "Berlin" for r in rows)


def test_filter_no_column_searches_all(sample_csv, output_path):
    args = _Args(str(sample_csv), str(output_path), None, r"^9")
    run_regex_filter(args)
    rows = _read_csv(output_path)
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"


def test_filter_no_matches_writes_header_only(sample_csv, output_path):
    args = _Args(str(sample_csv), str(output_path), "city", r"^ZZZNOMATCH")
    run_regex_filter(args)
    rows = _read_csv(output_path)
    assert rows == []
    # Header should still be present
    content = output_path.read_text()
    assert "name" in content
