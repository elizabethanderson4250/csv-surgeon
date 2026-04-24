"""Integration tests for the reshape CLI sub-commands."""
import csv
import io
import pytest
from pathlib import Path
from csv_surgeon.cli_reshape import run_reshape


@pytest.fixture()
def long_csv(tmp_path):
    p = tmp_path / "long.csv"
    p.write_text("id,metric,val\n1,height,180\n1,weight,75\n2,height,165\n2,weight,60\n")
    return str(p)


@pytest.fixture()
def wide_csv(tmp_path):
    p = tmp_path / "wide.csv"
    p.write_text("id,height,weight\n1,180,75\n2,165,60\n")
    return str(p)


@pytest.fixture()
def output_path(tmp_path):
    return str(tmp_path / "out.csv")


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


# --- widen ---

def test_widen_creates_file(long_csv, output_path):
    args = _Args(reshape_cmd="widen", index="id", key="metric", value="val",
                 input=long_csv, output=output_path)
    run_reshape(args)
    assert Path(output_path).exists()


def test_widen_row_count(long_csv, output_path):
    args = _Args(reshape_cmd="widen", index="id", key="metric", value="val",
                 input=long_csv, output=output_path)
    run_reshape(args)
    rows = _read_csv(output_path)
    assert len(rows) == 2


def test_widen_columns_correct(long_csv, output_path):
    args = _Args(reshape_cmd="widen", index="id", key="metric", value="val",
                 input=long_csv, output=output_path)
    run_reshape(args)
    rows = _read_csv(output_path)
    assert "height" in rows[0] and "weight" in rows[0]


# --- narrow ---

def test_narrow_row_count(wide_csv, output_path):
    args = _Args(reshape_cmd="narrow", index="id", columns="height,weight",
                 key_col="key", value_col="value", input=wide_csv, output=output_path)
    run_reshape(args)
    rows = _read_csv(output_path)
    assert len(rows) == 4


def test_narrow_key_column_present(wide_csv, output_path):
    args = _Args(reshape_cmd="narrow", index="id", columns="height,weight",
                 key_col="key", value_col="value", input=wide_csv, output=output_path)
    run_reshape(args)
    rows = _read_csv(output_path)
    assert all("key" in r for r in rows)


# --- stack ---

def test_stack_row_count(wide_csv, output_path):
    args = _Args(reshape_cmd="stack", columns="height,weight",
                 output_col="value", label_col="source",
                 input=wide_csv, output=output_path)
    run_reshape(args)
    rows = _read_csv(output_path)
    assert len(rows) == 4


# --- unstack ---

def test_unstack_row_count(long_csv, output_path):
    args = _Args(reshape_cmd="unstack", index="id",
                 label_col="metric", value_col="val",
                 input=long_csv, output=output_path)
    run_reshape(args)
    rows = _read_csv(output_path)
    assert len(rows) == 2


def test_unstack_columns_correct(long_csv, output_path):
    args = _Args(reshape_cmd="unstack", index="id",
                 label_col="metric", value_col="val",
                 input=long_csv, output=output_path)
    run_reshape(args)
    rows = _read_csv(output_path)
    assert "height" in rows[0] and "weight" in rows[0]
