"""Streaming CSV reader that processes rows without loading the full file into memory."""

import csv
from pathlib import Path
from typing import Generator, Iterator, Optional


class StreamingCSVReader:
    """Reads a CSV file row-by-row using a generator to avoid full memory load."""

    def __init__(self, filepath: str | Path, delimiter: str = ",", encoding: str = "utf-8"):
        self.filepath = Path(filepath)
        self.delimiter = delimiter
        self.encoding = encoding
        self._headers: Optional[list[str]] = None

        if not self.filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {self.filepath}")

    @property
    def headers(self) -> list[str]:
        """Return the header row without consuming the full file."""
        if self._headers is None:
            with self.filepath.open(encoding=self.encoding, newline="") as fh:
                reader = csv.reader(fh, delimiter=self.delimiter)
                self._headers = next(reader, [])
        return self._headers

    def rows(self, skip_header: bool = True) -> Generator[dict[str, str], None, None]:
        """Yield each row as a dict keyed by header name."""
        with self.filepath.open(encoding=self.encoding, newline="") as fh:
            reader = csv.DictReader(fh, delimiter=self.delimiter)
            for row in reader:
                yield dict(row)

    def raw_rows(self, skip_header: bool = True) -> Generator[list[str], None, None]:
        """Yield each row as a plain list of strings."""
        with self.filepath.open(encoding=self.encoding, newline="") as fh:
            reader = csv.reader(fh, delimiter=self.delimiter)
            if skip_header:
                next(reader, None)
            for row in reader:
                yield row

    def row_count(self) -> int:
        """Count data rows (excluding header) without storing them."""
        count = 0
        for _ in self.raw_rows(skip_header=True):
            count += 1
        return count
