import pytest
from backend.services.csv_parser import parse_wealthsimple_csv, ParseError


SAMPLE_CSV = """Date,Action,Symbol,Description,Quantity,Price,Amount
2026-01-10,Buy to Open,AAPL 2026-01-31 180.00 P,AAPL Put $180 Jan 31 2026,1,1.20,-120.00
2026-01-25,Sell to Close,AAPL 2026-01-31 180.00 P,AAPL Put $180 Jan 31 2026,1,2.20,220.00
2026-01-15,Sell to Open,SPY 2026-02-07 500.00 C,SPY Call $500 Feb 7 2026,2,0.85,170.00
"""


def test_parse_returns_list_of_raw_rows(tmp_path):
    f = tmp_path / "trades.csv"
    f.write_text(SAMPLE_CSV)
    rows = parse_wealthsimple_csv(str(f))
    assert len(rows) == 3


def test_parsed_row_has_required_fields(tmp_path):
    f = tmp_path / "trades.csv"
    f.write_text(SAMPLE_CSV)
    rows = parse_wealthsimple_csv(str(f))
    row = rows[0]
    assert row["date"] is not None
    assert row["action"] in ("buy_to_open", "sell_to_open", "buy_to_close", "sell_to_close")
    assert row["symbol"] == "AAPL"
    assert row["option_type"] in ("call", "put")
    assert row["strike"] == 180.0
    assert row["expiry"] is not None
    assert row["quantity"] == 1
    assert row["price"] == 1.20


def test_parse_raises_on_missing_columns(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text("col1,col2\nval1,val2\n")
    with pytest.raises(ParseError, match="Missing required columns"):
        parse_wealthsimple_csv(str(f))


def test_sell_to_open_action(tmp_path):
    f = tmp_path / "trades.csv"
    f.write_text(SAMPLE_CSV)
    rows = parse_wealthsimple_csv(str(f))
    sell_open = next(r for r in rows if r["action"] == "sell_to_open")
    assert sell_open["symbol"] == "SPY"
    assert sell_open["option_type"] == "call"
    assert sell_open["strike"] == 500.0
    assert sell_open["quantity"] == 2
