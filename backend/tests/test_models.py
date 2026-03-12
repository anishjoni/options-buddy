from backend.models.trade import Trade, TradeLeg, StrategyEnum, StatusEnum
from backend.models.campaign import Campaign
from backend.models.import_run import ImportRun
import uuid
from datetime import datetime, date


def test_create_trade(db_session):
    trade = Trade(
        id=str(uuid.uuid4()),
        symbol="AAPL",
        strategy=StrategyEnum.csp,
        status=StatusEnum.closed,
        opened_at=datetime(2026, 1, 10),
        premium_collected=120.0,
        pnl=100.0,
        broker="wealthsimple",
        dte_entry=21,
    )
    db_session.add(trade)
    db_session.commit()
    result = db_session.query(Trade).filter_by(symbol="AAPL").first()
    assert result.strategy == StrategyEnum.csp
    assert result.pnl == 100.0


def test_create_trade_leg(db_session):
    trade_id = str(uuid.uuid4())
    trade = Trade(
        id=trade_id,
        symbol="AAPL",
        strategy=StrategyEnum.csp,
        status=StatusEnum.closed,
        opened_at=datetime(2026, 1, 10),
        premium_collected=120.0,
        broker="wealthsimple",
        dte_entry=21,
    )
    db_session.add(trade)
    leg = TradeLeg(
        id=str(uuid.uuid4()),
        trade_id=trade_id,
        option_type="put",
        side="sell",
        strike=180.0,
        expiry=date(2026, 1, 31),
        contracts=1,
        price_open=1.20,
    )
    db_session.add(leg)
    db_session.commit()
    assert len(trade.legs) == 1
    assert trade.legs[0].strike == 180.0


def test_create_campaign(db_session):
    campaign = Campaign(
        id=str(uuid.uuid4()),
        name="TSLA Wheel Q1 2026",
        type="wheel",
        symbol="TSLA",
        status="active",
        started_at=datetime(2026, 1, 5),
    )
    db_session.add(campaign)
    db_session.commit()
    result = db_session.query(Campaign).first()
    assert result.symbol == "TSLA"
