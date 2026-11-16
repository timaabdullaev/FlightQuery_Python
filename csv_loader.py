"""Reading CSV files into flight records and error messages."""

import csv
from pathlib import Path

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """

     #AI GENERATED BLOCK
    records: list[dict] = []
    errors: list[str] = []
    seen_flights: set[tuple[str, str]] = set()

    for path_str in paths:
        path = Path(path_str)
        file_name = path.name

        with open(path, mode="r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            for line_no, row in enumerate(reader, start=1):
                # Skip empty lines, comments, and the header row
                if not row:
                    continue
                first_cell = row[0].strip()
                if not first_cell or first_cell.startswith("#") or first_cell == "flight_id":
                    continue

                # Validate row structure and business rules
                error_code = validate_row(row, airports)
                if error_code is not None:
                    errors.append(f"{file_name}:{line_no}: {error_code} | {error_code}")
                else:
                    # Check for duplicate flights across all files (keyed by flight_id and departure_datetime)
                    cleaned = [field.strip() for field in row]
                    flight_key = (cleaned[0], cleaned[3])
                    
                    if flight_key in seen_flights:
                        errors.append(f"{file_name}:{line_no}: DUPLICATE_FLIGHT | DUPLICATE_FLIGHT")
                    else:
                        seen_flights.add(flight_key)
                        records.append(to_record(row))

    return records, errors
