"""Column encoding/decoding utilities: base64, url-encoding, hash."""

import base64
import hashlib
import urllib.parse
from typing import Callable, Iterable, Iterator


def _encoder(func: Callable[[str], str]):
    """Wrap an encoding function so it operates on a named column."""
    def _transform(col: str):
        def apply(row: dict) -> dict:
            if col in row:
                row = dict(row)
                row[col] = func(row[col])
            return row
        return apply
    return _transform


@_encoder
def to_base64(value: str) -> str:
    """Encode a column value to base64."""
    return base64.b64encode(value.encode()).decode()


@_encoder
def from_base64(value: str) -> str:
    """Decode a column value from base64."""
    try:
        return base64.b64decode(value.encode()).decode()
    except Exception:
        return value


@_encoder
def url_encode(value: str) -> str:
    """URL-encode a column value."""
    return urllib.parse.quote(value, safe="")


@_encoder
def url_decode(value: str) -> str:
    """URL-decode a column value."""
    return urllib.parse.unquote(value)


def hash_column(col: str, algorithm: str = "sha256", truncate: int = 0):
    """Hash a column value using the given algorithm (e.g. md5, sha256).

    Args:
        col: Column name to hash.
        algorithm: Hash algorithm supported by hashlib.
        truncate: If > 0, truncate the hex digest to this many characters.
    """
    def apply(row: dict) -> dict:
        if col in row:
            row = dict(row)
            digest = hashlib.new(algorithm, row[col].encode()).hexdigest()
            row[col] = digest[:truncate] if truncate > 0 else digest
        return row
    return apply


def encode_rows(
    rows: Iterable[dict],
    transforms: list,
) -> Iterator[dict]:
    """Apply a list of encoding transforms to each row."""
    for row in rows:
        for transform in transforms:
            row = transform(row)
        yield row
