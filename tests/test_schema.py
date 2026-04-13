"""Tests for csv_surgeon.schema."""
from __future__ import annotations

import pytest

from csv_surgeon.schema import (
    SchemaViolation,
    _infer_type,
    _merge_types,
    enforce_schema,
    infer_schema,
)


# ---------------------------------------------------------------------------
# _infer_type
# ---------------------------------------------------------------------------


def test_infer_integer():
    assert _infer_type("42") == "integer"
    assert _infer_type(" -7 ") == "integer"


def test_infer_float():
    assert _infer_type("3.14") == "float"
    assert _infer_type("-0.5") == "float"


def test_infer_boolean():
    for v in ("true", "False", "yes", "NO", "1", "0"):
        assert _infer_type(v) == "boolean", v


def test_infer_string():
    assert _infer_type("hello") == "string"
    assert _infer_type("") == "string"


# ---------------------------------------------------------------------------
# _merge_types
# ---------------------------------------------------------------------------


def test_merge_same_type():
    assert _merge_types("integer", "integer") == "integer"


def test_merge_integer_float():
    assert _merge_types("integer", "float") == "float"


def test_merge_integer_string():
    assert _merge_types("integer", "string") == "string"


def test_merge_boolean_string():
    assert _merge_types("boolean", "string") == "string"


# ---------------------------------------------------------------------------
# infer_schema
# ---------------------------------------------------------------------------


def _rows(*dicts):
    return list(dicts)


def test_infer_schema_simple():
    rows = [
        {"age": "25", "name": "Alice"},
        {"age": "30", "name": "Bob"},
    ]
    schema = infer_schema(rows)
    assert schema["age"] == "integer"
    assert schema["name"] == "string"


def test_infer_schema_mixed_numeric():
    rows = [
        {"val": "1"},
        {"val": "2.5"},
    ]
    schema = infer_schema(rows)
    assert schema["val"] == "float"


def test_infer_schema_empty_rows():
    assert infer_schema([]) == {}


# ---------------------------------------------------------------------------
# enforce_schema
# ---------------------------------------------------------------------------


def test_enforce_schema_passes_valid_rows():
    schema = {"age": "integer", "name": "string"}
    rows = [{"age": "25", "name": "Alice"}, {"age": "30", "name": "Bob"}]
    result = list(enforce_schema(rows, schema))
    assert len(result) == 2


def test_enforce_schema_skips_invalid_rows():
    schema = {"age": "integer"}
    rows = [{"age": "25"}, {"age": "not_a_number"}, {"age": "40"}]
    result = list(enforce_schema(rows, schema))
    assert len(result) == 2
    assert all(r["age"] in ("25", "40") for r in result)


def test_enforce_schema_strict_raises():
    schema = {"age": "integer"}
    rows = [{"age": "bad"}]
    with pytest.raises(SchemaViolation) as exc_info:
        list(enforce_schema(rows, schema, strict=True))
    assert exc_info.value.column == "age"
    assert exc_info.value.expected_type == "integer"


def test_enforce_schema_missing_key_treated_as_empty_string():
    schema = {"age": "integer"}
    rows = [{"name": "Alice"}]  # 'age' key missing
    result = list(enforce_schema(rows, schema))
    # empty string is not a valid integer → row skipped
    assert result == []
