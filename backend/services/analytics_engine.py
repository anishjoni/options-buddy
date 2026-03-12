from typing import Literal

DTE_BUCKETS = [
    ("0-7 DTE", 0, 7),
    ("8-14 DTE", 8, 14),
    ("15-20 DTE", 15, 20),
    ("21-35 DTE", 21, 35),
    ("36+ DTE", 36, 9999),
]

IV_RANK_BUCKETS = [
    ("IV < 25", 0, 24),
    ("IV 25-49", 25, 49),
    ("IV 50-74", 50, 74),
    ("IV 75+", 75, 100),
]


def _win_rate_and_pnl(trades: list[dict]) -> dict:
    closed = [t for t in trades if t["status"] == "closed" and t["pnl"] is not None]
    if not closed:
        return {"win_rate": 0, "total_pnl": 0, "trade_count": 0,
                "winning_trades": 0, "profit_factor": 0, "avg_premium": 0}
    wins = [t for t in closed if t["pnl"] > 0]
    losses = [t for t in closed if t["pnl"] <= 0]
    total_win = sum(t["pnl"] for t in wins)
    total_loss = abs(sum(t["pnl"] for t in losses))
    premiums = [t["premium_collected"] for t in closed if t.get("premium_collected")]
    return {
        "win_rate": len(wins) / len(closed),
        "total_pnl": round(sum(t["pnl"] for t in closed), 2),
        "trade_count": len(closed),
        "winning_trades": len(wins),
        "profit_factor": round(total_win / total_loss, 2) if total_loss > 0 else None,
        "avg_premium": round(sum(premiums) / len(premiums), 2) if premiums else 0,
    }


def compute_overview(trades: list[dict]) -> dict:
    return _win_rate_and_pnl(trades)


def compute_by_dimension(
    trades: list[dict],
    dimension: Literal["strategy", "symbol", "dte", "iv_rank"],
) -> list[dict]:
    """Segment trades by dimension, return stats per segment."""
    closed = [t for t in trades if t["status"] == "closed" and t["pnl"] is not None]
    results = []

    if dimension == "strategy":
        strategies = sorted(set(t["strategy"] for t in closed))
        for s in strategies:
            subset = [t for t in closed if t["strategy"] == s]
            stats = _win_rate_and_pnl(subset)
            results.append({"label": s, **stats})

    elif dimension == "symbol":
        symbols = sorted(set(t["symbol"] for t in closed))
        for sym in symbols:
            subset = [t for t in closed if t["symbol"] == sym]
            stats = _win_rate_and_pnl(subset)
            results.append({"label": sym, **stats})

    elif dimension == "dte":
        for label, lo, hi in DTE_BUCKETS:
            subset = [t for t in closed if t.get("dte_entry") is not None and lo <= t["dte_entry"] <= hi]
            if subset:
                stats = _win_rate_and_pnl(subset)
                results.append({"label": label, **stats})

    elif dimension == "iv_rank":
        for label, lo, hi in IV_RANK_BUCKETS:
            subset = [t for t in closed if t.get("iv_rank_entry") is not None and lo <= t["iv_rank_entry"] <= hi]
            if subset:
                stats = _win_rate_and_pnl(subset)
                results.append({"label": label, **stats})

    return sorted(results, key=lambda r: r["win_rate"], reverse=True)


def compute_edge_patterns(trades: list[dict]) -> dict:
    """
    Surface top winning and losing conditions across DTE and IV rank dimensions.
    Returns {"best": [...], "worst": [...]} with condition, win_rate, trade_count.
    """
    closed = [t for t in trades if t["status"] == "closed" and t["pnl"] is not None]
    if len(closed) < 3:
        return {"best": [], "worst": []}

    overall_win_rate = len([t for t in closed if t["pnl"] > 0]) / len(closed)
    patterns = []

    # DTE patterns
    for label, lo, hi in DTE_BUCKETS:
        subset = [t for t in closed if t.get("dte_entry") is not None and lo <= t["dte_entry"] <= hi]
        if len(subset) >= 2:
            wr = len([t for t in subset if t["pnl"] > 0]) / len(subset)
            patterns.append({"condition": f"DTE {label}", "win_rate": round(wr, 3), "trade_count": len(subset)})

    # IV rank patterns
    for label, lo, hi in IV_RANK_BUCKETS:
        subset = [t for t in closed if t.get("iv_rank_entry") is not None and lo <= t["iv_rank_entry"] <= hi]
        if len(subset) >= 2:
            wr = len([t for t in subset if t["pnl"] > 0]) / len(subset)
            patterns.append({"condition": f"IV Rank {label}", "win_rate": round(wr, 3), "trade_count": len(subset)})

    best = sorted([p for p in patterns if p["win_rate"] > overall_win_rate], key=lambda x: -x["win_rate"])[:3]
    worst = sorted([p for p in patterns if p["win_rate"] <= overall_win_rate], key=lambda x: x["win_rate"])[:3]
    return {"best": best, "worst": worst}
