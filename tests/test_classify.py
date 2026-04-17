import pytest
from csv_surgeon.classify import classify_by_map, classify_by_patterns, classify_by_ranges


def make_rows(data):
    return [dict(zip(["id", "value"], row)) for row in data]


# --- classify_by_map ---

def test_map_assigns_correct_label():
    rows = [{"id": "1", "color": "red"}]
    result = list(classify_by_map(rows, "color", {"red": "warm", "blue": "cool"}, "group"))
    assert result[0]["group"] == "warm"


def test_map_uses_default_for_unknown():
    rows = [{"id": "1", "color": "green"}]
    result = list(classify_by_map(rows, "color", {"red": "warm"}, "group", default="other"))
    assert result[0]["group"] == "other"


def test_map_case_insensitive():
    rows = [{"id": "1", "color": "RED"}]
    result = list(classify_by_map(rows, "color", {"red": "warm"}, "group", case_sensitive=False))
    assert result[0]["group"] == "warm"


def test_map_preserves_other_columns():
    rows = [{"id": "42", "color": "blue"}]
    result = list(classify_by_map(rows, "color", {"blue": "cool"}, "group"))
    assert result[0]["id"] == "42"


def test_map_missing_column_uses_default():
    rows = [{"id": "1"}]
    result = list(classify_by_map(rows, "color", {"red": "warm"}, "group", default="?"))
    assert result[0]["group"] == "?"


# --- classify_by_patterns ---

def test_patterns_first_match_wins():
    rows = [{"v": "hello world"}]
    patterns = [(r"hello", "greeting"), (r"world", "place")]
    result = list(classify_by_patterns(rows, "v", patterns, "tag"))
    assert result[0]["tag"] == "greeting"


def test_patterns_no_match_uses_default():
    rows = [{"v": "xyz"}]
    result = list(classify_by_patterns(rows, "v", [(r"^\d+$", "number")], "tag", default="unknown"))
    assert result[0]["tag"] == "unknown"


def test_patterns_case_insensitive_flag():
    import re
    rows = [{"v": "HELLO"}]
    result = list(classify_by_patterns(rows, "v", [(r"hello", "greeting")], "tag", flags=re.IGNORECASE))
    assert result[0]["tag"] == "greeting"


def test_patterns_does_not_mutate_original():
    row = {"v": "abc"}
    list(classify_by_patterns([row], "v", [(r"abc", "match")], "tag"))
    assert "tag" not in row


# --- classify_by_ranges ---

def test_ranges_assigns_correct_label():
    rows = [{"score": "75"}]
    ranges = [(0, 59, "fail"), (60, 79, "pass"), (80, 100, "distinction")]
    result = list(classify_by_ranges(rows, "score", ranges, "grade"))
    assert result[0]["grade"] == "pass"


def test_ranges_boundary_inclusive():
    rows = [{"score": "60"}, {"score": "79"}]
    ranges = [(60, 79, "pass")]
    results = list(classify_by_ranges(rows, "score", ranges, "grade"))
    assert all(r["grade"] == "pass" for r in results)


def test_ranges_non_numeric_uses_default():
    rows = [{"score": "n/a"}]
    result = list(classify_by_ranges(rows, "score", [(0, 100, "ok")], "grade", default="?"))
    assert result[0]["grade"] == "?"


def test_ranges_no_match_uses_default():
    rows = [{"score": "150"}]
    result = list(classify_by_ranges(rows, "score", [(0, 100, "ok")], "grade", default="out"))
    assert result[0]["grade"] == "out"
