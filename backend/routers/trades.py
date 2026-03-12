from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.trade import Trade
from backend.schemas.trade import TradeResponse, TradeUpdate

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/", response_model=list[TradeResponse])
def list_trades(
    status: str | None = None,
    symbol: str | None = None,
    strategy: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Trade)
    if status:
        query = query.filter(Trade.status == status)
    if symbol:
        query = query.filter(Trade.symbol == symbol.upper())
    if strategy:
        query = query.filter(Trade.strategy == strategy)
    return query.order_by(Trade.opened_at.desc()).all()


@router.get("/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: str, db: Session = Depends(get_db)):
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade


@router.patch("/{trade_id}", response_model=TradeResponse)
def update_trade(trade_id: str, update: TradeUpdate, db: Session = Depends(get_db)):
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(trade, field, value)
    db.commit()
    db.refresh(trade)
    return trade
