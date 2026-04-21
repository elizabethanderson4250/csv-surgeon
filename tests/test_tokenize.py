"""Tests for csv_surgeon/tokenize.py."""
import pytest
from csv_surgeon.tokenize import tokenize_column, token_count, token_contains


def make_rows(*values, column="text"):
    return [{column: v} for v in values]


# ---------------------------------------------------------------------------
# tokenize_column
# ---------------------------------------------------------------------------

def test_tokenize_default_whitespace_split():
    rows = make_rows("hello world foo")
    result = list(tokenize_column(rows, "text"))
    assert result[0]["text_tokens"] == "hello|world|foo"


def test_tokenize_custom_separator():
    rows = make_rows("a,b,c")
    result = list(tokenize_column(rows, "text", sep=","))
    assert result[0]["text_tokens"] == "a|b|c"


def test_tokenize_regex_pattern():
    rows = make_rows("one1two2three")
    result = list(tokenize_column(rows, "text", pattern=r"\d"))
    assert result[0]["text_tokens"] == "one|two|three"


def test_tokenize_custom_output_column():
    rows = make_rows("x y")
    result = list(tokenize_column(rows, "text", output_column="toks"))
    assert "toks" in result[0]
    assert "text_tokens" not in result[0]


def test_tokenize_empty_value_yields_empty_tokens():
    rows = make_rows("")
    result = list(tokenize_column(rows, "text"))
    assert result[0]["text_tokens"] == ""


def test_tokenize_preserves_other_columns():
    rows = [{"text": "hello world", "id": "1"}]
    result = list(tokenize_column(rows, "text"))
    assert result[0]["id"] == "1"


# ---------------------------------------------------------------------------
# token_count
# ---------------------------------------------------------------------------

def test_token_count_basic():
    rows = make_rows("a b c d")
    result = list(token_count(rows, "text"))
    assert result[0]["text_token_count"] == "4"


def test_token_count_empty_string_is_zero():
    rows = make_rows("")
    result = list(token_count(rows, "text"))
    assert result[0]["text_token_count"] == "0"


def test_token_count_custom_sep():
    rows = make_rows("a;b;c")
    result = list(token_count(rows, "text", sep=";"))
    assert result[0]["text_token_count"] == "3"


def test_token_count_custom_output_column():
    rows = make_rows("x y")
    result = list(token_count(rows, "text", output_column="n"))
    assert "n" in result[0]


# ---------------------------------------------------------------------------
# token_contains
# ---------------------------------------------------------------------------

def test_token_contains_true():
    rows = make_rows("apple banana cherry")
    result = list(token_contains(rows, "text", "banana"))
    assert result[0]["text_has_banana"] == "True"


def test_token_contains_false():
    rows = make_rows("apple cherry")
    result = list(token_contains(rows, "text", "banana"))
    assert result[0]["text_has_banana"] == "False"


def test_token_contains_case_insensitive():
    rows = make_rows("Apple Banana")
    result = list(token_contains(rows, "text", "banana", case_sensitive=False))
    assert result[0]["text_has_banana"] == "True"


def test_token_contains_case_sensitive_mismatch():
    rows = make_rows("Apple Banana")
    result = list(token_contains(rows, "text", "banana", case_sensitive=True))
    assert result[0]["text_has_banana"] == "False"


def test_token_contains_custom_output_column():
    rows = make_rows("foo bar")
    result = list(token_contains(rows, "text", "foo", output_column="found"))
    assert "found" in result[0]
