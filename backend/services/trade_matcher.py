from datetime import datetime, date


def _infer_strategy(option_type: str, side: str) -> str:
    """
    Infer strategy from a single-leg trade.
    Note: CSV import cannot distinguish a covered call from a naked short call
    (no 'shares held' data). We default short calls to 'covered_call' since
    this app targets premium sellers. If you want to track naked short calls,
    manually update the strategy field after import via the Trade Log.
    """
    if side == "sell" and option_type == "put":
        return "csp"
    if side == "sell" and option_type == "call":
        return "covered_call"  # assumes covered; update manually if naked short call
    if side == "buy" and option_type == "call":
        return "long_call"
    if side == "buy" and option_type == "put":
        return "long_put"
    return "csp"  # fallback, should not be reached


def _leg_key(row: dict) -> tuple:
    """Unique key for matching open/close rows."""
    return (row["symbol"], row["option_type"], row["strike"], row["expiry"])


def match_trades(rows: list[dict]) -> list[dict]:
    """
    Match open and close rows into complete trade dicts.
    Returns list of trade dicts ready for DB insertion.
    Each dict has: symbol, strategy, status, opened_at, closed_at,
    premium_collected, pnl, broker, dte_entry, legs (list of leg dicts).
    """
    import uuid

    # Sort chronologically
    sorted_rows = sorted(rows, key=lambda r: r["date"])

    # Track open positions: key → list of open rows (FIFO)
    open_positions: dict[tuple, list[dict]] = {}
    trades: list[dict] = []

    for row in sorted_rows:
        action = row["action"]
        key = _leg_key(row)

        if action in ("buy_to_open", "sell_to_open"):
            open_positions.setdefault(key, []).append(row)

        elif action in ("buy_to_close", "sell_to_close"):
            if key in open_positions and open_positions[key]:
                open_row = open_positions[key].pop(0)
                if not open_positions[key]:
                    del open_positions[key]

                open_side = "sell" if open_row["action"] == "sell_to_open" else "buy"
                strategy = _infer_strategy(open_row["option_type"], open_side)

                premium_collected = open_row["price"] * open_row["quantity"] * 100

                # P&L for premium seller: collected - cost to close
                if open_side == "sell":
                    pnl = (open_row["price"] - row["price"]) * open_row["quantity"] * 100
                else:
                    pnl = (row["price"] - open_row["price"]) * open_row["quantity"] * 100

                expiry: date = open_row["expiry"]
                opened_at: datetime = open_row["date"]
                dte_entry = (expiry - opened_at.date()).days

                trade_id = str(uuid.uuid4())
                trades.append({
                    "id": trade_id,
                    "symbol": open_row["symbol"],
                    "strategy": strategy,
                    "status": "closed",
                    "opened_at": opened_at,
                    "closed_at": row["date"],
                    "premium_collected": premium_collected if open_side == "sell" else None,
                    "pnl": round(pnl, 2),
                    "broker": "wealthsimple",
                    "dte_entry": dte_entry,
                    "legs": [{
                        "id": str(uuid.uuid4()),
                        "trade_id": trade_id,
                        "option_type": open_row["option_type"],
                        "side": open_side,
                        "strike": open_row["strike"],
                        "expiry": expiry,
                        "contracts": open_row["quantity"],
                        "price_open": open_row["price"],
                        "price_close": row["price"],
                    }],
                })

    # Remaining open positions become open trades
    for key, open_rows in open_positions.items():
        for open_row in open_rows:
            open_side = "sell" if open_row["action"] == "sell_to_open" else "buy"
            strategy = _infer_strategy(open_row["option_type"], open_side)
            expiry: date = open_row["expiry"]
            opened_at: datetime = open_row["date"]
            dte_entry = (expiry - opened_at.date()).days
            trade_id = str(uuid.uuid4())
            trades.append({
                "id": trade_id,
                "symbol": open_row["symbol"],
                "strategy": strategy,
                "status": "open",
                "opened_at": opened_at,
                "closed_at": None,
                "premium_collected": open_row["price"] * open_row["quantity"] * 100 if open_side == "sell" else None,
                "pnl": None,
                "broker": "wealthsimple",
                "dte_entry": dte_entry,
                "legs": [{
                    "id": str(uuid.uuid4()),
                    "trade_id": trade_id,
                    "option_type": open_row["option_type"],
                    "side": open_side,
                    "strike": open_row["strike"],
                    "expiry": expiry,
                    "contracts": open_row["quantity"],
                    "price_open": open_row["price"],
                    "price_close": None,
                }],
            })

    return trades
