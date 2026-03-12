import pytest
from backend.services.analytics_engine import (
    compute_overview,
    compute_by_dimension,
    compute_edge_patterns,
)


def _trade(pnl, strategy="csp", dte=21, iv_rank=60, symbol="AAPL"):
    return {
        "pnl": pnl,
        "status": "closed",
        "strategy": strategy,
        "dte_entry": dte,
        "iv_rank_entry": iv_rank,
        "symbol": symbol,
        "premium_collected": abs(pnl) * 1.5 if pnl else None,
    }


TRADES = [
    _trade(100, strategy="csp", dte=21, iv_rank=70),
    _trade(80, strategy="csp", dte=25, iv_rank=65),
    _trade(-50, strategy="csp", dte=5, iv_rank=20),
    _trade(60, strategy="covered_call", dte=30, iv_rank=55),
    _trade(-40, strategy="covered_call", dte=3, iv_rank=15),
    _trade(90, strategy="csp", dte=28, iv_rank=80),
]


def test_overview_win_rate():
    result = compute_overview(TRADES)
    assert result["win_rate"] == pytest.approx(4 / 6, rel=0.01)
    assert result["trade_count"] == 6
    assert result["winning_trades"] == 4


def test_overview_total_pnl():
    result = compute_overview(TRADES)
    assert result["total_pnl"] == pytest.approx(240.0, rel=0.01)


def test_overview_profit_factor():
    result = compute_overview(TRADES)
    total_wins = 100 + 80 + 60 + 90
    total_losses = 50 + 40
    assert result["profit_factor"] == pytest.approx(total_wins / total_losses, rel=0.01)


def test_by_dimension_strategy():
    result = compute_by_dimension(TRADES, dimension="strategy")
    csp = next(r for r in result if r["label"] == "csp")
    assert csp["win_rate"] == pytest.approx(3 / 4, rel=0.01)
    assert csp["trade_count"] == 4


def test_by_dimension_dte_buckets():
    result = compute_by_dimension(TRADES, dimension="dte")
    labels = [r["label"] for r in result]
    assert "0-7 DTE" in labels
    assert "21-35 DTE" in labels


def test_edge_patterns_identifies_high_iv_rank():
    result = compute_edge_patterns(TRADES)
    high_iv = next((p for p in result["best"] if "IV Rank" in p["condition"]), None)
    assert high_iv is not None
    assert high_iv["win_rate"] > 0.7


def test_edge_patterns_identifies_low_dte_weakness():
    result = compute_edge_patterns(TRADES)
    low_dte = next((p for p in result["worst"] if "DTE" in p["condition"]), None)
    assert low_dte is not None
    assert low_dte["win_rate"] < 0.6


def test_empty_trades_returns_zeros():
    result = compute_overview([])
    assert result["win_rate"] == 0
    assert result["total_pnl"] == 0
