"""Tests for csv_surgeon/lookup.py."""
import pytest
from csv_surgeon.lookup import lookup_enrich, lookup_filter, _build_lookup


def make_primary():
    return [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Carol"},
    ]


def make_ref():
    return [
        {"user_id": "1", "dept": "Engineering"},
        {"user_id": "2", "dept": "Marketing"},
    ]


def test_build_lookup_basic():
    mapping = _build_lookup(make_ref(), "user_id", "dept")
    assert mapping == {"1": "Engineering", "2": "Marketing"}


def test_build_lookup_empty():
    assert _build_lookup([], "k", "v") == {}


def test_enrich_adds_column():
    result = list(lookup_enrich(make_primary(), make_ref(), "id", "user_id", "dept"))
    assert "dept" in result[0]


def test_enrich_correct_values():
    result = list(lookup_enrich(make_primary(), make_ref(), "id", "user_id", "dept"))
    assert result[0]["dept"] == "Engineering"
    assert result[1]["dept"] == "Marketing"


def test_enrich_default_for_missing():
    result = list(lookup_enrich(make_primary(), make_ref(), "id", "user_id", "dept", default="N/A"))
    assert result[2]["dept"] == "N/A"


def test_enrich_custom_dest_col():
    result = list(lookup_enrich(make_primary(), make_ref(), "id", "user_id", "dept", dest_col="department"))
    assert "department" in result[0]
    assert "dept" not in result[0]


def test_enrich_does_not_mutate_original():
    rows = make_primary()
    _ = list(lookup_enrich(rows, make_ref(), "id", "user_id", "dept"))
    assert "dept" not in rows[0]


def test_filter_keeps_matching():
    result = list(lookup_filter(make_primary(), make_ref(), "id", "user_id"))
    assert len(result) == 2
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"


def test_filter_exclude_removes_matching():
    result = list(lookup_filter(make_primary(), make_ref(), "id", "user_id", exclude=True))
    assert len(result) == 1
    assert result[0]["id"] == "3"


def test_filter_empty_ref_keeps_nothing():
    result = list(lookup_filter(make_primary(), [], "id", "user_id"))
    assert result == []


def test_filter_empty_ref_exclude_keeps_all():
    result = list(lookup_filter(make_primary(), [], "id", "user_id", exclude=True))
    assert len(result) == 3
