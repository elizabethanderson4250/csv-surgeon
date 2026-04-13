"""TransformPipeline for applying column transformations to CSV rows."""

from typing import Callable, Any, Iterator


class TransformPipeline:
    """Applies a series of column transformations to rows from a CSV reader."""

    def __init__(self) -> None:
        # List of (column_name, transform_fn) pairs
        self._transforms: list[tuple[str, Callable[[str, dict], tuple[str, Any]]]] = []

    def add_transform(self, column: str, transform_fn: Callable[[str, dict], tuple[str, Any]]) -> "TransformPipeline":
        """Register a transformation for the given column. Returns self for chaining."""
        self._transforms.append((column, transform_fn))
        return self

    def apply_to_row(self, row: dict) -> dict:
        """Apply all registered transforms to a single row dict."""
        result = dict(row)
        for column, transform_fn in self._transforms:
            if column not in result:
                continue
            new_key, new_value = transform_fn(column, result)
            if new_key != column:
                del result[column]
            result[new_key] = new_value
        return result

    def execute(self, rows: Iterator[dict]) -> Iterator[dict]:
        """Yield transformed rows from the given row iterator."""
        for row in rows:
            yield self.apply_to_row(row)

    def count(self) -> int:
        """Return the number of registered transforms."""
        return len(self._transforms)

    def clear(self) -> None:
        """Remove all registered transforms."""
        self._transforms.clear()
