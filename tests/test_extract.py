"""Tests for csv_surgeon.extract."""

import pytest
from csv_surgeon.extract import extract_regex, extract_substring, extract_split_index, apply_extract


def make_row(**kwargs):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# extract_regex
# ---------------------------------------------------------------------------

def test_extract_regex_captures_group():
    transform = extract_regex("email", output_column="domain", pattern=r"@(.+)$")
    result = transform(make_row(email="user@example.com"))
    assert result["domain"] == "example.com"


def test_extract_regex_no_match_returns_default():
    transform = extract_regex("code", output_column="num", pattern=r"(\d+)", default="N/A")
    result = transform(make_row(code="abc"))
    assert result["num"] == "N/A"


def test_extract_regex_overwrites_source_when_no_output_column():
    transform = extract_regex("text", pattern=r"(\w+)")
    result = transform(make_row(text="hello world"))
    assert result["text"] == "hello"


def test_extract_regex_missing_column_returns_default():
    transform = extract_regex("missing", output_column="out", pattern=r"(\d+)", default="")
    result = transform(make_row(other="x"))
    assert result["out"] == ""


def test_extract_regex_custom_group():
    transform = extract_regex("date", output_column="year", pattern=r"(\d{4})-(\d{2})-(\d{2})", group=1)
    result = transform(make_row(date="2024-06-15"))
    assert result["year"] == "2024"


# ---------------------------------------------------------------------------
# extract_substring
# ---------------------------------------------------------------------------

def test_extract_substring_basic():
    transform = extract_substring("code", output_column="prefix", start=0, end=3)
    result = transform(make_row(code="ABCDEF"))
    assert result["prefix"] == "ABC"


def test_extract_substring_no_end():
    transform = extract_substring("value", output_column="tail", start=2, end=None)
    result = transform(make_row(value="hello"))
    assert result["tail"] == "llo"


def test_extract_substring_out_of_range_returns_empty():
    transform = extract_substring("v", output_column="out", start=100, end=200)
    result = transform(make_row(v="hi"))
    assert result["out"] == ""


def test_extract_substring_does_not_mutate_original():
    row = make_row(code="ABCDEF")
    transform = extract_substring("code", output_column="prefix", start=0, end=3)
    transform(row)
    assert row["code"] == "ABCDEF"


# ---------------------------------------------------------------------------
# extract_split_index
# ---------------------------------------------------------------------------

def test_extract_split_index_first_element():
    transform = extract_split_index("tags", output_column="first_tag", sep=",", index=0)
    result = transform(make_row(tags="python, data, csv"))
    assert result["first_tag"] == "python"


def test_extract_split_index_last_element():
    transform = extract_split_index("path", output_column="filename", sep="/", index=2)
    result = transform(make_row(path="a/b/file.csv"))
    assert result["filename"] == "file.csv"


def test_extract_split_index_out_of_range_returns_empty():
    transform = extract_split_index("v", output_column="out", sep=",", index=5)
    result = transform(make_row(v="a,b"))
    assert result["out"] == ""


def test_extract_split_index_negative_index_returns_empty():
    transform = extract_split_index("v", output_column="out", sep=",", index=-1)
    result = transform(make_row(v="a,b,c"))
    assert result["out"] == ""


# ---------------------------------------------------------------------------
# apply_extract
# ---------------------------------------------------------------------------

def test_apply_extract_processes_all_rows():
    rows = [make_row(email=f"user{i}@host{i}.com") for i in range(5)]
    transform = extract_regex("email", output_column="host", pattern=r"@(.+)$")
    results = list(apply_extract(rows, transform))
    assert len(results) == 5
    assert all(r["host"].startswith("host") for r in results)


def test_apply_extract_returns_iterator():
    rows = [make_row(v="abc")]
    transform = extract_substring("v", output_column="out", start=0, end=1)
    result = apply_extract(rows, transform)
    # Should be a generator / iterator, not a list
    import types
    assert isinstance(result, types.GeneratorType)
