"""Tests for transforms.py and TransformPipeline."""

import pytest
from csv_surgeon.transforms import (
    rename, uppercase, lowercase, strip_whitespace,
    replace, regex_replace, cast, apply,
)
from csv_surgeon.transform_pipeline import TransformPipeline


ROW = {"name": "  Alice  ", "age": "30", "city": "New York"}


def test_uppercase_transform():
    col, val = uppercase()("city", ROW)
    assert col == "city"
    assert val == "NEW YORK"


def test_lowercase_transform():
    col, val = lowercase()("city", ROW)
    assert col == "city"
    assert val == "new york"


def test_strip_whitespace_transform():
    col, val = strip_whitespace()("name", ROW)
    assert col == "name"
    assert val == "Alice"


def test_replace_transform():
    col, val = replace("New York", "Boston")("city", ROW)
    assert col == "city"
    assert val == "Boston"


def test_regex_replace_transform():
    col, val = regex_replace(r"\s+", "_")("city", ROW)
    assert col == "city"
    assert val == "New_York"


def test_cast_transform():
    col, val = cast(int)("age", ROW)
    assert col == "age"
    assert val == 30
    assert isinstance(val, int)


def test_apply_transform():
    col, val = apply(lambda v: v[::-1])("city", ROW)
    assert col == "city"
    assert val == "kroY weN"


def test_rename_transform():
    col, val = rename("full_name")("name", ROW)
    assert col == "full_name"
    assert val == "  Alice  "


def test_pipeline_apply_to_row():
    pipeline = TransformPipeline()
    pipeline.add_transform("name", strip_whitespace())
    pipeline.add_transform("age", cast(int))
    pipeline.add_transform("city", uppercase())

    result = pipeline.apply_to_row(ROW)
    assert result["name"] == "Alice"
    assert result["age"] == 30
    assert result["city"] == "NEW YORK"


def test_pipeline_rename_updates_key():
    pipeline = TransformPipeline()
    pipeline.add_transform("name", rename("full_name"))

    result = pipeline.apply_to_row(ROW)
    assert "full_name" in result
    assert "name" not in result
    assert result["full_name"] == "  Alice  "


def test_pipeline_skips_missing_column():
    pipeline = TransformPipeline()
    pipeline.add_transform("nonexistent", uppercase())

    result = pipeline.apply_to_row(ROW)
    assert result == ROW


def test_pipeline_execute_iterator():
    rows = [
        {"name": "alice", "score": "10"},
        {"name": "bob", "score": "20"},
    ]
    pipeline = TransformPipeline()
    pipeline.add_transform("name", uppercase())
    pipeline.add_transform("score", cast(int))

    results = list(pipeline.execute(iter(rows)))
    assert results[0] == {"name": "ALICE", "score": 10}
    assert results[1] == {"name": "BOB", "score": 20}


def test_pipeline_count_and_clear():
    pipeline = TransformPipeline()
    pipeline.add_transform("name", uppercase())
    pipeline.add_transform("city", lowercase())
    assert pipeline.count() == 2
    pipeline.clear()
    assert pipeline.count() == 0


def test_pipeline_chaining():
    pipeline = TransformPipeline()
    result = pipeline.add_transform("name", uppercase()).add_transform("city", lowercase())
    assert result is pipeline
    assert pipeline.count() == 2
