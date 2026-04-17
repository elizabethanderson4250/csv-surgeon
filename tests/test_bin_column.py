"""Tests for csv_surgeon.bin_column."""
import pytest
from csv_surgeon.bin_column import bin_fixed, bin_quantile


def make_rows(values):
    return [{"name": f"r{i}", "score": str(v)} for i, v in enumerate(values)]


# --- bin_fixed ---

def test_bin_fixed_basic_labels():
    rows = make_rows([5, 15, 25])
    result = list(bin_fixed(rows, "score", edges=[0, 10, 20, 30], labels=["low", "mid", "high"]))
    assert [r["score_bin"] for r in result] == ["low", "mid", "high"]


def test_bin_fixed_auto_labels():
    rows = make_rows([5])
    result = list(bin_fixed(rows, "score", edges=[0, 10]))
    assert result[0]["score_bin"] == "0-10"


def test_bin_fixed_custom_output_column():
    rows = make_rows([5])
    result = list(bin_fixed(rows, "score", edges=[0, 10], output_column="bucket"))
    assert "bucket" in result[0]
    assert "score_bin" not in result[0]


def test_bin_fixed_non_numeric_uses_default():
    rows = [{"score": "n/a"}]
    result = list(bin_fixed(rows, "score", edges=[0, 10], default="unknown"))
    assert result[0]["score_bin"] == "unknown"


def test_bin_fixed_out_of_range_uses_default():
    rows = make_rows([999])
    result = list(bin_fixed(rows, "score", edges=[0, 10], default="OOB"))
    assert result[0]["score_bin"] == "OOB"


def test_bin_fixed_boundary_included_in_last_bin():
    rows = make_rows([10])
    result = list(bin_fixed(rows, "score", edges=[0, 10], labels=["all"]))
    assert result[0]["score_bin"] == "all"


def test_bin_fixed_wrong_label_count_raises():
    with pytest.raises(ValueError, match="labels length"):
        list(bin_fixed(make_rows([1]), "score", edges=[0, 5, 10], labels=["only-one"]))


def test_bin_fixed_too_few_edges_raises():
    with pytest.raises(ValueError, match="edges must contain"):
        list(bin_fixed(make_rows([1]), "score", edges=[0]))


def test_bin_fixed_preserves_other_columns():
    rows = [{"name": "alice", "score": "7"}]
    result = list(bin_fixed(rows, "score", edges=[0, 10]))
    assert result[0]["name"] == "alice"


# --- bin_quantile ---

def test_bin_quantile_assigns_q_labels():
    rows = make_rows([1, 2, 3, 4])
    result = list(bin_quantile(rows, "score", n_quantiles=4))
    bins = [r["score_bin"] for r in result]
    assert all(b.startswith("Q") for b in bins)


def test_bin_quantile_count_matches_input():
    rows = make_rows(range(10))
    result = list(bin_quantile(rows, "score", n_quantiles=2))
    assert len(result) == 10


def test_bin_quantile_invalid_n_raises():
    with pytest.raises(ValueError):
        list(bin_quantile(make_rows([1, 2]), "score", n_quantiles=1))


def test_bin_quantile_non_numeric_default():
    rows = [{"score": "bad"}, {"score": "5"}]
    result = list(bin_quantile(rows, "score", n_quantiles=2, default="?"))
    assert result[0]["score_bin"] == "?"


def test_bin_quantile_custom_output_column():
    rows = make_rows([1, 2, 3, 4])
    result = list(bin_quantile(rows, "score", n_quantiles=2, output_column="tier"))
    assert "tier" in result[0]
