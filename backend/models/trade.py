import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Float, Integer, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from backend.database import Base


class StrategyEnum(str, PyEnum):
    long_call = "long_call"
    long_put = "long_put"
    short_call = "short_call"
    short_put = "short_put"
    csp = "csp"
    covered_call = "covered_call"
    credit_spread = "credit_spread"
    debit_spread = "debit_spread"


class StatusEnum(str, PyEnum):
    open = "open"
    closed = "closed"
    expired = "expired"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, nullable=False, index=True)
    strategy = Column(Enum(StrategyEnum), nullable=False)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.open)
    opened_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    premium_collected = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    broker = Column(String, nullable=False)
    iv_rank_entry = Column(Integer, nullable=True)
    dte_entry = Column(Integer, nullable=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=True)
    notes = Column(String, nullable=True)

    legs = relationship("TradeLeg", back_populates="trade", cascade="all, delete-orphan")
    campaign = relationship("Campaign", back_populates="trades")


class TradeLeg(Base):
    __tablename__ = "trade_legs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trade_id = Column(String, ForeignKey("trades.id"), nullable=False)
    option_type = Column(String, nullable=False)   # "call" | "put"
    side = Column(String, nullable=False)           # "buy" | "sell"
    strike = Column(Float, nullable=False)
    expiry = Column(Date, nullable=False)
    delta_entry = Column(Float, nullable=True)
    contracts = Column(Integer, nullable=False, default=1)
    price_open = Column(Float, nullable=False)
    price_close = Column(Float, nullable=True)

    trade = relationship("Trade", back_populates="legs")
