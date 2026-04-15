"""Integration tests for the compute CLI sub-commands."""
import csv
import io
import pytest
from csv_surgeon.cli_compute import run_compute


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,price,qty\napple,1.50,4\nbanana,0.75,10\ncherry,3.00,2\n")
    return str(p)


@pytest.fixture()
def output_path(tmp_path):
    return str(tmp_path / "out.csv")


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class _Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# --- expr ---

def test_expr_adds_column(sample_csv, output_path):
    args = _Args(
        input=sample_csv,
        output=output_path,
        compute_cmd="expr",
        name="total",
        expr="price * qty",
    )
    run_compute(args)
    rows = _read_csv(output_path)
    assert "total" in rows[0]


def test_expr_correct_values(sample_csv, output_path):
    args = _Args(
        input=sample_csv,
        output=output_path,
        compute_cmd="expr",
        name="total",
        expr="price * qty",
    )
    run_compute(args)
    rows = _read_csv(output_path)
    assert rows[0]["total"] == "6"
    assert rows[1]["total"] == "7.5"


def test_expr_preserves_row_count(sample_csv, output_path):
    args = _Args(
        input=sample_csv,
        output=output_path,
        compute_cmd="expr",
        name="total",
        expr="price * qty",
    )
    run_compute(args)
    rows = _read_csv(output_path)
    assert len(rows) == 3


# --- copy ---

def test_copy_creates_dest_column(sample_csv, output_path):
    args = _Args(
        input=sample_csv,
        output=output_path,
        compute_cmd="copy",
        source="name",
        dest="label",
    )
    run_compute(args)
    rows = _read_csv(output_path)
    assert "label" in rows[0]
    assert rows[0]["label"] == rows[0]["name"]


# --- drop ---

def test_drop_removes_column(sample_csv, output_path):
    args = _Args(
        input=sample_csv,
        output=output_path,
        compute_cmd="drop",
        columns=["price"],
    )
    run_compute(args)
    rows = _read_csv(output_path)
    assert "price" not in rows[0]


def test_drop_preserves_other_columns(sample_csv, output_path):
    args = _Args(
        input=sample_csv,
        output=output_path,
        compute_cmd="drop",
        columns=["price"],
    )
    run_compute(args)
    rows = _read_csv(output_path)
    assert "name" in rows[0]
    assert "qty" in rows[0]
