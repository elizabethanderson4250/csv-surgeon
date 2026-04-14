"""Tests for csv_surgeon/encode.py"""

import base64
import hashlib
import urllib.parse

import pytest

from csv_surgeon.encode import (
    to_base64,
    from_base64,
    url_encode,
    url_decode,
    hash_column,
    encode_rows,
)


def make_row(**kwargs):
    return dict(kwargs)


# --- to_base64 ---

def test_to_base64_encodes_value():
    row = make_row(email="user@example.com")
    result = to_base64("email")(row)
    expected = base64.b64encode(b"user@example.com").decode()
    assert result["email"] == expected


def test_to_base64_missing_column_unchanged():
    row = make_row(name="Alice")
    result = to_base64("email")(row)
    assert result == {"name": "Alice"}


# --- from_base64 ---

def test_from_base64_decodes_value():
    encoded = base64.b64encode(b"hello world").decode()
    row = make_row(data=encoded)
    result = from_base64("data")(row)
    assert result["data"] == "hello world"


def test_from_base64_invalid_returns_original():
    row = make_row(data="not-valid-base64!!!")
    result = from_base64("data")(row)
    assert result["data"] == "not-valid-base64!!!"


# --- url_encode / url_decode ---

def test_url_encode_encodes_special_chars():
    row = make_row(query="hello world & more")
    result = url_encode("query")(row)
    assert result["query"] == urllib.parse.quote("hello world & more", safe="")


def test_url_decode_decodes_value():
    row = make_row(query="hello%20world%20%26%20more")
    result = url_decode("query")(row)
    assert result["query"] == "hello world & more"


def test_url_encode_missing_column_unchanged():
    row = make_row(name="Bob")
    result = url_encode("query")(row)
    assert result == {"name": "Bob"}


# --- hash_column ---

def test_hash_column_sha256():
    row = make_row(password="secret")
    result = hash_column("password", algorithm="sha256")(row)
    expected = hashlib.sha256(b"secret").hexdigest()
    assert result["password"] == expected


def test_hash_column_md5():
    row = make_row(token="abc")
    result = hash_column("token", algorithm="md5")(row)
    expected = hashlib.md5(b"abc").hexdigest()
    assert result["token"] == expected


def test_hash_column_truncate():
    row = make_row(id="value")
    result = hash_column("id", algorithm="sha256", truncate=8)(row)
    assert len(result["id"]) == 8


def test_hash_column_missing_column_unchanged():
    row = make_row(name="Carol")
    result = hash_column("password")(row)
    assert result == {"name": "Carol"}


# --- encode_rows ---

def test_encode_rows_applies_multiple_transforms():
    rows = [
        {"name": "alice", "token": "abc"},
        {"name": "bob", "token": "def"},
    ]
    transforms = [
        to_base64("token"),
    ]
    results = list(encode_rows(rows, transforms))
    assert results[0]["token"] == base64.b64encode(b"abc").decode()
    assert results[1]["token"] == base64.b64encode(b"def").decode()
    assert results[0]["name"] == "alice"


def test_encode_rows_empty_transforms_returns_unchanged():
    rows = [{"a": "1"}, {"a": "2"}]
    results = list(encode_rows(rows, []))
    assert results == [{"a": "1"}, {"a": "2"}]
