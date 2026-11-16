# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- Google Gemini

## Conversation links

- https://share.gemini.google/zmEuuJgzWnT9

## What I used them for

- e.g. I used for assistance for running a programm and generation some parts of the codes

## Which parts of the code were AI-generated or substantially AI-assisted

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

_____________________________________________________________________________________


            matches = []
    for record in db:
        match = True
        for key, val in query.items():
            if key in ("sort_by", "order", "limit"):
                continue
            elif key == "min_price":
                if record["price"] < val:
                    match = False
                    break
            elif key == "price":
                if record["price"] > val:
                    match = False
                    break
            elif key == "departure_datetime":
                if record["departure_datetime"] < val:
                    match = False
                    break
            elif key == "arrival_datetime":
                if record["arrival_datetime"] > val:
                    match = False
                    break
            else:
                if record[key] != val:
                    match = False
                    break
        if match:
            matches.append(record)

______________________________________________________________________

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

## Key prompts

1.Here is my updated validator.py..." / Checking row validation logic for date formats, airport codes, and price boundaries.
2.Write a block of code for def query only" / Implementing query validation, exact matching, min_price/price range filtering, sorting (asc/desc), and limiting.
3.Troubleshooting price filters acting as upper bounds (price) versus minimum thresholds (min_price) to pass the test suite successfully.
4.Generate block for csv loader py" / Implementing file reading, skipping comments/headers, line numbering, and cross-file duplicate checking.

## What I changed or verified myself

