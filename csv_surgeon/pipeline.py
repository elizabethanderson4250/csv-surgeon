"""Pipeline for chaining filters over a StreamingCSVReader."""

from typing import Iterable, List, Optional, Iterator
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.filters import FilterFunc, apply_filters


class FilterPipeline:
    """Applies a sequence of filters to rows from a StreamingCSVReader."""

    def __init__(self, reader: StreamingCSVReader) -> None:
        self._reader = reader
        self._filters: List[FilterFunc] = []

    def add_filter(self, f: FilterFunc) -> "FilterPipeline":
        """Add a filter to the pipeline. Returns self for chaining."""
        self._filters.append(f)
        return self

    def execute(self) -> Iterator[dict]:
        """Execute the pipeline and yield matching rows as dicts."""
        rows: Iterable[dict] = self._reader.rows()
        if not self._filters:
            yield from rows
            return
        yield from apply_filters(rows, *self._filters)

    def count(self) -> int:
        """Return the number of rows that pass all filters."""
        return sum(1 for _ in self.execute())

    def first(self) -> Optional[dict]:
        """Return the first matching row, or None if no rows match."""
        return next(self.execute(), None)

    def to_list(self) -> List[dict]:
        """Collect all matching rows into a list."""
        return list(self.execute())

    @property
    def headers(self) -> List[str]:
        """Return the headers from the underlying reader."""
        return self._reader.headers()
