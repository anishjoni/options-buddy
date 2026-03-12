import pytest
from datetime import datetime, date
from backend.services.trade_matcher import match_trades


def _row(action, symbol, option_type, strike, expiry_str, price, qty=1, dt_str="2026-01-10"):
    return {
        "date": datetime.strptime(dt_str, "%Y-%m-%d"),
        "action": action,
        "symbol": symbol,
        "option_type": option_type,
        "strike": strike,
        "expiry": date.fromisoformat(expiry_str),
        "quantity": qty,
        "price": price,
        "amount": price * qty * 100 * (-1 if "open" in action and "sell" not in action else 1),
        "symbol_raw": f"{symbol} {expiry_str} {strike} {'C' if option_type == 'call' else 'P'}",
    }


def test_matched_csp_produces_one_closed_trade():
    rows = [
        _row("sell_to_open", "AAPL", "put", 180.0, "2026-01-31", 1.20, dt_str="2026-01-10"),
        _row("buy_to_close", "AAPL", "put", 180.0, "2026-01-31", 0.20, dt_str="2026-01-25"),
    ]
    trades = match_trades(rows)
    assert len(trades) == 1
    t = trades[0]
    assert t["status"] == "closed"
    assert t["strategy"] == "csp"
    assert t["symbol"] == "AAPL"
    assert t["premium_collected"] == 1.20 * 100
    assert t["pnl"] == pytest.approx((1.20 - 0.20) * 100, rel=0.01)
    assert len(t["legs"]) == 1


def test_unmatched_sell_open_produces_open_trade():
    rows = [
        _row("sell_to_open", "TSLA", "put", 220.0, "2026-02-28", 2.50),
    ]
    trades = match_trades(rows)
    assert len(trades) == 1
    assert trades[0]["status"] == "open"
    assert trades[0]["pnl"] is None


def test_covered_call_strategy_detected():
    rows = [
        _row("sell_to_open", "SPY", "call", 500.0, "2026-02-07", 0.85, dt_str="2026-01-15"),
        _row("buy_to_close", "SPY", "call", 500.0, "2026-02-07", 0.30, dt_str="2026-02-01"),
    ]
    trades = match_trades(rows)
    assert trades[0]["strategy"] == "covered_call"


def test_multiple_trades_same_symbol():
    rows = [
        _row("sell_to_open", "AAPL", "put", 180.0, "2026-01-31", 1.20, dt_str="2026-01-05"),
        _row("buy_to_close", "AAPL", "put", 180.0, "2026-01-31", 0.20, dt_str="2026-01-20"),
        _row("sell_to_open", "AAPL", "put", 175.0, "2026-02-28", 1.50, dt_str="2026-01-25"),
        _row("buy_to_close", "AAPL", "put", 175.0, "2026-02-28", 0.50, dt_str="2026-02-15"),
    ]
    trades = match_trades(rows)
    assert len(trades) == 2
    assert all(t["status"] == "closed" for t in trades)
