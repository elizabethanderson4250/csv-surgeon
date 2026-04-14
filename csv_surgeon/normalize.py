"""Column normalization transforms for CSV data."""

import re
import unicodedata


def _normalizer(func):
    """Decorator that wraps a normalization function to operate on a named column."""
    def _transform(col, **kwargs):
        def apply(row):
            row = dict(row)
            if col in row:
                row[col] = func(row[col], **kwargs)
            return row
        return apply
    _transform.__name__ = func.__name__
    return _transform


@_normalizer
def to_slug(value, separator="-"):
    """Convert a string to a URL-friendly slug."""
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", separator, value)
    value = re.sub(r"-{2,}", separator, value)
    return value.strip(separator)


@_normalizer
def pad_left(value, width, fillchar="0"):
    """Left-pad a string to a given width."""
    return str(value).rjust(int(width), fillchar[0])


@_normalizer
def pad_right(value, width, fillchar=" "):
    """Right-pad a string to a given width."""
    return str(value).ljust(int(width), fillchar[0])


@_normalizer
def truncate(value, max_length, ellipsis=False):
    """Truncate a string to max_length characters."""
    max_length = int(max_length)
    if len(value) <= max_length:
        return value
    if ellipsis:
        return value[: max(0, max_length - 3)] + "..."
    return value[:max_length]


@_normalizer
def normalize_whitespace(value):
    """Collapse multiple whitespace characters into a single space and strip."""
    return re.sub(r"\s+", " ", value).strip()


@_normalizer
def remove_non_alphanumeric(value, keep_spaces=False):
    """Remove all non-alphanumeric characters from a string."""
    pattern = r"[^\w ]" if keep_spaces else r"[^\w]"
    result = re.sub(pattern, "", value)
    if not keep_spaces:
        result = re.sub(r"\s+", "", result)
    return result
