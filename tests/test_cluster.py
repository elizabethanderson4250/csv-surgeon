"""Tests for csv_surgeon.cluster."""
from __future__ import annotations

import pytest

from csv_surgeon.cluster import (
    _fingerprint_soundex,
    cluster_by_soundex,
    cluster_by_value,
    collect_clusters,
)


def make_rows(*cities: str) -> list[dict]:
    return [{"city": c, "pop": "100"} for c in cities]


# ---------------------------------------------------------------------------
# _fingerprint_soundex
# ---------------------------------------------------------------------------

def test_soundex_same_for_similar_spellings():
    assert _fingerprint_soundex("Robert") == _fingerprint_soundex("Rupert")


def test_soundex_different_for_different_names():
    assert _fingerprint_soundex("Smith") != _fingerprint_soundex("Jones")


def test_soundex_empty_string():
    assert _fingerprint_soundex("") == ""


def test_soundex_single_char():
    result = _fingerprint_soundex("A")
    assert result == "A000"


# ---------------------------------------------------------------------------
# cluster_by_value
# ---------------------------------------------------------------------------

def test_cluster_by_value_adds_column():
    rows = make_rows("London", "Paris")
    result = list(cluster_by_value(rows, "city"))
    assert "cluster_key" in result[0]


def test_cluster_by_value_exact_match():
    rows = make_rows("London", "london", "LONDON")
    result = list(cluster_by_value(rows, "city"))
    keys = {r["cluster_key"] for r in result}
    assert len(keys) == 1, "All case variants should share one cluster key"


def test_cluster_by_value_custom_output_column():
    rows = make_rows("Berlin")
    result = list(cluster_by_value(rows, "city", output_column="grp"))
    assert "grp" in result[0]


def test_cluster_by_value_custom_key_func():
    rows = make_rows("hello world", "hello-world")
    result = list(
        cluster_by_value(rows, "city", key_func=lambda v: v.replace("-", " ").lower())
    )
    assert result[0]["cluster_key"] == result[1]["cluster_key"]


def test_cluster_by_value_missing_column_uses_empty():
    rows = [{"name": "Alice"}]
    result = list(cluster_by_value(rows, "city"))
    assert result[0]["cluster_key"] == ""


def test_cluster_by_value_does_not_mutate_original():
    original = {"city": "Rome", "pop": "3M"}
    rows = [original]
    list(cluster_by_value(rows, "city"))
    assert "cluster_key" not in original


# ---------------------------------------------------------------------------
# cluster_by_soundex
# ---------------------------------------------------------------------------

def test_cluster_by_soundex_adds_column():
    rows = make_rows("Smith", "Smyth")
    result = list(cluster_by_soundex(rows, "city"))
    assert "cluster_key" in result[0]


def test_cluster_by_soundex_groups_similar():
    rows = make_rows("Robert", "Rupert")
    result = list(cluster_by_soundex(rows, "city"))
    assert result[0]["cluster_key"] == result[1]["cluster_key"]


# ---------------------------------------------------------------------------
# collect_clusters
# ---------------------------------------------------------------------------

def test_collect_clusters_groups_correctly():
    rows = [
        {"city": "London", "cluster_key": "london"},
        {"city": "london", "cluster_key": "london"},
        {"city": "Paris", "cluster_key": "paris"},
    ]
    buckets = collect_clusters(rows, "cluster_key")
    assert len(buckets["london"]) == 2
    assert len(buckets["paris"]) == 1


def test_collect_clusters_empty_input():
    assert collect_clusters([], "cluster_key") == {}
