"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
import sys

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251ADB075"
FIRST_NAME = "Timur"
LAST_NAME = "Abdullaev"

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flight_parser.py",
        description="Validate flight schedule CSVs, build JSON DB, and run queries.",
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("-i", dest="input_csv", help="Single input CSV file")
    source_group.add_argument("-d", dest="input_dir", help="Folder with CSV files")
    source_group.add_argument("-j", dest="input_json", help="Existing JSON database")

    parser.add_argument("-a", dest="airports_file", help="Airport list file")
    parser.add_argument("-o", dest="output_db", help="Output JSON database path")
    parser.add_argument("-q", dest="query_file", help="JSON file with queries")
    parser.add_argument("-r", dest="response_dir", default=".", help="Folder for query response")
    return parser


def _error(message: str) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return 1

def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    # TODO: parse arguments with argparse (-i, -d, -j, -a, -o, -q, -r).
    # TODO: load or parse the data, write the database and errors.log.
    # TODO: run the queries and write the response file.
    # Remember: remove and close the logging handler before returning,
    # also when returning early because of an error (use try/finally).
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0

    if args.input_csv is not None or args.input_dir is not None:
        if args.airports_file is None:
            try:
                parser.error("argument -a is required when using -i or -d")
            except SystemExit as exc:
                return int(exc.code) if exc.code is not None else 2
    elif args.input_json is not None:
        if args.output_db is not None:
            try:
                parser.error("argument -o is not allowed with -j")
            except SystemExit as exc:
                return int(exc.code) if exc.code is not None else 2

    db: list[dict] = []

#AI GENERATED BLOCK
    if args.input_json is not None:
        json_path = Path(args.input_json)
        if not json_path.is_file():
            return _error(f"Database file not found: {json_path}")
        try:
            loaded = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return _error(f"Invalid JSON in database file: {exc}")

        if not isinstance(loaded, list) or not all(isinstance(item, dict) for item in loaded):
            return _error("JSON database must be an array of objects")
        db = loaded
    else:
        airports_path = Path(args.airports_file)
        if not airports_path.is_file():
            return _error(f"Airport file not found: {airports_path}")
        try:
            airports = load_airports(str(airports_path))
        except (OSError, UnicodeDecodeError) as exc:
            return _error(f"Cannot read airport file: {exc}")

        csv_paths: list[str] = []
        if args.input_csv is not None:
            csv_file = Path(args.input_csv)
            if not csv_file.is_file():
                return _error(f"CSV file not found: {csv_file}")
            csv_paths = [str(csv_file)]
        else:
            folder = Path(args.input_dir)
            if not folder.is_dir():
                return _error(f"Folder not found: {folder}")
            try:
                matched = sorted(
                    p for p in folder.iterdir()
                    if p.is_file() and p.name.endswith(".csv")
                )
            except OSError as exc:
                return _error(f"Cannot read folder: {exc}")
            if not matched:
                return _error(f"No .csv files found in folder: {folder}")
            csv_paths = [str(p) for p in matched]

        db_path = Path(args.output_db) if args.output_db is not None else Path("db.json")
        log_path = db_path.parent / "errors.log"

        logger = logging.getLogger("flight_parser")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        )
        logger.addHandler(handler)
        try:
            try:
                db, errors = parse_files(csv_paths, airports)
            except (OSError, UnicodeDecodeError) as exc:
                return _error(f"Cannot read CSV file: {exc}")

            for err_msg in errors:
                logger.warning(err_msg)

            try:
                db_path.write_text(json.dumps(db, indent=2), encoding="utf-8")
            except OSError as exc:
                return _error(f"Cannot write database file: {exc}")
        finally:
            logger.removeHandler(handler)
            handler.close()
#MY OWN BLOCK

    if args.query_file is not None:
        query_path = Path(args.query_file)
        if not query_path.is_file():
            return _error(f"Query file not found: {query_path}")
        try:
            queries_data = json.loads(query_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return _error(f"Invalid JSON in query file: {exc}")

        if not isinstance(queries_data, (dict, list)):
            return _error("Query file must contain a JSON object or array")
        if isinstance(queries_data, list) and not all(isinstance(q, dict) for q in queries_data):
            return _error("Query array must contain only JSON objects")

        results = run_queries(db, queries_data)

        resp_dir = Path(args.response_dir)
        if not resp_dir.is_dir():
            return _error(f"Response folder not found: {resp_dir}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        resp_filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
        resp_path = resp_dir / resp_filename
        try:
            resp_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        except OSError as exc:
            return _error(f"Cannot write response file: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

