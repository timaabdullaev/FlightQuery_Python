"""Running queries against the flight database."""

from datetime import datetime
import math
import re

_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

_RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}

_ALLOWED_KEYS = _RECORD_KEYS | {"min_price", "sort_by", "order", "limit"}


def _is_valid_datetime(value: object) -> bool:
    if not isinstance(value, str) or not _DATETIME_RE.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def _is_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value))


def _is_int(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, int)


def _validate_query(query: object) -> bool:
    if not isinstance(query, dict):
        return False

    if not set(query.keys()).issubset(_ALLOWED_KEYS):
        return False

    if "order" in query and "sort_by" not in query:
        return False

    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return False

    for key in ("departure_datetime", "arrival_datetime"):
        if key in query and not _is_valid_datetime(query[key]):
            return False

    for key in ("price", "min_price"):
        if key in query and not _is_number(query[key]):
            return False

    if "sort_by" in query:
        if not isinstance(query["sort_by"], str) or query["sort_by"] not in _RECORD_KEYS:
            return False

    if "order" in query:
        if query["order"] not in ("asc", "desc"):
            return False

    if "limit" in query:
        if not _is_int(query["limit"]) or query["limit"] < 0:
            return False

    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not _validate_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

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

    if "sort_by" in query:
        sort_key = query["sort_by"]
        reverse = query.get("order") == "desc"
        matches = sorted(matches, key=lambda r: r[sort_key], reverse=reverse)

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        return [run_query(db, queries)]
    return [run_query(db, q) for q in queries]
