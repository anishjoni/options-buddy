import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.campaign import Campaign
from backend.models.trade import Trade
from backend.schemas.campaign import CampaignCreate, CampaignResponse

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/", response_model=list[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.started_at.desc()).all()
    result = []
    for c in campaigns:
        trades = db.query(Trade).filter(Trade.campaign_id == c.id).all()
        total_pnl = sum(t.pnl for t in trades if t.pnl is not None)
        result.append(CampaignResponse(
            id=c.id, name=c.name, type=c.type, symbol=c.symbol,
            status=c.status, started_at=c.started_at, ended_at=c.ended_at,
            notes=c.notes, trade_count=len(trades),
            total_pnl=round(total_pnl, 2) if trades else None,
        ))
    return result


@router.post("/", response_model=CampaignResponse)
def create_campaign(body: CampaignCreate, db: Session = Depends(get_db)):
    campaign = Campaign(
        id=str(uuid.uuid4()),
        name=body.name,
        type=body.type,
        symbol=body.symbol.upper(),
        status="active",
        started_at=datetime.utcnow(),
        notes=body.notes,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return CampaignResponse(
        **campaign.__dict__, trade_count=0, total_pnl=None
    )


class LinkTradesRequest(BaseModel):
    trade_ids: list[str]


@router.post("/{campaign_id}/link-trades")
def link_trades(campaign_id: str, body: LinkTradesRequest, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    updated = 0
    for tid in body.trade_ids:
        trade = db.query(Trade).filter(Trade.id == tid).first()
        if trade:
            trade.campaign_id = campaign_id
            updated += 1
    db.commit()
    return {"linked": updated}


@router.patch("/{campaign_id}/complete")
def complete_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.status = "completed"
    campaign.ended_at = datetime.utcnow()
    db.commit()
    return {"status": "completed"}
