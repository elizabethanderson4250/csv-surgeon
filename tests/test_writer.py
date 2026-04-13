import os
import csv
import pytest
from csv_surgeon.writer import StreamingCSVWriter


FIELDNAMES = ["id", "name", "email"]

SAMPLE_ROWS = [
    {"id": "1", "name": "Alice", "email": "alice@example.com"},
    {"id": "2", "name": "Bob", "email": "bob@example.com"},
    {"id": "3", "name": "Charlie", "email": "charlie@example.com"},
]


@pytest.fixture
def output_path(tmp_path):
    return str(tmp_path / "output.csv")


def test_write_rows_creates_file(output_path):
    writer = StreamingCSVWriter(output_path, FIELDNAMES)
    writer.write_rows(iter(SAMPLE_ROWS))
    assert os.path.exists(output_path)


def test_write_rows_correct_count(output_path):
    writer = StreamingCSVWriter(output_path, FIELDNAMES)
    count = writer.write_rows(iter(SAMPLE_ROWS))
    assert count == 3


def test_write_rows_header_present(output_path):
    writer = StreamingCSVWriter(output_path, FIELDNAMES)
    writer.write_rows(iter(SAMPLE_ROWS))
    with open(output_path) as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == FIELDNAMES


def test_write_rows_data_integrity(output_path):
    writer = StreamingCSVWriter(output_path, FIELDNAMES)
    writer.write_rows(iter(SAMPLE_ROWS))
    with open(output_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert rows[0]["name"] == "Alice"
    assert rows[1]["email"] == "bob@example.com"
    assert rows[2]["id"] == "3"


def test_write_rows_without_header(output_path):
    writer = StreamingCSVWriter(output_path, FIELDNAMES)
    writer.write_rows(iter(SAMPLE_ROWS), write_header=False)
    with open(output_path) as f:
        lines = f.readlines()
    assert len(lines) == 3
    assert "id" not in lines[0]


def test_write_raw_rows(output_path):
    raw = [["1", "Alice", "alice@example.com"], ["2", "Bob", "bob@example.com"]]
    writer = StreamingCSVWriter(output_path, FIELDNAMES)
    count = writer.write_raw_rows(iter(raw))
    assert count == 2
    with open(output_path) as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == FIELDNAMES
        first = next(reader)
        assert first == ["1", "Alice", "alice@example.com"]


def test_to_string_returns_csv(output_path):
    writer = StreamingCSVWriter(output_path, FIELDNAMES)
    result = writer.to_string(iter(SAMPLE_ROWS))
    assert "id,name,email" in result
    assert "Alice" in result
    assert "charlie@example.com" in result


def test_to_string_without_header(output_path):
    writer = StreamingCSVWriter(output_path, FIELDNAMES)
    result = writer.to_string(iter(SAMPLE_ROWS), write_header=False)
    assert "id,name,email" not in result
    assert "Alice" in result


def test_write_empty_rows(output_path):
    writer = StreamingCSVWriter(output_path, FIELDNAMES)
    count = writer.write_rows(iter([]))
    assert count == 0
    with open(output_path) as f:
        content = f.read()
    assert "id,name,email" in content
