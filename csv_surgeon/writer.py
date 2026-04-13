import csv
import io
from typing import Iterator, List, Optional, Dict, Any


class StreamingCSVWriter:
    """
    Writes CSV rows to a file or stream without buffering all rows in memory.
    Supports writing from dicts or raw row lists.
    """

    def __init__(self, output_path: str, fieldnames: List[str], delimiter: str = ",", lineterminator: str = "\n"):
        self.output_path = output_path
        self.fieldnames = fieldnames
        self.delimiter = delimiter
        self.lineterminator = lineterminator

    def write_rows(self, rows: Iterator[Dict[str, Any]], write_header: bool = True) -> int:
        """
        Write an iterator of dict rows to the output file.
        Returns the number of rows written (excluding header).
        """
        count = 0
        with open(self.output_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=self.fieldnames,
                delimiter=self.delimiter,
                lineterminator=self.lineterminator,
                extrasaction="ignore",
            )
            if write_header:
                writer.writeheader()
            for row in rows:
                writer.writerow(row)
                count += 1
        return count

    def write_raw_rows(self, rows: Iterator[List[str]], write_header: bool = True) -> int:
        """
        Write an iterator of raw list rows to the output file.
        Returns the number of rows written (excluding header).
        """
        count = 0
        with open(self.output_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter=self.delimiter, lineterminator=self.lineterminator)
            if write_header:
                writer.writerow(self.fieldnames)
            for row in rows:
                writer.writerow(row)
                count += 1
        return count

    def to_string(self, rows: Iterator[Dict[str, Any]], write_header: bool = True) -> str:
        """
        Serialize rows to a CSV-formatted string (useful for testing / piping).
        """
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=self.fieldnames,
            delimiter=self.delimiter,
            lineterminator=self.lineterminator,
            extrasaction="ignore",
        )
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return output.getvalue()
