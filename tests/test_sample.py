"""Tests for csv_surgeon.sample."""

import pytest

from csv_surgeon.sample import head, sample_fraction, sample_rows


def make_rows(n: int):
    return [{"id": str(i), "val": str(i * 2)} for i in range(n)]


# ---------------------------------------------------------------------------
# head
# ---------------------------------------------------------------------------

def test_head_returns_first_n():
    rows = make_rows(20)
    result = head(iter(rows), n=5)
    assert len(result) == 5
    assert result[0]["id"] == "0"
    assert result[4]["id"] == "4"


def test_head_fewer_rows_than_n():
    rows = make_rows(3)
    result = head(iter(rows), n=10)
    assert len(result) == 3


def test_head_invalid_n():
    with pytest.raises(ValueError):
        head(iter(make_rows(5)), n=0)


# ---------------------------------------------------------------------------
# sample_rows (reservoir)
# ---------------------------------------------------------------------------

def test_sample_rows_exact_count():
    rows = make_rows(100)
    result = sample_rows(iter(rows), n=20, seed=42)
    assert len(result) == 20


def test_sample_rows_all_from_source():
    rows = make_rows(50)
    ids = {r["id"] for r in rows}
    result = sample_rows(iter(rows), n=10, seed=0)
    for r in result:
        assert r["id"] in ids


def test_sample_rows_smaller_stream():
    rows = make_rows(5)
    result = sample_rows(iter(rows), n=20, seed=1)
    assert len(result) == 5


def test_sample_rows_reproducible():
    rows = make_rows(200)
    r1 = sample_rows(iter(rows), n=30, seed=99)
    r2 = sample_rows(iter(rows), n=30, seed=99)
    assert r1 == r2


def test_sample_rows_invalid_n():
    with pytest.raises(ValueError):
        sample_rows(iter(make_rows(10)), n=-1)


# ---------------------------------------------------------------------------
# sample_fraction
# ---------------------------------------------------------------------------

def test_sample_fraction_fraction_one_keeps_all():
    rows = make_rows(50)
    result = sample_fraction(iter(rows), fraction=1.0, seed=7)
    assert len(result) == 50


def test_sample_fraction_roughly_correct_size():
    rows = make_rows(10_000)
    result = sample_fraction(iter(rows), fraction=0.1, seed=42)
    # Allow ±3 % absolute tolerance
    assert 700 <= len(result) <= 1300


def test_sample_fraction_reproducible():
    rows = make_rows(1000)
    r1 = sample_fraction(iter(rows), fraction=0.25, seed=5)
    r2 = sample_fraction(iter(rows), fraction=0.25, seed=5)
    assert r1 == r2


def test_sample_fraction_invalid():
    with pytest.raises(ValueError):
        sample_fraction(iter(make_rows(10)), fraction=0.0)
    with pytest.raises(ValueError):
        sample_fraction(iter(make_rows(10)), fraction=1.5)
