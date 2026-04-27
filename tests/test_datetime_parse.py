"""Tests for csv_surgeon.datetime_parse."""

import pytest
from csv_surgeon.datetime_parse import parse_date, format_date, extract_part, apply


def make_row(date_val="2024-03-15"):
    return {"id": "1", "date": date_val, "name": "Alice"}


def test_parse_date_normalizes_to_iso():
    t = parse_date("date", fmt="%d/%m/%Y")
    row = make_row("15/03/2024")
    assert t(row)["date"] == "2024-03-15"


def test_parse_date_already_iso_passthrough():
    t = parse_date("date", fmt="%Y-%m-%d")
    row = make_row("2024-03-15")
    assert t(row)["date"] == "2024-03-15"


def test_parse_date_invalid_value_unchanged():
    t = parse_date("date", fmt="%Y-%m-%d")
    row = make_row("not-a-date")
    assert t(row)["date"] == "not-a-date"


def test_parse_date_missing_column_unchanged():
    t = parse_date("missing", fmt="%Y-%m-%d")
    row = make_row()
    assert t(row) == row


def test_format_date_reformats_correctly():
    t = format_date("date", in_fmt="%Y-%m-%d", out_fmt="%d/%m/%Y")
    row = make_row("2024-03-15")
    assert t(row)["date"] == "15/03/2024"


def test_format_date_invalid_unchanged():
    t = format_date("date", in_fmt="%Y-%m-%d", out_fmt="%d/%m/%Y")
    row = make_row("bad")
    assert t(row)["date"] == "bad"


def test_format_date_missing_column_unchanged():
    t = format_date("missing", in_fmt="%Y-%m-%d", out_fmt="%d/%m/%Y")
    row = make_row()
    assert t(row) == row


def test_extract_part_year():
    t = extract_part("date", "year")
    row = make_row("2024-03-15")
    assert t(row)["date_year"] == "2024"


def test_extract_part_month():
    t = extract_part("date", "month")
    row = make_row("2024-03-15")
    assert t(row)["date_month"] == "3"


def test_extract_part_weekday():
    t = extract_part("date", "weekday")
    row = make_row("2024-03-15")
    assert t(row)["date_weekday"] == "Friday"


def test_extract_part_custom_out_col():
    t = extract_part("date", "year", out_col="yr")
    row = make_row("2024-03-15")
    result = t(row)
    assert "yr" in result
    assert result["yr"] == "2024"


def test_extract_part_invalid_date_sets_empty():
    t = extract_part("date", "year")
    row = make_row("bad")
    assert t(row)["date_year"] == ""


def test_extract_part_unknown_part_raises():
    with pytest.raises(ValueError, match="Unknown date part"):
        extract_part("date", "century")


def test_apply_chains_transforms():
    rows = [make_row("15/03/2024"), make_row("01/01/2023")]
    t1 = parse_date("date", fmt="%d/%m/%Y")
    t2 = extract_part("date", "year")
    result = list(apply(iter(rows), t1, t2))
    assert result[0]["date"] == "2024-03-15"
    assert result[0]["date_year"] == "2024"
    assert result[1]["date_year"] == "2023"


def test_parse_date_does_not_mutate_original():
    t = parse_date("date", fmt="%d/%m/%Y")
    row = make_row("15/03/2024")
    original = dict(row)
    t(row)
    assert row == original


def test_format_date_does_not_mutate_original():
    t = format_date("date", in_fmt="%Y-%m-%d", out_fmt="%d/%m/%Y")
    row = make_row("2024-03-15")
    original = dict(row)
    t(row)
    assert row == original
