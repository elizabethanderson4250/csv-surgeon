"""Integration tests for csv_surgeon/cli_mask.py"""

import csv
import io
import pytest
from pathlib import Path
from csv_surgeon.cli_mask import run_mask


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "input.csv"
    p.write_text(
        "name,card,email\n"
        "Alice,1234567890123456,alice@example.com\n"
        "Bob,9876543210987654,bob@example.com\n"
    )
    return str(p)


@pytest.fixture
def output_path(tmp_path):
    return str(tmp_path / "output.csv")


def _make_args(input_path, output_path, redact=None, mask_chars=None, mask_regex=None):
    class Args:
        pass
    a = Args()
    a.input = input_path
    a.output = output_path
    a.redact = redact or []
    a.mask_chars = mask_chars or []
    a.mask_regex = mask_regex or []
    return a


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_redact_column(sample_csv, output_path):
    args = _make_args(sample_csv, output_path, redact=["name"])
    run_mask(args)
    rows = _read_csv(output_path)
    assert all(r["name"] == "***" for r in rows)


def test_mask_chars_keep_last_four(sample_csv, output_path):
    args = _make_args(sample_csv, output_path, mask_chars=["card:4"])
    run_mask(args)
    rows = _read_csv(output_path)
    assert rows[0]["card"].endswith("3456")
    assert rows[0]["card"].startswith("*")


def test_mask_regex_email(sample_csv, output_path):
    args = _make_args(sample_csv, output_path, mask_regex=["email:[^@]+@"])
    run_mask(args)
    rows = _read_csv(output_path)
    assert "alice" not in rows[0]["email"]
    assert "example.com" in rows[0]["email"]


def test_multiple_masks_applied(sample_csv, output_path):
    args = _make_args(
        sample_csv, output_path,
        redact=["name"],
        mask_chars=["card:4"]
    )
    run_mask(args)
    rows = _read_csv(output_path)
    assert rows[0]["name"] == "***"
    assert rows[0]["card"].endswith("3456")


def test_no_masks_preserves_data(sample_csv, output_path):
    args = _make_args(sample_csv, output_path)
    run_mask(args)
    rows = _read_csv(output_path)
    assert rows[0]["name"] == "Alice"
    assert rows[1]["name"] == "Bob"


def test_output_has_correct_row_count(sample_csv, output_path):
    args = _make_args(sample_csv, output_path, redact=["name"])
    run_mask(args)
    rows = _read_csv(output_path)
    assert len(rows) == 2
