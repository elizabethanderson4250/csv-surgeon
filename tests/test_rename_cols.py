"""Tests for csv_surgeon.rename_cols."""
import pytest
from csv_surgeon.rename_cols import (
    rename_columns,
    reorder_columns,
    drop_columns,
    select_columns,
)


def make_rows():
    return [
        {"id": "1", "name": "Alice", "age": "30"},
        {"id": "2", "name": "Bob", "age": "25"},
        {"id": "3", "name": "Carol", "age": "35"},
    ]


# --- rename_columns ---

def test_rename_single_column():
    rows = list(rename_columns(make_rows(), {"name": "full_name"}))
    assert "full_name" in rows[0]
    assert "name" not in rows[0]
    assert rows[0]["full_name"] == "Alice"


def test_rename_multiple_columns():
    rows = list(rename_columns(make_rows(), {"id": "ID", "age": "years"}))
    assert rows[0]["ID"] == "1"
    assert rows[0]["years"] == "30"
    assert "id" not in rows[0]
    assert "age" not in rows[0]


def test_rename_unmapped_columns_unchanged():
    rows = list(rename_columns(make_rows(), {"name": "full_name"}))
    assert rows[0]["id"] == "1"
    assert rows[0]["age"] == "30"


def test_rename_nonexistent_column_ignored_by_default():
    rows = list(rename_columns(make_rows(), {"missing": "new"}))
    assert rows[0] == {"id": "1", "name": "Alice", "age": "30"}


def test_rename_strict_raises_on_missing_column():
    with pytest.raises(KeyError, match="missing"):
        list(rename_columns(make_rows(), {"missing": "new"}, strict=True))


def test_rename_preserves_row_count():
    rows = list(rename_columns(make_rows(), {"id": "pk"}))
    assert len(rows) == 3


# --- reorder_columns ---

def test_reorder_changes_key_order():
    rows = list(reorder_columns(make_rows(), ["age", "name", "id"]))
    assert list(rows[0].keys()) == ["age", "name", "id"]


def test_reorder_drops_unlisted_columns():
    rows = list(reorder_columns(make_rows(), ["name", "id"]))
    assert "age" not in rows[0]


def test_reorder_fills_missing_with_empty_string():
    rows = list(reorder_columns(make_rows(), ["id", "email"]))
    assert rows[0]["email"] == ""


def test_reorder_custom_fill_value():
    rows = list(reorder_columns(make_rows(), ["id", "email"], fill_value="N/A"))
    assert rows[0]["email"] == "N/A"


# --- drop_columns ---

def test_drop_removes_listed_columns():
    rows = list(drop_columns(make_rows(), ["age"]))
    assert "age" not in rows[0]
    assert "id" in rows[0]
    assert "name" in rows[0]


def test_drop_multiple_columns():
    rows = list(drop_columns(make_rows(), ["id", "age"]))
    assert list(rows[0].keys()) == ["name"]


def test_drop_nonexistent_column_is_safe():
    rows = list(drop_columns(make_rows(), ["nonexistent"]))
    assert rows[0] == {"id": "1", "name": "Alice", "age": "30"}


# --- select_columns ---

def test_select_keeps_only_listed_columns():
    rows = list(select_columns(make_rows(), ["name"]))
    assert list(rows[0].keys()) == ["name"]
    assert rows[0]["name"] == "Alice"


def test_select_preserves_order():
    rows = list(select_columns(make_rows(), ["age", "id"]))
    assert list(rows[0].keys()) == ["age", "id"]


def test_select_fills_missing_column():
    rows = list(select_columns(make_rows(), ["id", "score"]))
    assert rows[0]["score"] == ""
