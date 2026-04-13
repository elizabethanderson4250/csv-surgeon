"""Tests for csv_surgeon.pivot (pivot and unpivot)."""
import pytest
from csv_surgeon.pivot import pivot, unpivot


def make_long_rows():
    return [
        {"name": "Alice", "subject": "math", "score": "90"},
        {"name": "Alice", "subject": "english", "score": "85"},
        {"name": "Bob", "subject": "math", "score": "78"},
        {"name": "Bob", "subject": "english", "score": "92"},
    ]


def make_wide_rows():
    return [
        {"name": "Alice", "math": "90", "english": "85"},
        {"name": "Bob", "math": "78", "english": "92"},
    ]


# --- pivot tests ---

def test_pivot_produces_correct_columns():
    result = pivot(make_long_rows(), "name", "subject", "score")
    cols = set(result[0].keys())
    assert "name" in cols
    assert "math" in cols
    assert "english" in cols


def test_pivot_correct_row_count():
    result = pivot(make_long_rows(), "name", "subject", "score")
    assert len(result) == 2


def test_pivot_values_correct():
    result = pivot(make_long_rows(), "name", "subject", "score")
    by_name = {r["name"]: r for r in result}
    assert by_name["Alice"]["math"] == "90"
    assert by_name["Bob"]["english"] == "92"


def test_pivot_agg_sum():
    rows = [
        {"dept": "eng", "month": "jan", "sales": "100"},
        {"dept": "eng", "month": "jan", "sales": "50"},
    ]
    result = pivot(rows, "dept", "month", "sales", agg="sum")
    assert result[0]["jan"] == "150.0"


def test_pivot_agg_count():
    rows = [
        {"dept": "eng", "month": "jan", "sales": "100"},
        {"dept": "eng", "month": "jan", "sales": "50"},
    ]
    result = pivot(rows, "dept", "month", "sales", agg="count")
    assert result[0]["jan"] == "2"


def test_pivot_agg_last():
    rows = [
        {"dept": "eng", "month": "jan", "sales": "100"},
        {"dept": "eng", "month": "jan", "sales": "50"},
    ]
    result = pivot(rows, "dept", "month", "sales", agg="last")
    assert result[0]["jan"] == "50"


def test_pivot_empty_input():
    result = pivot([], "name", "subject", "score")
    assert result == []


# --- unpivot tests ---

def test_unpivot_row_count():
    result = list(unpivot(make_wide_rows(), id_cols=["name"]))
    # 2 rows × 2 value columns = 4
    assert len(result) == 4


def test_unpivot_column_names():
    result = list(unpivot(make_wide_rows(), id_cols=["name"]))
    assert "name" in result[0]
    assert "variable" in result[0]
    assert "value" in result[0]


def test_unpivot_custom_col_names():
    result = list(
        unpivot(make_wide_rows(), id_cols=["name"], variable_col="metric", value_col="score")
    )
    assert "metric" in result[0]
    assert "score" in result[0]


def test_unpivot_values_preserved():
    result = list(unpivot(make_wide_rows(), id_cols=["name"]))
    alice_math = next(r for r in result if r["name"] == "Alice" and r["variable"] == "math")
    assert alice_math["value"] == "90"


def test_unpivot_explicit_columns():
    result = list(unpivot(make_wide_rows(), id_cols=["name"], columns=["math"]))
    assert len(result) == 2
    assert all(r["variable"] == "math" for r in result)


def test_unpivot_empty_input():
    result = list(unpivot([], id_cols=["name"]))
    assert result == []
