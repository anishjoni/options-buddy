import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.trade import Trade, TradeLeg
from backend.models.import_run import ImportRun
from backend.services.csv_parser import parse_wealthsimple_csv, ParseError
from backend.services.trade_matcher import match_trades
from backend.services.wheel_detector import detect_wheel_candidates
from backend.schemas.analytics import ImportResponse
import tempfile, os

router = APIRouter(prefix="/import", tags=["import"])


def _dedup_key(trade: dict) -> str:
    leg = trade["legs"][0] if trade["legs"] else {}
    return f"{trade['symbol']}-{trade['opened_at'].date()}-{leg.get('strike')}-{leg.get('expiry')}-{leg.get('option_type')}"


@router.post("/csv", response_model=ImportResponse)
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    errors = []
    trades_added = 0
    status = "success"

    try:
        rows = parse_wealthsimple_csv(tmp_path)
        trade_dicts = match_trades(rows)

        # Deduplication: build set of existing trade keys
        existing = db.query(Trade).all()
        existing_keys = set()
        for t in existing:
            key = f"{t.symbol}-{t.opened_at.date()}-"
            if t.legs:
                l = t.legs[0]
                key += f"{l.strike}-{l.expiry}-{l.option_type}"
            existing_keys.add(key)

        for trade_dict in trade_dicts:
            key = _dedup_key(trade_dict)
            if key in existing_keys:
                continue

            legs = trade_dict.pop("legs", [])
            trade = Trade(**trade_dict)
            db.add(trade)
            for leg_dict in legs:
                db.add(TradeLeg(**leg_dict))
            trades_added += 1

        db.commit()

        # Detect wheel suggestions on all unlinked trades
        all_trades = [
            {"id": t.id, "symbol": t.symbol, "strategy": t.strategy.value,
             "status": t.status.value, "opened_at": t.opened_at, "campaign_id": t.campaign_id}
            for t in db.query(Trade).all()
        ]
        wheel_suggestions = detect_wheel_candidates(all_trades)

    except ParseError as e:
        errors.append(str(e))
        status = "failed"
        db.rollback()
        wheel_suggestions = []
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        status = "partial"
        db.rollback()
        wheel_suggestions = []
    finally:
        os.unlink(tmp_path)

    # Use a fresh transaction for the audit log — the session is safe after rollback
    # but we explicitly expunge any pending state to avoid stale object issues.
    db.expire_all()
    import_run = ImportRun(
        id=str(uuid.uuid4()),
        broker="wealthsimple",
        imported_at=datetime.utcnow(),
        trades_added=trades_added,
        status=status,
    )
    import_run.set_errors(errors)
    db.add(import_run)
    db.commit()

    return ImportResponse(
        trades_added=trades_added,
        status=status,
        errors=errors,
        wheel_suggestions=wheel_suggestions,
    )
