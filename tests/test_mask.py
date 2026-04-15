"""Unit tests for csv_surgeon/mask.py"""

import pytest
from csv_surgeon.mask import redact, mask_chars, mask_regex, truncate_mask, apply_masks


def make_row(**kwargs):
    return dict(kwargs)


# --- redact ---

def test_redact_replaces_value():
    fn = redact("secret")
    row = make_row(secret="mysecret")
    assert fn(row)["secret"] == "***"


def test_redact_custom_replacement():
    fn = redact("secret", replacement="[REDACTED]")
    row = make_row(secret="value")
    assert fn(row)["secret"] == "[REDACTED]"


def test_redact_empty_value_unchanged():
    fn = redact("secret")
    row = make_row(secret="")
    assert fn(row)["secret"] == ""


def test_redact_missing_column_unchanged():
    fn = redact("secret")
    row = make_row(other="value")
    assert "secret" not in fn(row)
    assert fn(row)["other"] == "value"


# --- mask_chars ---

def test_mask_chars_full():
    fn = mask_chars("card")
    row = make_row(card="1234567890")
    assert fn(row)["card"] == "**********"


def test_mask_chars_keep_last():
    fn = mask_chars("card", keep_last=4)
    row = make_row(card="1234567890")
    assert fn(row)["card"] == "******7890"


def test_mask_chars_empty_value():
    fn = mask_chars("card", keep_last=4)
    row = make_row(card="")
    assert fn(row)["card"] == ""


def test_mask_chars_keep_last_exceeds_length():
    fn = mask_chars("card", keep_last=20)
    row = make_row(card="1234")
    assert fn(row)["card"] == "1234"


# --- mask_regex ---

def test_mask_regex_replaces_match():
    fn = mask_regex("email", pattern=r"[^@]+")
    row = make_row(email="user@example.com")
    assert fn(row)["email"] == "***@***.***"


def test_mask_regex_no_match_unchanged():
    fn = mask_regex("field", pattern=r"\d+")
    row = make_row(field="no digits here")
    assert fn(row)["field"] == "no digits here"


def test_mask_regex_custom_replacement():
    fn = mask_regex("ssn", pattern=r"\d", replacement="X")
    row = make_row(ssn="123-45-6789")
    assert fn(row)["ssn"] == "XXX-XX-XXXX"


# --- truncate_mask ---

def test_truncate_mask_basic():
    fn = truncate_mask("name", visible_start=2, visible_end=2)
    row = make_row(name="JohnDoe")
    assert fn(row)["name"] == "Jo***oe"


def test_truncate_mask_short_value_unchanged():
    fn = truncate_mask("name", visible_start=3, visible_end=3)
    row = make_row(name="Jo")
    assert fn(row)["name"] == "Jo"


# --- apply_masks ---

def test_apply_masks_chains_transforms():
    rows = [
        {"name": "Alice", "card": "1234567890"},
        {"name": "Bob", "card": "0987654321"},
    ]
    masks = [
        redact("name"),
        mask_chars("card", keep_last=4),
    ]
    result = list(apply_masks(rows, masks))
    assert result[0]["name"] == "***"
    assert result[0]["card"] == "******7890"
    assert result[1]["name"] == "***"
    assert result[1]["card"] == "******4321"


def test_apply_masks_empty_list_is_noop():
    rows = [{"name": "Alice"}]
    result = list(apply_masks(rows, []))
    assert result == [{"name": "Alice"}]
