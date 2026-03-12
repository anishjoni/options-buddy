WHEEL_STRATEGIES = {"csp", "covered_call"}


def detect_wheel_candidates(trades: list[dict]) -> list[dict]:
    """
    Scan trades for CSP → covered_call sequences on the same symbol.
    Returns a list of suggestions: {symbol, trade_ids, suggested_name, trade_count}.
    Only surfaces groups not already linked to a campaign (campaign_id is None).
    """
    # Filter to unlinked wheel-eligible trades
    eligible = [
        t for t in trades
        if t["strategy"] in WHEEL_STRATEGIES and not t.get("campaign_id")
    ]

    # Group by symbol
    by_symbol: dict[str, list[dict]] = {}
    for t in eligible:
        by_symbol.setdefault(t["symbol"], []).append(t)

    suggestions = []
    for symbol, symbol_trades in by_symbol.items():
        sorted_trades = sorted(symbol_trades, key=lambda t: t["opened_at"])
        strategies = [t["strategy"] for t in sorted_trades]

        # Must have at least one CSP and one covered_call
        if "csp" not in strategies or "covered_call" not in strategies:
            continue

        # Must have CSP before covered_call
        first_csp_idx = strategies.index("csp")
        try:
            first_cc_idx = strategies.index("covered_call")
        except ValueError:
            continue

        if first_csp_idx >= first_cc_idx:
            continue

        trade_ids = [t["id"] for t in sorted_trades]
        suggestions.append({
            "symbol": symbol,
            "trade_ids": trade_ids,
            "suggested_name": f"{symbol} Wheel",
            "trade_count": len(sorted_trades),
        })

    return suggestions
