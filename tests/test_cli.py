import os
import csv
import pytest
from csv_surgeon.cli import run


@pytest.fixture
def sample_csv(tmp_path):
    path = str(tmp_path / "sample.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "age", "city"])
        writer.writerow(["1", "Alice", "30", "New York"])
        writer.writerow(["2", "bob", "17", "London"])
        writer.writerow(["3", "Charlie", "25", "Paris"])
        writer.writerow(["4", "diana", "22", "Berlin"])
    return path


@pytest.fixture
def output_path(tmp_path):
    return str(tmp_path / "output.csv")


def read_output(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def test_cli_no_filters_writes_all_rows(sample_csv, output_path):
    run([sample_csv, "-o", output_path])
    rows = read_output(output_path)
    assert len(rows) == 4


def test_cli_filter_equals(sample_csv, output_path):
    run([sample_csv, "-o", output_path, "--filter", "city:eq:London"])
    rows = read_output(output_path)
    assert len(rows) == 1
    assert rows[0]["name"] == "bob"


def test_cli_filter_greater_than(sample_csv, output_path):
    run([sample_csv, "-o", output_path, "--filter", "age:gt:20"])
    rows = read_output(output_path)
    assert all(int(r["age"]) > 20 for r in rows)


def test_cli_transform_uppercase(sample_csv, output_path):
    run([sample_csv, "-o", output_path, "--transform", "name:uppercase"])
    rows = read_output(output_path)
    assert rows[1]["name"] == "BOB"
    assert rows[3]["name"] == "DIANA"


def test_cli_transform_lowercase(sample_csv, output_path):
    run([sample_csv, "-o", output_path, "--transform", "name:lowercase"])
    rows = read_output(output_path)
    assert rows[0]["name"] == "alice"
    assert rows[2]["name"] == "charlie"


def test_cli_filter_and_transform_combined(sample_csv, output_path):
    run([
        sample_csv, "-o", output_path,
        "--filter", "age:gt:20",
        "--transform", "name:uppercase",
    ])
    rows = read_output(output_path)
    assert all(int(r["age"]) > 20 for r in rows)
    assert all(r["name"] == r["name"].upper() for r in rows)


def test_cli_output_has_header(sample_csv, output_path):
    run([sample_csv, "-o", output_path])
    with open(output_path) as f:
        first_line = f.readline()
    assert "id" in first_line
    assert "name" in first_line
