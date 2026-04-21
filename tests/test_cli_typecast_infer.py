"""Integration tests for the auto-cast CLI sub-command."""
import csv
import io
import os
import pytest

from csv_surgeon.cli_typecast_infer import run_typecast_infer


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(
        "name,age,score,active\n"
        "Alice,30,9.5,true\n"
        "Bob,25,8.0,false\n"
        "Carol,28,7.75,yes\n",
        encoding="utf-8",
    )
    return str(p)


@pytest.fixture()
def output_path(tmp_path):
    return str(tmp_path / "out.csv")


class _Args:
    def __init__(self, input, output="-", sample_size=200, stringify=False):
        self.input = input
        self.output = output
        self.sample_size = sample_size
        self.stringify = stringify


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_auto_cast_writes_output_file(sample_csv, output_path):
    run_typecast_infer(_Args(input=sample_csv, output=output_path))
    assert os.path.exists(output_path)


def test_auto_cast_output_row_count(sample_csv, output_path):
    run_typecast_infer(_Args(input=sample_csv, output=output_path))
    rows = _read_csv(output_path)
    assert len(rows) == 3


def test_auto_cast_preserves_headers(sample_csv, output_path):
    run_typecast_infer(_Args(input=sample_csv, output=output_path))
    rows = _read_csv(output_path)
    assert set(rows[0].keys()) == {"name", "age", "score", "active"}


def test_auto_cast_integer_values_cast(sample_csv, output_path):
    run_typecast_infer(_Args(input=sample_csv, output=output_path))
    rows = _read_csv(output_path)
    # values are written as strings in CSV; verify they round-trip as ints
    assert int(rows[0]["age"]) == 30
    assert int(rows[1]["age"]) == 25


def test_auto_cast_float_values_cast(sample_csv, output_path):
    run_typecast_infer(_Args(input=sample_csv, output=output_path))
    rows = _read_csv(output_path)
    assert float(rows[0]["score"]) == pytest.approx(9.5)


def test_auto_cast_bool_values_cast(sample_csv, output_path):
    run_typecast_infer(_Args(input=sample_csv, output=output_path))
    rows = _read_csv(output_path)
    # bool is cast to Python True/False then str()'d
    assert rows[0]["active"] == "True"
    assert rows[1]["active"] == "False"
