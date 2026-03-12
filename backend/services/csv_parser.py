import csv
from datetime import datetime
import re


class ParseError(Exception):
    pass


# Maps Wealthsimple action strings to normalized action names.
# UPDATE these keys to match your actual Wealthsimple CSV export.
ACTION_MAP = {
    "Buy to Open": "buy_to_open",
    "Sell to Open": "sell_to_open",
    "Buy to Close": "buy_to_close",
    "Sell to Close": "sell_to_close",
}

# Maps Wealthsimple CSV column headers to internal field names.
# UPDATE these keys to match your actual Wealthsimple CSV export.
COLUMN_MAP = {
    "Date": "date",
    "Action": "action",
    "Symbol": "symbol_raw",
    "Description": "description",
    "Quantity": "quantity",
    "Price": "price",
    "Amount": "amount",
}

REQUIRED_COLUMNS = set(COLUMN_MAP.keys())


def _parse_option_symbol(symbol_raw: str) -> dict:
    """
    Parse OCC-style option symbol: 'AAPL 2026-01-31 180.00 P'
    Returns dict with underlying, expiry, strike, option_type.
    Adjust regex if Wealthsimple uses a different symbol format.
    """
    pattern = r"^(\w+)\s+(\d{4}-\d{2}-\d{2})\s+([\d.]+)\s+([CP])$"
    match = re.match(pattern, symbol_raw.strip())
    if not match:
        raise ParseError(f"Cannot parse option symbol: {symbol_raw!r}")
    underlying, expiry_str, strike_str, opt_type = match.groups()
    return {
        "symbol": underlying,
        "expiry": datetime.strptime(expiry_str, "%Y-%m-%d").date(),
        "strike": float(strike_str),
        "option_type": "call" if opt_type == "C" else "put",
    }


def parse_wealthsimple_csv(filepath: str) -> list[dict]:
    """
    Parse a Wealthsimple options CSV export.
    Returns a list of normalized raw trade row dicts.
    """
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise ParseError(f"Missing required columns: {missing}")

        rows = []
        for i, row in enumerate(reader, start=2):
            action_raw = row["Action"].strip()
            action = ACTION_MAP.get(action_raw)
            if action is None:
                continue  # skip non-options rows (e.g. dividends, stock purchases)

            try:
                parsed_symbol = _parse_option_symbol(row["Symbol"])
            except ParseError:
                continue  # skip rows that don't match option symbol format

            rows.append({
                "date": datetime.strptime(row["Date"].strip(), "%Y-%m-%d"),
                "action": action,
                "symbol": parsed_symbol["symbol"],
                "option_type": parsed_symbol["option_type"],
                "strike": parsed_symbol["strike"],
                "expiry": parsed_symbol["expiry"],
                "quantity": int(float(row["Quantity"].strip())),
                "price": abs(float(row["Price"].strip())),
                "amount": float(row["Amount"].strip()),
                "symbol_raw": row["Symbol"].strip(),
            })
        return rows
