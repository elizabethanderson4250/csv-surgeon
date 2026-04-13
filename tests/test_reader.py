"""Tests for the StreamingCSVReader module."""

import csv
import pytest
from pathlib import Path

from csv_surgeon.reader import StreamingCSVReader


SAMPLE_DATA = [
    ["id", "name", "age", "city"],
    ["1", "Alice", "30", "New York"],
    ["2", "Bob", "25", "London"],
    ["3", "Carol", "35", "Berlin"],
]


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    """Write a small CSV file and return its path."""
    filepath = tmp_path / "sample.csv"
    with filepath.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerows(SAMPLE_DATA)
    return filepath


def test_headers_are_read_correctly(sample_csv: Path):
    reader = StreamingCSVReader(sample_csv)
    assert reader.headers == ["id", "name", "age", "city"]


def test_rows_returns_dicts(sample_csv: Path):
    reader = StreamingCSVReader(sample_csv)
    rows = list(reader.rows())
    assert len(rows) == 3
    assert rows[0] == {"id": "1", "name": "Alice", "age": "30", "city": "New York"}


def test_raw_rows_skips_header_by_default(sample_csv: Path):
    reader = StreamingCSVReader(sample_csv)
    raw = list(reader.raw_rows())
    assert len(raw) == 3
    assert raw[0] == ["1", "Alice", "30", "New York"]


def test_raw_rows_includes_header_when_requested(sample_csv: Path):
    reader = StreamingCSVReader(sample_csv)
    raw = list(reader.raw_rows(skip_header=False))
    assert len(raw) == 4
    assert raw[0] == ["id", "name", "age", "city"]


def test_row_count(sample_csv: Path):
    reader = StreamingCSVReader(sample_csv)
    assert reader.row_count() == 3


def test_rows_is_a_generator(sample_csv: Path):
    import types
    reader = StreamingCSVReader(sample_csv)
    assert isinstance(reader.rows(), types.GeneratorType)


def test_file_not_found_raises():
    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        StreamingCSVReader("/nonexistent/path/file.csv")


def test_custom_delimiter(tmp_path: Path):
    filepath = tmp_path / "pipe.csv"
    with filepath.open("w", newline="") as fh:
        fh.write("a|b|c\n1|2|3\n4|5|6\n")
    reader = StreamingCSVReader(filepath, delimiter="|")
    assert reader.headers == ["a", "b", "c"]
    rows = list(reader.rows())
    assert rows[0] == {"a": "1", "b": "2", "c": "3"}
