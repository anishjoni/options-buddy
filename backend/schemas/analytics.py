from pydantic import BaseModel
from typing import Optional


class OverviewResponse(BaseModel):
    win_rate: float
    total_pnl: float
    trade_count: int       # matches key returned by compute_overview
    winning_trades: int
    profit_factor: Optional[float]
    avg_premium: float


class DimensionBreakdown(BaseModel):
    label: str
    win_rate: float
    total_pnl: float
    trade_count: int
    winning_trades: int
    profit_factor: Optional[float]
    avg_premium: float


class EdgePattern(BaseModel):
    condition: str
    win_rate: float
    trade_count: int


class EdgeResponse(BaseModel):
    best: list[EdgePattern]
    worst: list[EdgePattern]


class ImportResponse(BaseModel):
    trades_added: int
    status: str
    errors: list[str]
    wheel_suggestions: list[dict]
