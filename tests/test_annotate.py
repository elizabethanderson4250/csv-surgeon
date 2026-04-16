"""Tests for csv_surgeon/annotate.py"""
import pytest
from csv_surgeon.annotate import add_row_number, add_timestamp, add_hash, add_constant


def make_rows():
    return [
        {"name": "Alice", "score": "90"},
        {"name": "Bob", "score": "85"},
        {"name": "Carol", "score": "92"},
    ]


def test_add_row_number_default_column():
    result = list(add_row_number(make_rows()))
    assert "_row_num" in result[0]


def test_add_row_number_sequential():
    result = list(add_row_number(make_rows()))
    assert [r["_row_num"] for r in result] == ["1", "2", "3"]


def test_add_row_number_custom_start():
    result = list(add_row_number(make_rows(), start=10))
    assert result[0]["_row_num"] == "10"


def test_add_row_number_custom_column():
    result = list(add_row_number(make_rows(), column="idx"))
    assert "idx" in result[0]
    assert "_row_num" not in result[0]


def test_add_row_number_preserves_original_fields():
    result = list(add_row_number(make_rows()))
    assert result[0]["name"] == "Alice"


def test_add_timestamp_adds_column():
    result = list(add_timestamp(make_rows()))
    assert "_timestamp" in result[0]


def test_add_timestamp_same_for_all_rows():
    result = list(add_timestamp(make_rows()))
    ts_values = {r["_timestamp"] for r in result}
    assert len(ts_values) == 1


def test_add_timestamp_custom_column():
    result = list(add_timestamp(make_rows(), column="ts"))
    assert "ts" in result[0]


def test_add_hash_adds_column():
    result = list(add_hash(make_rows()))
    assert "_hash" in result[0]


def test_add_hash_different_rows_different_hashes():
    result = list(add_hash(make_rows()))
    hashes = [r["_hash"] for r in result]
    assert len(set(hashes)) == 3


def test_add_hash_same_row_same_hash():
    rows = [{"name": "Alice", "score": "90"}]
    r1 = list(add_hash(rows))[0]["_hash"]
    r2 = list(add_hash([{"name": "Alice", "score": "90"}]))[0]["_hash"]
    assert r1 == r2


def test_add_hash_selected_fields():
    rows = [{"name": "Alice", "score": "90", "extra": "x"}]
    h_all = list(add_hash(rows))[0]["_hash"]
    rows2 = [{"name": "Alice", "score": "90", "extra": "DIFFERENT"}]
    h_partial = list(add_hash(rows2, fields=["name", "score"]))[0]["_hash"]
    assert h_all != h_partial  # extra differs so full hash differs
    rows3 = [{"name": "Alice", "score": "90", "extra": "x"}]
    h_partial2 = list(add_hash(rows3, fields=["name", "score"]))[0]["_hash"]
    assert h_partial == h_partial2


def test_add_hash_invalid_algorithm():
    with pytest.raises(ValueError, match="Unsupported"):
        list(add_hash(make_rows(), algorithm="notreal"))


def test_add_hash_sha256():
    result = list(add_hash(make_rows(), algorithm="sha256"))
    assert len(result[0]["_hash"]) == 64


def test_add_constant_adds_column():
    result = list(add_constant(make_rows(), column="source", value="test"))
    assert result[0]["source"] == "test"


def test_add_constant_all_rows_same_value():
    result = list(add_constant(make_rows(), column="env", value="prod"))
    assert all(r["env"] == "prod" for r in result)


def test_add_constant_preserves_other_fields():
    result = list(add_constant(make_rows(), column="tag", value="v1"))
    assert result[1]["name"] == "Bob"
