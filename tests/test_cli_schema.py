"""Integration tests for the schema-infer and schema-enforce CLI sub-commands."""
from __future__ import annotations

import json
import os
import textwrap

import pytest

from csv_surgeon.cli_schema import run_schema_enforce, run_schema_infer


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(
        textwrap.dedent("""\
        name,age,score
        Alice,30,9.5
        Bob,25,8.0
        Carol,bad_age,7.5
        """)
    )
    return str(p)


@pytest.fixture()
def schema_path(tmp_path):
    return str(tmp_path / "schema.json")


@pytest.fixture()
def output_path(tmp_path):
    return str(tmp_path / "out.csv")


class _Args:
    """Simple namespace replacement."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# ---------------------------------------------------------------------------
# schema-infer
# ---------------------------------------------------------------------------


def test_schema_infer_writes_json(sample_csv, schema_path):
    args = _Args(input=sample_csv, output=schema_path)
    run_schema_infer(args)
    assert os.path.exists(schema_path)
    with open(schema_path) as fh:
        schema = json.load(fh)
    assert "name" in schema
    assert "age" in schema
    assert "score" in schema


def test_schema_infer_correct_types(sample_csv, schema_path):
    args = _Args(input=sample_csv, output=schema_path)
    run_schema_infer(args)
    with open(schema_path) as fh:
        schema = json.load(fh)
    # 'age' column has one bad value → falls back to string
    assert schema["age"] == "string"
    assert schema["score"] == "float"
    assert schema["name"] == "string"


# ---------------------------------------------------------------------------
# schema-enforce
# ---------------------------------------------------------------------------


def test_schema_enforce_filters_bad_rows(sample_csv, schema_path, output_path):
    # Build a strict integer schema for 'age'
    explicit_schema = {"name": "string", "age": "integer", "score": "float"}
    with open(schema_path, "w") as fh:
        json.dump(explicit_schema, fh)

    args = _Args(input=sample_csv, schema=schema_path, output=output_path, strict=False)
    run_schema_enforce(args)

    import csv
    with open(output_path, newline="") as fh:
        rows = list(csv.DictReader(fh))

    # Carol has bad_age → should be filtered
    assert len(rows) == 2
    assert all(r["name"] in ("Alice", "Bob") for r in rows)


def test_schema_enforce_output_has_header(sample_csv, schema_path, output_path):
    explicit_schema = {"name": "string", "age": "integer", "score": "float"}
    with open(schema_path, "w") as fh:
        json.dump(explicit_schema, fh)

    args = _Args(input=sample_csv, schema=schema_path, output=output_path, strict=False)
    run_schema_enforce(args)

    with open(output_path) as fh:
        first_line = fh.readline().strip()
    assert "name" in first_line
    assert "age" in first_line
