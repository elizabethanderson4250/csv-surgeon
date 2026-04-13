"""Tests for csv_surgeon.diff and csv_surgeon.cli_diff."""

import argparse
import csv
import io
import json
import pytest
from pathlib import Path

from csv_surgeon.diff import diff_rows
from csv_surgeon.cli_diff import run_diff


def make_rows(data):
    return [dict(zip(data[0], row)) for row in data[1:]]


LEFT = make_rows([
    ["id", "name", "score"],
    ["1", "Alice", "90"],
    ["2", "Bob",   "80"],
    ["3", "Carol", "70"],
])

RIGHT = make_rows([
    ["id", "name", "score"],
    ["1", "Alice", "95"],   # changed score
    ["3", "Carol", "70"],   # unchanged
    ["4", "Dave",  "85"],   # added
])


def test_added_rows():
    added, _, _ = diff_rows(iter(LEFT), iter(RIGHT), key="id")
    assert len(added) == 1
    assert added[0]["id"] == "4"


def test_removed_rows():
    _, removed, _ = diff_rows(iter(LEFT), iter(RIGHT), key="id")
    assert len(removed) == 1
    assert removed[0]["id"] == "2"


def test_changed_rows():
    _, _, changed = diff_rows(iter(LEFT), iter(RIGHT), key="id")
    assert len(changed) == 1
    assert changed[0]["key"] == "1"
    assert changed[0]["before"] == {"score": "90"}
    assert changed[0]["after"] == {"score": "95"}


def test_no_differences():
    added, removed, changed = diff_rows(iter(LEFT), iter(LEFT), key="id")
    assert added == []
    assert removed == []
    assert changed == []


def test_columns_filter_limits_comparison():
    # Only compare 'name'; score change should be ignored
    _, _, changed = diff_rows(iter(LEFT), iter(RIGHT), key="id", columns=["name"])
    assert changed == []


def test_empty_right():
    added, removed, changed = diff_rows(iter(LEFT), iter([]), key="id")
    assert added == []
    assert len(removed) == len(LEFT)
    assert changed == []


def test_empty_left():
    added, removed, changed = diff_rows(iter([]), iter(RIGHT), key="id")
    assert len(added) == len(RIGHT)
    assert removed == []
    assert changed == []


# --- CLI integration tests ---

@pytest.fixture
def left_csv(tmp_path):
    p = tmp_path / "left.csv"
    p.write_text("id,name,score\n1,Alice,90\n2,Bob,80\n3,Carol,70\n")
    return str(p)


@pytest.fixture
def right_csv(tmp_path):
    p = tmp_path / "right.csv"
    p.write_text("id,name,score\n1,Alice,95\n3,Carol,70\n4,Dave,85\n")
    return str(p)


def _make_args(left, right, key="id", fmt="json", columns=None):
    ns = argparse.Namespace(left=left, right=right, key=key, format=fmt, columns=columns)
    return ns


def test_cli_diff_json_output(left_csv, right_csv, capsys):
    run_diff(_make_args(left_csv, right_csv))
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert len(data["added"]) == 1
    assert len(data["removed"]) == 1
    assert len(data["changed"]) == 1


def test_cli_diff_text_no_differences(left_csv, capsys):
    run_diff(_make_args(left_csv, left_csv, fmt="text"))
    captured = capsys.readouterr().out
    assert "No differences found" in captured
