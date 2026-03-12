from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from backend.models.trade import StrategyEnum, StatusEnum


class TradeLegResponse(BaseModel):
    id: str
    trade_id: str
    option_type: str
    side: str
    strike: float
    expiry: date
    delta_entry: Optional[float]
    contracts: int
    price_open: float
    price_close: Optional[float]

    model_config = {"from_attributes": True}


class TradeResponse(BaseModel):
    id: str
    symbol: str
    strategy: StrategyEnum
    status: StatusEnum
    opened_at: datetime
    closed_at: Optional[datetime]
    premium_collected: Optional[float]
    pnl: Optional[float]
    broker: str
    iv_rank_entry: Optional[int]
    dte_entry: Optional[int]
    campaign_id: Optional[str]
    notes: Optional[str]
    legs: list[TradeLegResponse]

    model_config = {"from_attributes": True}


class TradeUpdate(BaseModel):
    notes: Optional[str] = None
    campaign_id: Optional[str] = None
    iv_rank_entry: Optional[int] = None
