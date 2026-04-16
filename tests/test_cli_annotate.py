"""CLI integration tests for the annotate sub-command."""
import csv
import io
import pytest
from csv_surgeon.cli_annotate import run_annotate


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "input.csv"
    p.write_text("name,score\nAlice,90\nBob,85\nCarol,92\n")
    return str(p)


@pytest.fixture
def output_path(tmp_path):
    return str(tmp_path / "output.csv")


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class _Args:
    def __init__(self, input, output, **kwargs):
        self.input = input
        self.output = output
        self.row_num = kwargs.get("row_num", None)
        self.timestamp = kwargs.get("timestamp", None)
        self.hash = kwargs.get("hash", None)
        self.hash_fields = kwargs.get("hash_fields", None)
        self.hash_algo = kwargs.get("hash_algo", "md5")
        self.constant = kwargs.get("constant", None)


def test_row_num_column_present(sample_csv, output_path):
    args = _Args(sample_csv, output_path, row_num="_row_num")
    run_annotate(args)
    rows = _read_csv(output_path)
    assert "_row_num" in rows[0]


def test_row_num_values_sequential(sample_csv, output_path):
    args = _Args(sample_csv, output_path, row_num="n")
    run_annotate(args)
    rows = _read_csv(output_path)
    assert [r["n"] for r in rows] == ["1", "2", "3"]


def test_timestamp_column_present(sample_csv, output_path):
    args = _Args(sample_csv, output_path, timestamp="ts")
    run_annotate(args)
    rows = _read_csv(output_path)
    assert "ts" in rows[0]


def test_hash_column_present(sample_csv, output_path):
    args = _Args(sample_csv, output_path, hash="fp")
    run_annotate(args)
    rows = _read_csv(output_path)
    assert "fp" in rows[0]


def test_hash_unique_per_row(sample_csv, output_path):
    args = _Args(sample_csv, output_path, hash="fp")
    run_annotate(args)
    rows = _read_csv(output_path)
    hashes = [r["fp"] for r in rows]
    assert len(set(hashes)) == 3


def test_constant_column(sample_csv, output_path):
    args = _Args(sample_csv, output_path, constant=["env", "staging"])
    run_annotate(args)
    rows = _read_csv(output_path)
    assert all(r["env"] == "staging" for r in rows)


def test_combined_annotations(sample_csv, output_path):
    args = _Args(sample_csv, output_path, row_num="n", constant=["src", "etl"])
    run_annotate(args)
    rows = _read_csv(output_path)
    assert "n" in rows[0]
    assert "src" in rows[0]
    assert rows[0]["src"] == "etl"
