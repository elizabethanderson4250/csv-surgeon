"""Tests for csv_surgeon/cli_format.py"""
import csv
import io
import pytest
from csv_surgeon.cli_format import run_format


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "input.csv"
    p.write_text("id,name,price\n1,alice smith,9.5\n2,bob jones,1234.1\n")
    return str(p)


@pytest.fixture
def output_path(tmp_path):
    return str(tmp_path / "output.csv")


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class _Args:
    def __init__(self, input, output, zero_pad=None, title_case=None,
                 wrap=None, number_format=None, strip=None, remove_non_alphanumeric=None):
        self.input = input
        self.output = output
        self.zero_pad = zero_pad or []
        self.title_case = title_case or []
        self.wrap = wrap or []
        self.number_format = number_format or []
        self.strip = strip or []
        self.remove_non_alphanumeric = remove_non_alphanumeric or []


def test_zero_pad_via_cli(sample_csv, output_path):
    args = _Args(sample_csv, output_path, zero_pad=[["id", "4"]])
    run_format(args)
    rows = _read_csv(output_path)
    assert rows[0]["id"] == "0001"
    assert rows[1]["id"] == "0002"


def test_title_case_via_cli(sample_csv, output_path):
    args = _Args(sample_csv, output_path, title_case=["name"])
    run_format(args)
    rows = _read_csv(output_path)
    assert rows[0]["name"] == "Alice Smith"
    assert rows[1]["name"] == "Bob Jones"


def test_number_format_via_cli(sample_csv, output_path):
    args = _Args(sample_csv, output_path, number_format=[["price", "2"]])
    run_format(args)
    rows = _read_csv(output_path)
    assert rows[0]["price"] == "9.50"


def test_combined_transforms(sample_csv, output_path):
    args = _Args(sample_csv, output_path, title_case=["name"], number_format=[["price", "2"]])
    run_format(args)
    rows = _read_csv(output_path)
    assert rows[0]["name"] == "Alice Smith"
    assert rows[0]["price"] == "9.50"


def test_no_transforms_passthrough(sample_csv, output_path):
    args = _Args(sample_csv, output_path)
    run_format(args)
    rows = _read_csv(output_path)
    assert len(rows) == 2
    assert rows[0]["name"] == "alice smith"
