"""Tests for csv_surgeon.frequency."""
import pytest
from csv_surgeon.frequency import value_frequency, cumulative_frequency


def make_rows(data: list[tuple[str, str]]) -> list[dict]:
    return [{"name": n, "city": c} for n, c in data]


SAMPLE = [
    ("alice", "London"),
    ("bob", "Paris"),
    ("carol", "London"),
    ("dave", "Berlin"),
    ("eve", "London"),
    ("frank", "Paris"),
]


# ---------------------------------------------------------------------------
# value_frequency
# ---------------------------------------------------------------------------

def test_frequency_count_values():
    rows = make_rows(SAMPLE)
    result = value_frequency(rows, "city")
    counts = {r["value"]: int(r["count"]) for r in result}
    assert counts["London"] == 3
    assert counts["Paris"] == 2
    assert counts["Berlin"] == 1


def test_frequency_default_sorted_by_count_desc():
    rows = make_rows(SAMPLE)
    result = value_frequency(rows, "city")
    counts = [int(r["count"]) for r in result]
    assert counts == sorted(counts, reverse=True)


def test_frequency_sort_by_value():
    rows = make_rows(SAMPLE)
    result = value_frequency(rows, "city", sort_by="value")
    values = [r["value"] for r in result]
    assert values == sorted(values)


def test_frequency_normalize_adds_percent():
    rows = make_rows(SAMPLE)
    result = value_frequency(rows, "city", normalize=True)
    for r in result:
        assert "percent" in r
    total_pct = sum(float(r["percent"]) for r in result)
    assert abs(total_pct - 100.0) < 0.01


def test_frequency_no_normalize_omits_percent():
    rows = make_rows(SAMPLE)
    result = value_frequency(rows, "city", normalize=False)
    for r in result:
        assert "percent" not in r


def test_frequency_top_n_limits_rows():
    rows = make_rows(SAMPLE)
    result = value_frequency(rows, "city", top_n=2)
    assert len(result) == 2
    # top-2 should be London and Paris
    values = {r["value"] for r in result}
    assert values == {"London", "Paris"}


def test_frequency_missing_column_counts_empty_string():
    rows = [{"name": "alice"}, {"name": "bob"}]
    result = value_frequency(rows, "city")
    assert len(result) == 1
    assert result[0]["value"] == ""
    assert result[0]["count"] == "2"


def test_frequency_empty_rows_returns_empty_list():
    result = value_frequency([], "city")
    assert result == []


# ---------------------------------------------------------------------------
# cumulative_frequency
# ---------------------------------------------------------------------------

def test_cumulative_count_is_running_total():
    rows = make_rows(SAMPLE)
    freq = value_frequency(rows, "city", normalize=True)
    cumulative_frequency(freq)
    cumulative_counts = [int(r["cumulative_count"]) for r in freq]
    assert cumulative_counts[-1] == len(SAMPLE)
    for i in range(1, len(cumulative_counts)):
        assert cumulative_counts[i] >= cumulative_counts[i - 1]


def test_cumulative_percent_reaches_100():
    rows = make_rows(SAMPLE)
    freq = value_frequency(rows, "city", normalize=True)
    cumulative_frequency(freq)
    last_pct = float(freq[-1]["cumulative_percent"])
    assert abs(last_pct - 100.0) < 0.01


def test_cumulative_without_percent_skips_cumulative_percent():
    rows = make_rows(SAMPLE)
    freq = value_frequency(rows, "city", normalize=False)
    cumulative_frequency(freq)
    for r in freq:
        assert "cumulative_percent" not in r
        assert "cumulative_count" in r
