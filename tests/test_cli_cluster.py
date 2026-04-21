"""Integration tests for the cluster CLI sub-command."""
from __future__ import annotations

import csv
import io
import textwrap

import pytest

from csv_surgeon.cli_cluster import run_cluster


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "input.csv"
    p.write_text(
        textwrap.dedent(
            """\
            city,population
            London,9000000
            london,9000000
            LONDON,9000000
            Paris,2000000
            Berlin,3500000
            """
        )
    )
    return str(p)


@pytest.fixture()
def output_path(tmp_path):
    return str(tmp_path / "output.csv")


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _make_args(input_path, output_path, column="city", output_column="cluster_key", method="exact"):
    return _Args(
        input=input_path,
        output=output_path,
        column=column,
        output_column=output_column,
        method=method,
    )


def test_cluster_creates_output_file(sample_csv, output_path):
    run_cluster(_make_args(sample_csv, output_path))
    rows = _read_csv(output_path)
    assert len(rows) == 5


def test_cluster_exact_groups_case_variants(sample_csv, output_path):
    run_cluster(_make_args(sample_csv, output_path))
    rows = _read_csv(output_path)
    london_keys = {r["cluster_key"] for r in rows if "london" in r["city"].lower()}
    assert len(london_keys) == 1


def test_cluster_output_column_present(sample_csv, output_path):
    run_cluster(_make_args(sample_csv, output_path))
    rows = _read_csv(output_path)
    assert "cluster_key" in rows[0]


def test_cluster_custom_output_column(sample_csv, output_path):
    run_cluster(_make_args(sample_csv, output_path, output_column="grp"))
    rows = _read_csv(output_path)
    assert "grp" in rows[0]


def test_cluster_soundex_method(sample_csv, output_path):
    run_cluster(_make_args(sample_csv, output_path, method="soundex"))
    rows = _read_csv(output_path)
    assert "cluster_key" in rows[0]
    # All three London variants should share the same soundex key
    london_keys = {r["cluster_key"] for r in rows if "london" in r["city"].lower()}
    assert len(london_keys) == 1


def test_cluster_preserves_original_columns(sample_csv, output_path):
    run_cluster(_make_args(sample_csv, output_path))
    rows = _read_csv(output_path)
    assert "city" in rows[0]
    assert "population" in rows[0]
