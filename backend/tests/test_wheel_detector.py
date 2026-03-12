from datetime import datetime
from backend.services.wheel_detector import detect_wheel_candidates


def _trade(strategy, symbol, opened_at_str, status="closed"):
    return {
        "id": f"{strategy}-{symbol}-{opened_at_str}",
        "symbol": symbol,
        "strategy": strategy,
        "status": status,
        "opened_at": datetime.fromisoformat(opened_at_str),
    }


def test_detects_csp_followed_by_covered_call():
    trades = [
        _trade("csp", "TSLA", "2026-01-05"),
        _trade("covered_call", "TSLA", "2026-01-20"),
    ]
    suggestions = detect_wheel_candidates(trades)
    assert len(suggestions) == 1
    assert suggestions[0]["symbol"] == "TSLA"
    assert len(suggestions[0]["trade_ids"]) == 2


def test_no_suggestion_for_single_csp():
    trades = [_trade("csp", "AAPL", "2026-01-10")]
    suggestions = detect_wheel_candidates(trades)
    assert len(suggestions) == 0


def test_no_suggestion_for_unrelated_strategies():
    trades = [
        _trade("long_call", "AAPL", "2026-01-10"),
        _trade("long_put", "AAPL", "2026-01-15"),
    ]
    suggestions = detect_wheel_candidates(trades)
    assert len(suggestions) == 0


def test_multiple_symbols_detected_separately():
    trades = [
        _trade("csp", "TSLA", "2026-01-05"),
        _trade("covered_call", "TSLA", "2026-01-20"),
        _trade("csp", "AAPL", "2026-01-08"),
        _trade("covered_call", "AAPL", "2026-01-22"),
    ]
    suggestions = detect_wheel_candidates(trades)
    assert len(suggestions) == 2
    symbols = {s["symbol"] for s in suggestions}
    assert symbols == {"TSLA", "AAPL"}
