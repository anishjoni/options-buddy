from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.trade import Trade, StatusEnum
from backend.schemas.analytics import OverviewResponse, DimensionBreakdown, EdgeResponse
from backend.services.analytics_engine import compute_overview, compute_by_dimension, compute_edge_patterns

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _trades_to_dicts(trades: list[Trade]) -> list[dict]:
    return [
        {
            "pnl": t.pnl,
            "status": t.status.value,
            "strategy": t.strategy.value,
            "dte_entry": t.dte_entry,
            "iv_rank_entry": t.iv_rank_entry,
            "symbol": t.symbol,
            "premium_collected": t.premium_collected,
        }
        for t in trades
    ]


@router.get("/overview", response_model=OverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    trades = db.query(Trade).all()
    return compute_overview(_trades_to_dicts(trades))


@router.get("/by-strategy", response_model=list[DimensionBreakdown])
def by_strategy(db: Session = Depends(get_db)):
    trades = db.query(Trade).all()
    return compute_by_dimension(_trades_to_dicts(trades), "strategy")


@router.get("/by-symbol", response_model=list[DimensionBreakdown])
def by_symbol(db: Session = Depends(get_db)):
    trades = db.query(Trade).all()
    return compute_by_dimension(_trades_to_dicts(trades), "symbol")


@router.get("/by-dte", response_model=list[DimensionBreakdown])
def by_dte(db: Session = Depends(get_db)):
    trades = db.query(Trade).all()
    return compute_by_dimension(_trades_to_dicts(trades), "dte")


@router.get("/by-iv-rank", response_model=list[DimensionBreakdown])
def by_iv_rank(db: Session = Depends(get_db)):
    trades = db.query(Trade).all()
    return compute_by_dimension(_trades_to_dicts(trades), "iv_rank")


@router.get("/edge", response_model=EdgeResponse)
def get_edge(db: Session = Depends(get_db)):
    trades = db.query(Trade).all()
    return compute_edge_patterns(_trades_to_dicts(trades))
