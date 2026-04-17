"""Tests for csv_surgeon.fingerprint."""
import pytest
from csv_surgeon.fingerprint import fingerprint_columns, fingerprint_rows


def make_rows():
    return [
        {"name": "Alice", "age": "30", "city": "NYC"},
        {"name": "Bob", "age": "25", "city": "LA"},
        {"name": "Alice", "age": "", "city": "NYC"},
        {"name": "Carol", "age": "30", "city": ""},
    ]


def test_fingerprint_count():
    stats = fingerprint_columns(make_rows())
    assert stats["name"]["count"] == 4
    assert stats["age"]["count"] == 3
    assert stats["city"]["count"] == 3


def test_fingerprint_nulls():
    stats = fingerprint_columns(make_rows())
    assert stats["age"]["nulls"] == 1
    assert stats["city"]["nulls"] == 1
    assert stats["name"]["nulls"] == 0


def test_fingerprint_cardinality():
    stats = fingerprint_columns(make_rows())
    assert stats["name"]["cardinality"] == 3  # Alice, Bob, Carol
    assert stats["age"]["cardinality"] == 2   # 25, 30
    assert stats["city"]["cardinality"] == 2  # NYC, LA


def test_fingerprint_uniqueness_range():
    stats = fingerprint_columns(make_rows())
    for col in stats:
        assert 0.0 <= stats[col]["uniqueness"] <= 1.0


def test_fingerprint_samples_limited():
    rows = [{"x": str(i)} for i in range(20)]
    stats = fingerprint_columns(rows, sample_limit=3)
    assert len(stats["x"]["samples"]) == 3


def test_fingerprint_checksum_is_string():
    stats = fingerprint_columns(make_rows())
    assert isinstance(stats["name"]["checksum"], str)
    assert len(stats["name"]["checksum"]) == 32


def test_fingerprint_checksum_changes_with_data():
    rows_a = [{"v": "1"}, {"v": "2"}]
    rows_b = [{"v": "1"}, {"v": "3"}]
    stats_a = fingerprint_columns(rows_a)
    stats_b = fingerprint_columns(rows_b)
    assert stats_a["v"]["checksum"] != stats_b["v"]["checksum"]


def test_fingerprint_empty_rows():
    stats = fingerprint_columns([])
    assert stats == {}


def test_fingerprint_rows_adds_hash_column():
    rows = list(make_rows())
    annotated = list(fingerprint_rows(rows, key_columns=["name", "age"]))
    assert all("_row_hash" in r for r in annotated)


def test_fingerprint_rows_hash_is_hex():
    rows = [{"id": "1", "val": "a"}]
    annotated = list(fingerprint_rows(rows, key_columns=["id"]))
    assert len(annotated[0]["_row_hash"]) == 32


def test_fingerprint_rows_same_key_same_hash():
    rows = [
        {"name": "Alice", "score": "10"},
        {"name": "Alice", "score": "99"},
    ]
    annotated = list(fingerprint_rows(rows, key_columns=["name"]))
    assert annotated[0]["_row_hash"] == annotated[1]["_row_hash"]


def test_fingerprint_rows_different_key_different_hash():
    rows = [
        {"name": "Alice"},
        {"name": "Bob"},
    ]
    annotated = list(fingerprint_rows(rows, key_columns=["name"]))
    assert annotated[0]["_row_hash"] != annotated[1]["_row_hash"]
