# csv-surgeon

> A CLI tool for surgical column transformations and filtering on large CSV files without loading them fully into memory.

---

## Installation

```bash
pip install csv-surgeon
```

Or install from source:

```bash
git clone https://github.com/yourname/csv-surgeon.git
cd csv-surgeon && pip install -e .
```

---

## Usage

```bash
# Keep only specific columns
csv-surgeon select --cols name,age,email input.csv -o output.csv

# Filter rows where a column matches a condition
csv-surgeon filter --col age --gt 30 input.csv -o output.csv

# Rename a column
csv-surgeon rename --col old_name --to new_name input.csv -o output.csv

# Chain operations via pipe
csv-surgeon select --cols name,age input.csv | csv-surgeon filter --col age --lt 50 -o output.csv
```

csv-surgeon processes files row-by-row using Python generators, making it safe to use on files that are gigabytes in size.

---

## Commands

| Command    | Description                          |
|------------|--------------------------------------|
| `select`   | Keep or drop specific columns        |
| `filter`   | Filter rows by column value          |
| `rename`   | Rename one or more columns           |
| `transform`| Apply a Python expression to a column|

---

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)

---

## License

This project is licensed under the [MIT License](LICENSE).