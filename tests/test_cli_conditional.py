"""Integration tests for csv_surgeon/cli_conditional.py"""

import csv
import io
import os
import pytest

from csv_surgeon.cli_conditional import run_conditional, _parse_condition


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "input.csv"
    p.write_text("name,status,label\nAlice,active,\nBob,inactive,\nCarol,active,\n")
    return str(p)


@pytest.fixture
def output_path(tmp_path):
    return str(tmp_path / "output.csv")


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class _Args:
    def __init__(self, input, output, column, when, true_value, false_value):
        self.input = input
        self.output = output
        self.column = column
        self.when = when
        self.true_value = true_value
        self.false_value = false_value


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_conditional_writes_output_file(sample_csv, output_path):
    args = _Args(sample_csv, output_path, "label", "status=active", "YES", "NO")
    run_conditional(args)
    assert os.path.exists(output_path)


def test_conditional_correct_row_count(sample_csv, output_path):
    args = _Args(sample_csv, output_path, "label", "status=active", "YES", "NO")
    run_conditional(args)
    rows = _read_csv(output_path)
    assert len(rows) == 3


def test_conditional_true_branch_applied(sample_csv, output_path):
    args = _Args(sample_csv, output_path, "label", "status=active", "YES", "NO")
    run_conditional(args)
    rows = _read_csv(output_path)
    active = [r for r in rows if r["status"] == "active"]
    assert all(r["label"] == "YES" for r in active)


def test_conditional_false_branch_applied(sample_csv, output_path):
    args = _Args(sample_csv, output_path, "label", "status=active", "YES", "NO")
    run_conditional(args)
    rows = _read_csv(output_path)
    inactive = [r for r in rows if r["status"] == "inactive"]
    assert all(r["label"] == "NO" for r in inactive)


def test_conditional_headers_preserved(sample_csv, output_path):
    args = _Args(sample_csv, output_path, "label", "status=active", "YES", "NO")
    run_conditional(args)
    rows = _read_csv(output_path)
    assert set(rows[0].keys()) == {"name", "status", "label"}


def test_parse_condition_invalid_raises(sample_csv, output_path):
    import argparse
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_condition("no-equals-sign")


def test_parse_condition_matches_correctly():
    cond = _parse_condition("city=Paris")
    assert cond({"city": "Paris"}) is True
    assert cond({"city": "London"}) is False
