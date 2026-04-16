"""Tests for csv_surgeon/conditional.py"""

import pytest
from csv_surgeon.conditional import if_else, set_if, case, apply_conditional


def make_row(**kwargs):
    return {k: str(v) for k, v in kwargs.items()}


# ---------------------------------------------------------------------------
# if_else
# ---------------------------------------------------------------------------

def test_if_else_true_branch():
    row = make_row(status="active", label="")
    transform = if_else("label", lambda r: r["status"] == "active", "YES", "NO")
    result = transform(row)
    assert result["label"] == "YES"


def test_if_else_false_branch():
    row = make_row(status="inactive", label="")
    transform = if_else("label", lambda r: r["status"] == "active", "YES", "NO")
    result = transform(row)
    assert result["label"] == "NO"


def test_if_else_does_not_mutate_original():
    row = make_row(status="active", label="original")
    transform = if_else("label", lambda r: True, "NEW", "OTHER")
    transform(row)
    assert row["label"] == "original"


def test_if_else_creates_new_column():
    row = make_row(score="90")
    transform = if_else("grade", lambda r: int(r["score"]) >= 50, "pass", "fail")
    result = transform(row)
    assert result["grade"] == "pass"
    assert "grade" not in row


# ---------------------------------------------------------------------------
# set_if
# ---------------------------------------------------------------------------

def test_set_if_sets_when_condition_true():
    row = make_row(flag="0", note="")
    transform = set_if("note", lambda r: r["flag"] == "0", "zero")
    result = transform(row)
    assert result["note"] == "zero"


def test_set_if_leaves_unchanged_when_false():
    row = make_row(flag="1", note="keep")
    transform = set_if("note", lambda r: r["flag"] == "0", "zero")
    result = transform(row)
    assert result["note"] == "keep"


# ---------------------------------------------------------------------------
# case
# ---------------------------------------------------------------------------

def test_case_first_matching_wins():
    row = make_row(score="85")
    transform = case(
        "grade",
        [
            (lambda r: int(r["score"]) >= 90, "A"),
            (lambda r: int(r["score"]) >= 80, "B"),
            (lambda r: int(r["score"]) >= 70, "C"),
        ],
        default="F",
    )
    result = transform(row)
    assert result["grade"] == "B"


def test_case_default_used_when_no_match():
    row = make_row(score="40")
    transform = case(
        "grade",
        [(lambda r: int(r["score"]) >= 90, "A")],
        default="F",
    )
    result = transform(row)
    assert result["grade"] == "F"


def test_case_no_default_leaves_column_unchanged():
    row = make_row(score="40", grade="existing")
    transform = case(
        "grade",
        [(lambda r: int(r["score"]) >= 90, "A")],
    )
    result = transform(row)
    assert result["grade"] == "existing"


# ---------------------------------------------------------------------------
# apply_conditional
# ---------------------------------------------------------------------------

def test_apply_conditional_processes_all_rows():
    rows = [make_row(x=str(i)) for i in range(5)]
    transform = if_else("big", lambda r: int(r["x"]) >= 3, "yes", "no")
    results = list(apply_conditional(rows, transform))
    assert len(results) == 5
    assert results[0]["big"] == "no"
    assert results[4]["big"] == "yes"


def test_apply_conditional_is_lazy():
    """apply_conditional should return an iterator, not a list."""
    rows = [make_row(v="1")]
    transform = if_else("out", lambda r: True, "x", "y")
    result = apply_conditional(rows, transform)
    import types
    assert isinstance(result, types.GeneratorType)
