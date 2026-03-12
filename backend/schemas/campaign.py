from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CampaignCreate(BaseModel):
    name: str
    type: str = "wheel"
    symbol: str
    notes: Optional[str] = None


class CampaignResponse(BaseModel):
    id: str
    name: str
    type: str
    symbol: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    notes: Optional[str]
    trade_count: int = 0
    total_pnl: Optional[float] = None

    model_config = {"from_attributes": True}


class WheelSuggestion(BaseModel):
    symbol: str
    trade_ids: list[str]
    suggested_name: str
    trade_count: int
