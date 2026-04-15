"""Streaming CSV writer — writes rows one at a time without buffering all data."""
from __future__ import annotations

import csv
import io
from typing import Dict, Iterable, List, Optional


class StreamingCSVWriter:
    """Write dicts (or raw lists) to a CSV file row by row."""

    def __init__(self, path: str, fieldnames: Optional[List[str]] = None) -> None:
        self.path = path
        self.fieldnames = fieldnames

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write_rows(
        self,
        rows: Iterable[Dict[str, str]],
        fieldnames: Optional[List[str]] = None,
    ) -> int:
        """Write an iterable of dicts to *self.path*.

        Returns the number of data rows written (header not counted).
        """
        effective_fields = fieldnames or self.fieldnames
        count = 0
        with open(self.path, "w", newline="", encoding="utf-8") as fh:
            writer: Optional[csv.DictWriter] = None
            for row in rows:
                if writer is None:
                    fields = effective_fields or list(row.keys())
                    writer = csv.DictWriter(
                        fh, fieldnames=fields, extrasaction="ignore"
                    )
                    writer.writeheader()
                writer.writerow(row)
                count += 1
            if writer is None:
                # No rows — write header only if we know the fields
                if effective_fields:
                    writer = csv.DictWriter(fh, fieldnames=effective_fields)
                    writer.writeheader()
        return count

    def write_raw_rows(
        self,
        rows: Iterable[List[str]],
        header: Optional[List[str]] = None,
    ) -> int:
        """Write raw lists (no header inference from row keys).

        If *header* is provided it is written as the first row.
        Returns the number of data rows written.
        """
        count = 0
        with open(self.path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            if header:
                writer.writerow(header)
            for row in rows:
                writer.writerow(row)
                count += 1
        return count

    def to_string(
        self,
        rows: Iterable[Dict[str, str]],
        fieldnames: Optional[List[str]] = None,
    ) -> str:
        """Return the CSV content as a string (useful for testing)."""
        effective_fields = fieldnames or self.fieldnames
        buf = io.StringIO()
        writer: Optional[csv.DictWriter] = None
        for row in rows:
            if writer is None:
                fields = effective_fields or list(row.keys())
                writer = csv.DictWriter(
                    buf, fieldnames=fields, extrasaction="ignore"
                )
                writer.writeheader()
            writer.writerow(row)
        return buf.getvalue()
