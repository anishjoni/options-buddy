# Options Buddy MVP Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web app that imports Wealthsimple options trade history via CSV, stores it in a structured database, and surfaces analytics to identify your personal trading edge.

**Architecture:** Python/FastAPI backend with SQLAlchemy + SQLite, React/Vite frontend. CSV import normalizes raw broker data into a common schema. Analytics engine segments trade history to surface win/loss patterns by strategy, symbol, DTE, and IV rank.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, SQLite, pytest | React 18, Vite, Tailwind CSS, Recharts, React Router

---

## File Structure

```
options_buddy/
├── backend/
│   ├── main.py                      # FastAPI app, CORS, router registration
│   ├── database.py                  # SQLAlchemy engine + session factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── trade.py                 # Trade + TradeLeg ORM models
│   │   ├── campaign.py              # Campaign ORM model
│   │   └── import_run.py            # ImportRun ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── trade.py                 # Pydantic request/response schemas
│   │   ├── campaign.py              # Pydantic campaign schemas
│   │   └── analytics.py             # Pydantic analytics response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── trades.py                # GET /trades, GET /trades/{id}, PATCH /trades/{id}
│   │   ├── imports.py               # POST /import/csv
│   │   ├── analytics.py             # GET /analytics/overview, /by-strategy, /by-symbol, /by-dte, /by-iv-rank, /edge
│   │   └── campaigns.py             # GET/POST/PATCH /campaigns, GET /campaigns/{id}
│   ├── services/
│   │   ├── __init__.py
│   │   ├── csv_parser.py            # Parse Wealthsimple CSV rows → RawTrade dicts
│   │   ├── trade_matcher.py         # Match open/close rows → Trade + TradeLeg records
│   │   ├── analytics_engine.py      # Compute win rate, P&L, profit factor, edge patterns
│   │   └── wheel_detector.py        # Detect CSP→assignment→CC sequences, return suggestions
│   └── tests/
│       ├── conftest.py              # pytest fixtures: test DB engine, test client
│       ├── test_csv_parser.py
│       ├── test_trade_matcher.py
│       ├── test_analytics_engine.py
│       └── test_wheel_detector.py
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── package.json
│   └── src/
│       ├── main.jsx                 # React entry point, BrowserRouter
│       ├── App.jsx                  # Root layout: nav sidebar + <Outlet>
│       ├── api/
│       │   └── client.js            # fetch wrapper with base URL + error handling
│       ├── pages/
│       │   ├── Dashboard.jsx        # PnL chart + metric cards + trade log
│       │   ├── Analytics.jsx        # Tabbed analytics: Overview/Strategy/Symbol/DTE/IVRank
│       │   ├── TradeLog.jsx         # Full filterable trade list
│       │   └── Campaigns.jsx        # Wheel campaigns list + detail
│       ├── components/
│       │   ├── PnLChart.jsx         # Recharts LineChart: cumulative P&L over time
│       │   ├── WinRateBar.jsx       # Horizontal bar chart: win rate by dimension
│       │   ├── MetricCard.jsx       # Single stat display (value + label + sub-label)
│       │   ├── EdgePanel.jsx        # "Your Edge" green/red conditions panel
│       │   ├── TradeTable.jsx       # Sortable table with strategy/symbol/DTE/P&L columns
│       │   ├── TradeDetail.jsx      # Modal: full trade + legs detail, notes editor
│       │   ├── CampaignCard.jsx     # Wheel cycle: name, status, cycle P&L, linked trades
│       │   └── CSVUpload.jsx        # Drag-and-drop zone + submit, shows import result
│       └── hooks/
│           ├── useTrades.js         # GET /trades, returns { trades, loading, error }
│           ├── useAnalytics.js      # GET /analytics/*, returns analytics data
│           └── useCampaigns.js      # GET /campaigns, returns { campaigns, loading, error }
├── requirements.txt
└── docs/
    └── superpowers/
        ├── specs/
        └── plans/
```

---

## Chunk 1: Project Setup + Database Models

### Task 1: Backend scaffold

**Files:**
- Create: `backend/main.py`
- Create: `backend/database.py`
- Create: `backend/requirements.txt` (root level)
- Create: `backend/models/__init__.py`

- [ ] **Step 1: Create backend directory structure**

```bash
mkdir -p backend/models backend/schemas backend/routers backend/services backend/tests
touch backend/models/__init__.py backend/schemas/__init__.py backend/routers/__init__.py backend/services/__init__.py backend/tests/__init__.py
```

- [ ] **Step 2: Create `requirements.txt` in project root**

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
pydantic==2.10.3
python-multipart==0.0.20
pytest==8.3.4
pytest-asyncio==0.24.0
httpx==0.28.1
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: all packages install without error.

- [ ] **Step 4: Create `backend/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./options_buddy.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: Create `backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Base, engine

app = FastAPI(title="Options Buddy", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Verify server starts**

```bash
cd backend && uvicorn main:app --reload
```

Expected: `Uvicorn running on http://127.0.0.1:8000`. Visit http://127.0.0.1:8000/health → `{"status":"ok"}`.

- [ ] **Step 7: Commit**

```bash
git init
git add requirements.txt backend/
git commit -m "feat: backend scaffold with FastAPI + SQLAlchemy"
```

---

### Task 2: Database models

**Files:**
- Create: `backend/models/trade.py`
- Create: `backend/models/campaign.py`
- Create: `backend/models/import_run.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: Write failing model smoke test**

Create `backend/tests/conftest.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
```

Create `backend/tests/test_models.py`:

```python
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
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd backend && pytest tests/test_models.py -v
```

Expected: ImportError — models don't exist yet.

- [ ] **Step 3: Create `backend/models/trade.py`**

```python
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
```

- [ ] **Step 4: Create `backend/models/campaign.py`**

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default="wheel")  # "wheel" | "custom"
    symbol = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="active")  # "active" | "completed"
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)

    trades = relationship("Trade", back_populates="campaign")
```

- [ ] **Step 5: Create `backend/models/import_run.py`**

```python
import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from backend.database import Base


class ImportRun(Base):
    __tablename__ = "import_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    broker = Column(String, nullable=False)
    imported_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    trades_added = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="success")  # success | partial | failed
    errors = Column(String, nullable=True)  # JSON string

    def set_errors(self, errors: list):
        self.errors = json.dumps(errors)

    def get_errors(self) -> list:
        return json.loads(self.errors) if self.errors else []
```

- [ ] **Step 6: Update `backend/models/__init__.py`**

```python
from backend.models.campaign import Campaign
from backend.models.trade import Trade, TradeLeg, StrategyEnum, StatusEnum
from backend.models.import_run import ImportRun

__all__ = ["Campaign", "Trade", "TradeLeg", "StrategyEnum", "StatusEnum", "ImportRun"]
```

- [ ] **Step 7: Run tests — expect pass**

```bash
cd backend && pytest tests/test_models.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add backend/models/ backend/tests/
git commit -m "feat: SQLAlchemy models for Trade, TradeLeg, Campaign, ImportRun"
```

---

## Chunk 2: CSV Import Engine

### Task 3: CSV Parser

**Files:**
- Create: `backend/services/csv_parser.py`
- Create: `backend/tests/test_csv_parser.py`

> **Note on Wealthsimple CSV format:** Wealthsimple's options trade export columns need to be confirmed against an actual export. The parser targets a likely format — you MUST verify and update `COLUMN_MAP` before this task produces real data.

- [ ] **Step 0: Verify Wealthsimple CSV format**

Export a real CSV from Wealthsimple (Account → Activity → Export). Open it in a text editor and confirm:
- Column headers match the keys in `COLUMN_MAP` (Date, Action, Symbol, Description, Quantity, Price, Amount)
- Action values match `ACTION_MAP` (e.g. "Buy to Open", "Sell to Open", etc.)
- Date format is `YYYY-MM-DD`
- Symbol format is OCC-style: `AAPL 2026-01-31 180.00 P`

If any differ, update `COLUMN_MAP`, `ACTION_MAP`, the date strptime format, and `_parse_option_symbol` regex accordingly. Also update `SAMPLE_CSV` in the test file to use real column names.

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_csv_parser.py`:

```python
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
```

- [ ] **Step 2: Run tests — expect fail**

```bash
cd backend && pytest tests/test_csv_parser.py -v
```

Expected: ImportError — module doesn't exist.

- [ ] **Step 3: Create `backend/services/csv_parser.py`**

```python
import csv
from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional
import re


class ParseError(Exception):
    pass


# Maps Wealthsimple action strings to normalized action names.
# UPDATE these keys to match your actual Wealthsimple CSV export.
ACTION_MAP = {
    "Buy to Open": "buy_to_open",
    "Sell to Open": "sell_to_open",
    "Buy to Close": "buy_to_close",
    "Sell to Close": "sell_to_close",
}

# Maps Wealthsimple CSV column headers to internal field names.
# UPDATE these keys to match your actual Wealthsimple CSV export.
COLUMN_MAP = {
    "Date": "date",
    "Action": "action",
    "Symbol": "symbol_raw",
    "Description": "description",
    "Quantity": "quantity",
    "Price": "price",
    "Amount": "amount",
}

REQUIRED_COLUMNS = set(COLUMN_MAP.keys())


def _parse_option_symbol(symbol_raw: str) -> dict:
    """
    Parse OCC-style option symbol: 'AAPL 2026-01-31 180.00 P'
    Returns dict with underlying, expiry, strike, option_type.
    Adjust regex if Wealthsimple uses a different symbol format.
    """
    pattern = r"^(\w+)\s+(\d{4}-\d{2}-\d{2})\s+([\d.]+)\s+([CP])$"
    match = re.match(pattern, symbol_raw.strip())
    if not match:
        raise ParseError(f"Cannot parse option symbol: {symbol_raw!r}")
    underlying, expiry_str, strike_str, opt_type = match.groups()
    return {
        "symbol": underlying,
        "expiry": datetime.strptime(expiry_str, "%Y-%m-%d").date(),
        "strike": float(strike_str),
        "option_type": "call" if opt_type == "C" else "put",
    }


def parse_wealthsimple_csv(filepath: str) -> list[dict]:
    """
    Parse a Wealthsimple options CSV export.
    Returns a list of normalized raw trade row dicts.
    """
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise ParseError(f"Missing required columns: {missing}")

        rows = []
        for i, row in enumerate(reader, start=2):
            action_raw = row["Action"].strip()
            action = ACTION_MAP.get(action_raw)
            if action is None:
                continue  # skip non-options rows (e.g. dividends, stock purchases)

            try:
                parsed_symbol = _parse_option_symbol(row["Symbol"])
            except ParseError:
                continue  # skip rows that don't match option symbol format

            rows.append({
                "date": datetime.strptime(row["Date"].strip(), "%Y-%m-%d"),
                "action": action,
                "symbol": parsed_symbol["symbol"],
                "option_type": parsed_symbol["option_type"],
                "strike": parsed_symbol["strike"],
                "expiry": parsed_symbol["expiry"],
                "quantity": int(float(row["Quantity"].strip())),
                "price": abs(float(row["Price"].strip())),
                "amount": float(row["Amount"].strip()),
                "symbol_raw": row["Symbol"].strip(),
            })
        return rows
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd backend && pytest tests/test_csv_parser.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/services/csv_parser.py backend/tests/test_csv_parser.py
git commit -m "feat: Wealthsimple CSV parser with OCC symbol parsing"
```

---

### Task 4: Trade Matcher

**Files:**
- Create: `backend/services/trade_matcher.py`
- Create: `backend/tests/test_trade_matcher.py`

The matcher takes raw parsed rows and groups them into complete `Trade` + `TradeLeg` records. A trade is matched when an open row (buy_to_open or sell_to_open) is paired with a close row (buy_to_close or sell_to_close) on the same symbol + strike + expiry + option_type. Unmatched open rows become open trades.

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_trade_matcher.py`:

```python
import pytest
from datetime import datetime, date
from backend.services.trade_matcher import match_trades


def _row(action, symbol, option_type, strike, expiry_str, price, qty=1, dt_str="2026-01-10"):
    return {
        "date": datetime.strptime(dt_str, "%Y-%m-%d"),
        "action": action,
        "symbol": symbol,
        "option_type": option_type,
        "strike": strike,
        "expiry": date.fromisoformat(expiry_str),
        "quantity": qty,
        "price": price,
        "amount": price * qty * 100 * (-1 if "open" in action and "sell" not in action else 1),
        "symbol_raw": f"{symbol} {expiry_str} {strike} {'C' if option_type == 'call' else 'P'}",
    }


def test_matched_csp_produces_one_closed_trade():
    rows = [
        _row("sell_to_open", "AAPL", "put", 180.0, "2026-01-31", 1.20, dt_str="2026-01-10"),
        _row("buy_to_close", "AAPL", "put", 180.0, "2026-01-31", 0.20, dt_str="2026-01-25"),
    ]
    trades = match_trades(rows)
    assert len(trades) == 1
    t = trades[0]
    assert t["status"] == "closed"
    assert t["strategy"] == "csp"
    assert t["symbol"] == "AAPL"
    assert t["premium_collected"] == 1.20 * 100
    assert t["pnl"] == pytest.approx((1.20 - 0.20) * 100, rel=0.01)
    assert len(t["legs"]) == 1


def test_unmatched_sell_open_produces_open_trade():
    rows = [
        _row("sell_to_open", "TSLA", "put", 220.0, "2026-02-28", 2.50),
    ]
    trades = match_trades(rows)
    assert len(trades) == 1
    assert trades[0]["status"] == "open"
    assert trades[0]["pnl"] is None


def test_covered_call_strategy_detected():
    rows = [
        _row("sell_to_open", "SPY", "call", 500.0, "2026-02-07", 0.85, dt_str="2026-01-15"),
        _row("buy_to_close", "SPY", "call", 500.0, "2026-02-07", 0.30, dt_str="2026-02-01"),
    ]
    trades = match_trades(rows)
    assert trades[0]["strategy"] == "covered_call"


def test_multiple_trades_same_symbol():
    rows = [
        _row("sell_to_open", "AAPL", "put", 180.0, "2026-01-31", 1.20, dt_str="2026-01-05"),
        _row("buy_to_close", "AAPL", "put", 180.0, "2026-01-31", 0.20, dt_str="2026-01-20"),
        _row("sell_to_open", "AAPL", "put", 175.0, "2026-02-28", 1.50, dt_str="2026-01-25"),
        _row("buy_to_close", "AAPL", "put", 175.0, "2026-02-28", 0.50, dt_str="2026-02-15"),
    ]
    trades = match_trades(rows)
    assert len(trades) == 2
    assert all(t["status"] == "closed" for t in trades)
```

- [ ] **Step 2: Run tests — expect fail**

```bash
cd backend && pytest tests/test_trade_matcher.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `backend/services/trade_matcher.py`**

```python
from datetime import datetime, date
from typing import Optional


def _infer_strategy(option_type: str, side: str) -> str:
    """
    Infer strategy from a single-leg trade.
    Note: CSV import cannot distinguish a covered call from a naked short call
    (no 'shares held' data). We default short calls to 'covered_call' since
    this app targets premium sellers. If you want to track naked short calls,
    manually update the strategy field after import via the Trade Log.
    """
    if side == "sell" and option_type == "put":
        return "csp"
    if side == "sell" and option_type == "call":
        return "covered_call"  # assumes covered; update manually if naked short call
    if side == "buy" and option_type == "call":
        return "long_call"
    if side == "buy" and option_type == "put":
        return "long_put"
    return "csp"  # fallback, should not be reached


def _leg_key(row: dict) -> tuple:
    """Unique key for matching open/close rows."""
    return (row["symbol"], row["option_type"], row["strike"], row["expiry"])


def match_trades(rows: list[dict]) -> list[dict]:
    """
    Match open and close rows into complete trade dicts.
    Returns list of trade dicts ready for DB insertion.
    Each dict has: symbol, strategy, status, opened_at, closed_at,
    premium_collected, pnl, broker, dte_entry, legs (list of leg dicts).
    """
    import uuid

    # Sort chronologically
    sorted_rows = sorted(rows, key=lambda r: r["date"])

    # Track open positions: key → list of open rows (FIFO)
    open_positions: dict[tuple, list[dict]] = {}
    trades: list[dict] = []

    for row in sorted_rows:
        action = row["action"]
        key = _leg_key(row)

        if action in ("buy_to_open", "sell_to_open"):
            open_positions.setdefault(key, []).append(row)

        elif action in ("buy_to_close", "sell_to_close"):
            if key in open_positions and open_positions[key]:
                open_row = open_positions[key].pop(0)
                if not open_positions[key]:
                    del open_positions[key]

                open_side = "sell" if open_row["action"] == "sell_to_open" else "buy"
                strategy = _infer_strategy(open_row["option_type"], open_side)
                premium_collected = open_row["price"] * open_row["quantity"] * 100

                # P&L for premium seller: collected - cost to close
                if open_side == "sell":
                    pnl = (open_row["price"] - row["price"]) * open_row["quantity"] * 100
                else:
                    pnl = (row["price"] - open_row["price"]) * open_row["quantity"] * 100

                expiry: date = open_row["expiry"]
                opened_at: datetime = open_row["date"]
                dte_entry = (expiry - opened_at.date()).days

                trade_id = str(uuid.uuid4())
                trades.append({
                    "id": trade_id,
                    "symbol": open_row["symbol"],
                    "strategy": strategy,
                    "status": "closed",
                    "opened_at": opened_at,
                    "closed_at": row["date"],
                    "premium_collected": premium_collected if open_side == "sell" else None,
                    "pnl": round(pnl, 2),
                    "broker": "wealthsimple",
                    "dte_entry": dte_entry,
                    "legs": [{
                        "id": str(uuid.uuid4()),
                        "trade_id": trade_id,
                        "option_type": open_row["option_type"],
                        "side": open_side,
                        "strike": open_row["strike"],
                        "expiry": expiry,
                        "contracts": open_row["quantity"],
                        "price_open": open_row["price"],
                        "price_close": row["price"],
                    }],
                })

    # Remaining open positions become open trades
    for key, open_rows in open_positions.items():
        for open_row in open_rows:
            open_side = "sell" if open_row["action"] == "sell_to_open" else "buy"
            strategy = _infer_strategy(open_row["option_type"], open_side)
            expiry: date = open_row["expiry"]
            opened_at: datetime = open_row["date"]
            dte_entry = (expiry - opened_at.date()).days
            trade_id = str(uuid.uuid4())
            trades.append({
                "id": trade_id,
                "symbol": open_row["symbol"],
                "strategy": strategy,
                "status": "open",
                "opened_at": opened_at,
                "closed_at": None,
                "premium_collected": open_row["price"] * open_row["quantity"] * 100 if open_side == "sell" else None,
                "pnl": None,
                "broker": "wealthsimple",
                "dte_entry": dte_entry,
                "legs": [{
                    "id": str(uuid.uuid4()),
                    "trade_id": trade_id,
                    "option_type": open_row["option_type"],
                    "side": open_side,
                    "strike": open_row["strike"],
                    "expiry": expiry,
                    "contracts": open_row["quantity"],
                    "price_open": open_row["price"],
                    "price_close": None,
                }],
            })

    return trades
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd backend && pytest tests/test_trade_matcher.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/services/trade_matcher.py backend/tests/test_trade_matcher.py
git commit -m "feat: trade matcher — groups CSV rows into complete Trade records"
```

---

## Chunk 3: Analytics Engine + Wheel Detector

### Task 5: Analytics Engine

**Files:**
- Create: `backend/services/analytics_engine.py`
- Create: `backend/tests/test_analytics_engine.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_analytics_engine.py`:

```python
import pytest
from backend.services.analytics_engine import (
    compute_overview,
    compute_by_dimension,
    compute_edge_patterns,
)


def _trade(pnl, strategy="csp", dte=21, iv_rank=60, symbol="AAPL"):
    return {
        "pnl": pnl,
        "status": "closed",
        "strategy": strategy,
        "dte_entry": dte,
        "iv_rank_entry": iv_rank,
        "symbol": symbol,
        "premium_collected": abs(pnl) * 1.5 if pnl else None,
    }


TRADES = [
    _trade(100, strategy="csp", dte=21, iv_rank=70),
    _trade(80, strategy="csp", dte=25, iv_rank=65),
    _trade(-50, strategy="csp", dte=5, iv_rank=20),
    _trade(60, strategy="covered_call", dte=30, iv_rank=55),
    _trade(-40, strategy="covered_call", dte=3, iv_rank=15),
    _trade(90, strategy="csp", dte=28, iv_rank=80),
]


def test_overview_win_rate():
    result = compute_overview(TRADES)
    assert result["win_rate"] == pytest.approx(4 / 6, rel=0.01)
    assert result["total_trades"] == 6
    assert result["winning_trades"] == 4


def test_overview_total_pnl():
    result = compute_overview(TRADES)
    assert result["total_pnl"] == pytest.approx(240.0, rel=0.01)


def test_overview_profit_factor():
    result = compute_overview(TRADES)
    total_wins = 100 + 80 + 60 + 90
    total_losses = 50 + 40
    assert result["profit_factor"] == pytest.approx(total_wins / total_losses, rel=0.01)


def test_by_dimension_strategy():
    result = compute_by_dimension(TRADES, dimension="strategy")
    csp = next(r for r in result if r["label"] == "csp")
    assert csp["win_rate"] == pytest.approx(3 / 4, rel=0.01)
    assert csp["trade_count"] == 4


def test_by_dimension_dte_buckets():
    result = compute_by_dimension(TRADES, dimension="dte")
    labels = [r["label"] for r in result]
    assert "0-7 DTE" in labels
    assert "21-35 DTE" in labels


def test_edge_patterns_identifies_high_iv_rank():
    result = compute_edge_patterns(TRADES)
    high_iv = next((p for p in result["best"] if "IV Rank" in p["condition"]), None)
    assert high_iv is not None
    assert high_iv["win_rate"] > 0.7


def test_edge_patterns_identifies_low_dte_weakness():
    result = compute_edge_patterns(TRADES)
    low_dte = next((p for p in result["worst"] if "DTE" in p["condition"]), None)
    assert low_dte is not None
    assert low_dte["win_rate"] < 0.6


def test_empty_trades_returns_zeros():
    result = compute_overview([])
    assert result["win_rate"] == 0
    assert result["total_pnl"] == 0
```

- [ ] **Step 2: Run tests — expect fail**

```bash
cd backend && pytest tests/test_analytics_engine.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `backend/services/analytics_engine.py`**

```python
from typing import Literal

DTE_BUCKETS = [
    ("0-7 DTE", 0, 7),
    ("8-14 DTE", 8, 14),
    ("15-20 DTE", 15, 20),
    ("21-35 DTE", 21, 35),
    ("36+ DTE", 36, 9999),
]

IV_RANK_BUCKETS = [
    ("IV < 25", 0, 24),
    ("IV 25-49", 25, 49),
    ("IV 50-74", 50, 74),
    ("IV 75+", 75, 100),
]


def _win_rate_and_pnl(trades: list[dict]) -> dict:
    closed = [t for t in trades if t["status"] == "closed" and t["pnl"] is not None]
    if not closed:
        return {"win_rate": 0, "total_pnl": 0, "trade_count": 0,
                "winning_trades": 0, "profit_factor": 0, "avg_premium": 0}
    wins = [t for t in closed if t["pnl"] > 0]
    losses = [t for t in closed if t["pnl"] <= 0]
    total_win = sum(t["pnl"] for t in wins)
    total_loss = abs(sum(t["pnl"] for t in losses))
    premiums = [t["premium_collected"] for t in closed if t.get("premium_collected")]
    return {
        "win_rate": len(wins) / len(closed),
        "total_pnl": round(sum(t["pnl"] for t in closed), 2),
        "trade_count": len(closed),
        "winning_trades": len(wins),
        "profit_factor": round(total_win / total_loss, 2) if total_loss > 0 else None,
        "avg_premium": round(sum(premiums) / len(premiums), 2) if premiums else 0,
    }


def compute_overview(trades: list[dict]) -> dict:
    return _win_rate_and_pnl(trades)


def compute_by_dimension(
    trades: list[dict],
    dimension: Literal["strategy", "symbol", "dte", "iv_rank"],
) -> list[dict]:
    """Segment trades by dimension, return stats per segment."""
    closed = [t for t in trades if t["status"] == "closed" and t["pnl"] is not None]
    results = []

    if dimension == "strategy":
        strategies = sorted(set(t["strategy"] for t in closed))
        for s in strategies:
            subset = [t for t in closed if t["strategy"] == s]
            stats = _win_rate_and_pnl(subset)
            results.append({"label": s, **stats})

    elif dimension == "symbol":
        symbols = sorted(set(t["symbol"] for t in closed))
        for sym in symbols:
            subset = [t for t in closed if t["symbol"] == sym]
            stats = _win_rate_and_pnl(subset)
            results.append({"label": sym, **stats})

    elif dimension == "dte":
        for label, lo, hi in DTE_BUCKETS:
            subset = [t for t in closed if t.get("dte_entry") is not None and lo <= t["dte_entry"] <= hi]
            if subset:
                stats = _win_rate_and_pnl(subset)
                results.append({"label": label, **stats})

    elif dimension == "iv_rank":
        for label, lo, hi in IV_RANK_BUCKETS:
            subset = [t for t in closed if t.get("iv_rank_entry") is not None and lo <= t["iv_rank_entry"] <= hi]
            if subset:
                stats = _win_rate_and_pnl(subset)
                results.append({"label": label, **stats})

    return sorted(results, key=lambda r: r["win_rate"], reverse=True)


def compute_edge_patterns(trades: list[dict]) -> dict:
    """
    Surface top winning and losing conditions across DTE and IV rank dimensions.
    Returns {"best": [...], "worst": [...]} with condition, win_rate, trade_count.
    """
    closed = [t for t in trades if t["status"] == "closed" and t["pnl"] is not None]
    if len(closed) < 3:
        return {"best": [], "worst": []}

    overall_win_rate = len([t for t in closed if t["pnl"] > 0]) / len(closed)
    patterns = []

    # DTE patterns
    for label, lo, hi in DTE_BUCKETS:
        subset = [t for t in closed if t.get("dte_entry") is not None and lo <= t["dte_entry"] <= hi]
        if len(subset) >= 3:
            wr = len([t for t in subset if t["pnl"] > 0]) / len(subset)
            patterns.append({"condition": f"DTE {label}", "win_rate": round(wr, 3), "trade_count": len(subset)})

    # IV rank patterns
    for label, lo, hi in IV_RANK_BUCKETS:
        subset = [t for t in closed if t.get("iv_rank_entry") is not None and lo <= t["iv_rank_entry"] <= hi]
        if len(subset) >= 3:
            wr = len([t for t in subset if t["pnl"] > 0]) / len(subset)
            patterns.append({"condition": f"IV Rank {label}", "win_rate": round(wr, 3), "trade_count": len(subset)})

    best = sorted([p for p in patterns if p["win_rate"] > overall_win_rate], key=lambda x: -x["win_rate"])[:3]
    worst = sorted([p for p in patterns if p["win_rate"] <= overall_win_rate], key=lambda x: x["win_rate"])[:3]
    return {"best": best, "worst": worst}
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd backend && pytest tests/test_analytics_engine.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/services/analytics_engine.py backend/tests/test_analytics_engine.py
git commit -m "feat: analytics engine — win rate, P&L, profit factor, edge patterns"
```

---

### Task 6: Wheel Detector

**Files:**
- Create: `backend/services/wheel_detector.py`
- Create: `backend/tests/test_wheel_detector.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_wheel_detector.py`:

```python
from datetime import datetime
from backend.services.wheel_detector import detect_wheel_candidates


def _trade(strategy, symbol, opened_at_str, status="closed"):
    return {
        "id": f"{strategy}-{symbol}-{opened_at_str}",
        "symbol": symbol,
        "strategy": strategy,
        "status": status,
        "opened_at": datetime.fromisoformat(opened_at_str),
    }


def test_detects_csp_followed_by_covered_call():
    trades = [
        _trade("csp", "TSLA", "2026-01-05"),
        _trade("covered_call", "TSLA", "2026-01-20"),
    ]
    suggestions = detect_wheel_candidates(trades)
    assert len(suggestions) == 1
    assert suggestions[0]["symbol"] == "TSLA"
    assert len(suggestions[0]["trade_ids"]) == 2


def test_no_suggestion_for_single_csp():
    trades = [_trade("csp", "AAPL", "2026-01-10")]
    suggestions = detect_wheel_candidates(trades)
    assert len(suggestions) == 0


def test_no_suggestion_for_unrelated_strategies():
    trades = [
        _trade("long_call", "AAPL", "2026-01-10"),
        _trade("long_put", "AAPL", "2026-01-15"),
    ]
    suggestions = detect_wheel_candidates(trades)
    assert len(suggestions) == 0


def test_multiple_symbols_detected_separately():
    trades = [
        _trade("csp", "TSLA", "2026-01-05"),
        _trade("covered_call", "TSLA", "2026-01-20"),
        _trade("csp", "AAPL", "2026-01-08"),
        _trade("covered_call", "AAPL", "2026-01-22"),
    ]
    suggestions = detect_wheel_candidates(trades)
    assert len(suggestions) == 2
    symbols = {s["symbol"] for s in suggestions}
    assert symbols == {"TSLA", "AAPL"}
```

- [ ] **Step 2: Run tests — expect fail**

```bash
cd backend && pytest tests/test_wheel_detector.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `backend/services/wheel_detector.py`**

```python
from itertools import groupby

WHEEL_STRATEGIES = {"csp", "covered_call"}


def detect_wheel_candidates(trades: list[dict]) -> list[dict]:
    """
    Scan trades for CSP → covered_call sequences on the same symbol.
    Returns a list of suggestions: {symbol, trade_ids, suggested_name}.
    Only surfaces groups not already linked to a campaign (campaign_id is None).
    """
    # Filter to unlinked wheel-eligible trades
    eligible = [
        t for t in trades
        if t["strategy"] in WHEEL_STRATEGIES and not t.get("campaign_id")
    ]

    # Group by symbol
    by_symbol: dict[str, list[dict]] = {}
    for t in eligible:
        by_symbol.setdefault(t["symbol"], []).append(t)

    suggestions = []
    for symbol, symbol_trades in by_symbol.items():
        sorted_trades = sorted(symbol_trades, key=lambda t: t["opened_at"])
        strategies = [t["strategy"] for t in sorted_trades]

        # Must have at least one CSP and one covered_call
        if "csp" not in strategies or "covered_call" not in strategies:
            continue

        # Must have CSP before covered_call
        first_csp_idx = strategies.index("csp")
        try:
            first_cc_idx = strategies.index("covered_call")
        except ValueError:
            continue

        if first_csp_idx >= first_cc_idx:
            continue

        trade_ids = [t["id"] for t in sorted_trades]
        suggestions.append({
            "symbol": symbol,
            "trade_ids": trade_ids,
            "suggested_name": f"{symbol} Wheel",
            "trade_count": len(sorted_trades),
        })

    return suggestions
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd backend && pytest tests/test_wheel_detector.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Run all backend tests together**

```bash
cd backend && pytest tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/services/wheel_detector.py backend/tests/test_wheel_detector.py
git commit -m "feat: wheel detector — surfaces CSP→CC sequences as campaign suggestions"
```

---

## Chunk 4: API Endpoints + Schemas

### Task 7: Pydantic Schemas

**Files:**
- Create: `backend/schemas/trade.py`
- Create: `backend/schemas/campaign.py`
- Create: `backend/schemas/analytics.py`

- [ ] **Step 1: Create `backend/schemas/trade.py`**

```python
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
```

- [ ] **Step 2: Create `backend/schemas/campaign.py`**

```python
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
```

- [ ] **Step 3: Create `backend/schemas/analytics.py`**

```python
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
```

- [ ] **Step 4: Commit**

```bash
git add backend/schemas/
git commit -m "feat: Pydantic schemas for API request/response contracts"
```

---

### Task 8: API Routers

**Files:**
- Create: `backend/routers/trades.py`
- Create: `backend/routers/imports.py`
- Create: `backend/routers/analytics.py`
- Create: `backend/routers/campaigns.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create `backend/routers/trades.py`**

```python
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
```

- [ ] **Step 2: Create `backend/routers/imports.py`**

```python
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
```

- [ ] **Step 3: Create `backend/routers/analytics.py`**

```python
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
```

- [ ] **Step 4: Create `backend/routers/campaigns.py`**

```python
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
```

- [ ] **Step 5: Register routers in `backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Base, engine
from backend.routers import trades, imports, analytics, campaigns

app = FastAPI(title="Options Buddy", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(trades.router)
app.include_router(imports.router)
app.include_router(analytics.router)
app.include_router(campaigns.router)
```

- [ ] **Step 6: Add router integration tests**

Create `backend/tests/test_routers.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, get_db
from backend.main import app

@pytest.fixture(scope="function")
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_trades_empty(client):
    res = client.get("/trades/")
    assert res.status_code == 200
    assert res.json() == []


def test_analytics_overview_empty(client):
    res = client.get("/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["win_rate"] == 0
    assert data["total_pnl"] == 0


def test_campaigns_create_and_list(client):
    res = client.post("/campaigns/", json={"name": "TSLA Wheel", "symbol": "TSLA"})
    assert res.status_code == 200
    data = res.json()
    assert data["symbol"] == "TSLA"
    assert data["status"] == "active"

    res2 = client.get("/campaigns/")
    assert res2.status_code == 200
    assert len(res2.json()) == 1


def test_campaign_complete(client):
    res = client.post("/campaigns/", json={"name": "AAPL Wheel", "symbol": "AAPL"})
    cid = res.json()["id"]
    res2 = client.patch(f"/campaigns/{cid}/complete")
    assert res2.status_code == 200
    campaigns = client.get("/campaigns/").json()
    assert campaigns[0]["status"] == "completed"
```

- [ ] **Step 7: Run integration tests**

```bash
cd backend && pytest tests/test_routers.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 8: Verify API docs load**

```bash
cd backend && uvicorn main:app --reload
```

Visit http://127.0.0.1:8000/docs — all routers should appear: `/trades`, `/import`, `/analytics/*`, `/campaigns`.

- [ ] **Step 9: Run all backend tests**

```bash
cd backend && pytest tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 10: Commit**

```bash
git add backend/routers/ backend/schemas/ backend/tests/test_routers.py backend/main.py
git commit -m "feat: API routers for trades, import, analytics, campaigns + integration tests"
```

---

## Chunk 5: React Frontend

### Task 9: Frontend scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/api/client.js`

- [ ] **Step 1: Scaffold React + Vite project**

```bash
cd frontend
npm create vite@latest . -- --template react
npm install
npm install react-router-dom recharts
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

- [ ] **Step 2: Configure `frontend/tailwind.config.js`**

```js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#1e293b",
        base: "#0f172a",
        border: "#334155",
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 3: Update `frontend/src/index.css`** — replace entire file:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #0f172a;
  color: #f8fafc;
  font-family: system-ui, sans-serif;
}
```

- [ ] **Step 4: Create `frontend/src/api/client.js`**

```js
const BASE_URL = "http://localhost:8000"

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || "Request failed")
  }
  return res.json()
}

export const api = {
  get: (path) => request(path),
  patch: (path, body) => request(path, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }),
  post: (path, body) => request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }),
  uploadCSV: (file) => {
    const form = new FormData()
    form.append("file", file)
    return request("/import/csv", { method: "POST", body: form })
  },
}
```

- [ ] **Step 5: Create `frontend/src/App.jsx`**

```jsx
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom"
import Dashboard from "./pages/Dashboard"
import Analytics from "./pages/Analytics"
import TradeLog from "./pages/TradeLog"
import Campaigns from "./pages/Campaigns"

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/analytics", label: "Analytics" },
  { to: "/trades", label: "Trade Log" },
  { to: "/campaigns", label: "Campaigns" },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        <nav className="w-48 bg-surface border-r border-border p-4 flex flex-col gap-1 shrink-0">
          <div className="text-lg font-bold text-white mb-6 px-2">Options Buddy</div>
          {navItems.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `px-3 py-2 rounded text-sm transition-colors ${
                  isActive
                    ? "bg-blue-700 text-white"
                    : "text-slate-400 hover:text-white hover:bg-slate-700"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 p-6 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/trades" element={<TradeLog />} />
            <Route path="/campaigns" element={<Campaigns />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
```

- [ ] **Step 6: Create stub pages** — create each file with just an `<h1>` so routing works:

`frontend/src/pages/Dashboard.jsx`:
```jsx
export default function Dashboard() { return <h1 className="text-2xl font-bold">Dashboard</h1> }
```

`frontend/src/pages/Analytics.jsx`:
```jsx
export default function Analytics() { return <h1 className="text-2xl font-bold">Analytics</h1> }
```

`frontend/src/pages/TradeLog.jsx`:
```jsx
export default function TradeLog() { return <h1 className="text-2xl font-bold">Trade Log</h1> }
```

`frontend/src/pages/Campaigns.jsx`:
```jsx
export default function Campaigns() { return <h1 className="text-2xl font-bold">Campaigns</h1> }
```

- [ ] **Step 7: Update `frontend/src/main.jsx`**

```jsx
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./index.css"
import App from "./App"

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
)
```

- [ ] **Step 8: Verify frontend runs**

```bash
cd frontend && npm run dev
```

Expected: App loads at http://localhost:5173 with sidebar nav and stub pages.

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat: React + Vite frontend scaffold with routing and nav"
```

---

### Task 10: Shared hooks and components

**Files:**
- Create: `frontend/src/hooks/useTrades.js`
- Create: `frontend/src/hooks/useAnalytics.js`
- Create: `frontend/src/hooks/useCampaigns.js`
- Create: `frontend/src/components/MetricCard.jsx`
- Create: `frontend/src/components/PnLChart.jsx`
- Create: `frontend/src/components/WinRateBar.jsx`
- Create: `frontend/src/components/EdgePanel.jsx`
- Create: `frontend/src/components/TradeTable.jsx`
- Create: `frontend/src/components/CSVUpload.jsx`

- [ ] **Step 1: Create `frontend/src/hooks/useTrades.js`**

```js
import { useState, useEffect } from "react"
import { api } from "../api/client"

export function useTrades(filters = {}) {
  const [trades, setTrades] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const params = new URLSearchParams(
    Object.fromEntries(Object.entries(filters).filter(([, v]) => v != null))
  ).toString()

  useEffect(() => {
    setLoading(true)
    api.get(`/trades${params ? "?" + params : ""}`)
      .then(setTrades)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [params])

  return { trades, loading, error }
}
```

- [ ] **Step 2: Create `frontend/src/hooks/useAnalytics.js`**

```js
import { useState, useEffect } from "react"
import { api } from "../api/client"

export function useAnalytics(endpoint) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    api.get(`/analytics/${endpoint}`)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [endpoint])

  return { data, loading, error }
}
```

- [ ] **Step 3: Create `frontend/src/hooks/useCampaigns.js`**

```js
import { useState, useEffect } from "react"
import { api } from "../api/client"

export function useCampaigns() {
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = () => {
    setLoading(true)
    api.get("/campaigns")
      .then(setCampaigns)
      .catch(setError)
      .finally(() => setLoading(false))
  }

  useEffect(() => { refresh() }, [])
  return { campaigns, loading, error, refresh }
}
```

- [ ] **Step 4: Create `frontend/src/components/MetricCard.jsx`**

```jsx
export default function MetricCard({ value, label, subLabel, color = "text-emerald-400" }) {
  return (
    <div className="bg-surface rounded-lg p-4 text-center">
      <div className={`text-2xl font-bold ${color}`}>{value ?? "—"}</div>
      <div className="text-slate-400 text-sm mt-1">{label}</div>
      {subLabel && <div className="text-slate-500 text-xs mt-0.5">{subLabel}</div>}
    </div>
  )
}
```

- [ ] **Step 5: Create `frontend/src/components/PnLChart.jsx`**

```jsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceDot } from "recharts"

export default function PnLChart({ trades }) {
  // Build cumulative P&L series from closed trades sorted by close date
  const sorted = [...trades]
    .filter(t => t.status === "closed" && t.pnl != null && t.closed_at)
    .sort((a, b) => new Date(a.closed_at) - new Date(b.closed_at))

  let cumulative = 0
  const data = sorted.map(t => {
    cumulative += t.pnl
    return {
      date: new Date(t.closed_at).toLocaleDateString("en-CA"),
      pnl: Math.round(cumulative * 100) / 100,
      loss: t.pnl < 0,
    }
  })

  const lossDots = data
    .map((d, i) => ({ ...d, index: i }))
    .filter(d => d.loss)

  if (data.length === 0) {
    return <div className="bg-surface rounded-lg p-6 text-slate-500 text-sm text-center">No closed trades yet</div>
  }

  return (
    <div className="bg-surface rounded-lg p-4">
      <div className="text-slate-400 text-xs font-semibold uppercase tracking-wide mb-3">Cumulative P&L</div>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data}>
          <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#64748b" }} tickLine={false} />
          <YAxis tick={{ fontSize: 10, fill: "#64748b" }} tickLine={false} axisLine={false}
            tickFormatter={v => `$${v}`} />
          <Tooltip
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 6 }}
            labelStyle={{ color: "#94a3b8" }}
            formatter={v => [`$${v}`, "Cumulative P&L"]}
          />
          <Line type="monotone" dataKey="pnl" stroke="#10b981" strokeWidth={2} dot={false} />
          {lossDots.map((d) => (
            <ReferenceDot key={d.index} x={d.date} y={d.pnl} r={4} fill="#ef4444" stroke="none" />
          ))}
        </LineChart>
      </ResponsiveContainer>
      <div className="text-slate-500 text-xs mt-1 text-right">Red dots = losing trades</div>
    </div>
  )
}
```

- [ ] **Step 6: Create `frontend/src/components/WinRateBar.jsx`**

```jsx
function Bar({ label, winRate, tradeCount }) {
  const pct = Math.round(winRate * 100)
  const color = pct >= 70 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-400" : "bg-red-500"
  const textColor = pct >= 70 ? "text-emerald-400" : pct >= 50 ? "text-amber-400" : "text-red-400"
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span className={textColor}>{pct}% <span className="text-slate-500">({tradeCount})</span></span>
      </div>
      <div className="bg-base rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function WinRateBar({ data, title }) {
  if (!data?.length) return null
  return (
    <div className="bg-surface rounded-lg p-4">
      <div className="text-slate-400 text-xs font-semibold uppercase tracking-wide mb-3">{title}</div>
      <div className="flex flex-col gap-3">
        {data.map(row => (
          <Bar key={row.label} label={row.label} winRate={row.win_rate} tradeCount={row.trade_count} />
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 7: Create `frontend/src/components/EdgePanel.jsx`**

```jsx
export default function EdgePanel({ edge }) {
  if (!edge) return null
  const { best, worst } = edge
  if (!best?.length && !worst?.length) {
    return (
      <div className="bg-surface border border-slate-700 rounded-lg p-4 text-slate-500 text-sm">
        Import more trades to surface your edge patterns.
      </div>
    )
  }
  return (
    <div className="bg-surface border border-blue-900 rounded-lg p-4">
      <div className="text-blue-400 text-sm font-bold mb-3">⚡ Your Edge</div>
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-base border-l-2 border-emerald-500 rounded p-3">
          <div className="text-emerald-400 text-xs font-semibold mb-2">Best Conditions</div>
          {best.map(p => (
            <div key={p.condition} className="text-slate-300 text-xs leading-relaxed">
              • {p.condition}: <strong className="text-emerald-400">{Math.round(p.win_rate * 100)}% win</strong>
              <span className="text-slate-500"> ({p.trade_count} trades)</span>
            </div>
          ))}
        </div>
        <div className="bg-base border-l-2 border-red-500 rounded p-3">
          <div className="text-red-400 text-xs font-semibold mb-2">Where You Lose</div>
          {worst.map(p => (
            <div key={p.condition} className="text-slate-300 text-xs leading-relaxed">
              • {p.condition}: <strong className="text-red-400">{Math.round(p.win_rate * 100)}% win</strong>
              <span className="text-slate-500"> ({p.trade_count} trades)</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 8: Create `frontend/src/components/TradeTable.jsx`**

```jsx
import { useState } from "react"

const STRATEGY_COLORS = {
  csp: "text-emerald-400", covered_call: "text-blue-400",
  credit_spread: "text-amber-400", long_call: "text-purple-400",
  long_put: "text-pink-400", debit_spread: "text-orange-400",
}

export default function TradeTable({ trades }) {
  const [sortField, setSortField] = useState("opened_at")
  const [sortDir, setSortDir] = useState("desc")

  const toggleSort = (field) => {
    if (sortField === field) setSortDir(d => d === "asc" ? "desc" : "asc")
    else { setSortField(field); setSortDir("desc") }
  }

  const sorted = [...trades].sort((a, b) => {
    const va = a[sortField], vb = b[sortField]
    if (va == null) return 1
    if (vb == null) return -1
    return sortDir === "asc" ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1)
  })

  const cols = [
    { key: "opened_at", label: "Date" },
    { key: "symbol", label: "Symbol" },
    { key: "strategy", label: "Strategy" },
    { key: "dte_entry", label: "DTE" },
    { key: "premium_collected", label: "Premium" },
    { key: "pnl", label: "P&L" },
    { key: "status", label: "Status" },
  ]

  return (
    <div className="bg-surface rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            {cols.map(c => (
              <th key={c.key}
                className="px-4 py-3 text-left text-xs text-slate-400 uppercase tracking-wide cursor-pointer hover:text-white"
                onClick={() => toggleSort(c.key)}>
                {c.label} {sortField === c.key ? (sortDir === "asc" ? "↑" : "↓") : ""}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map(t => (
            <tr key={t.id} className="border-b border-border/50 hover:bg-slate-800 transition-colors">
              <td className="px-4 py-3 text-slate-400 text-xs">
                {new Date(t.opened_at).toLocaleDateString("en-CA")}
              </td>
              <td className="px-4 py-3 font-semibold">{t.symbol}</td>
              <td className={`px-4 py-3 text-xs ${STRATEGY_COLORS[t.strategy] || "text-slate-300"}`}>
                {t.strategy.replace("_", " ")}
              </td>
              <td className="px-4 py-3 text-slate-400">{t.dte_entry ?? "—"}</td>
              <td className="px-4 py-3 text-slate-300">
                {t.premium_collected != null ? `$${t.premium_collected.toFixed(0)}` : "—"}
              </td>
              <td className={`px-4 py-3 font-semibold ${t.pnl == null ? "text-slate-500" : t.pnl >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                {t.pnl == null ? "Open" : `${t.pnl >= 0 ? "+" : ""}$${t.pnl.toFixed(0)}`}
              </td>
              <td className="px-4 py-3">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  t.status === "closed" ? "bg-slate-700 text-slate-300" :
                  t.status === "open" ? "bg-blue-900 text-blue-300" : "bg-slate-600 text-slate-400"
                }`}>{t.status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {sorted.length === 0 && (
        <div className="p-8 text-center text-slate-500 text-sm">No trades found</div>
      )}
    </div>
  )
}
```

- [ ] **Step 9: Create `frontend/src/components/CSVUpload.jsx`**

```jsx
import { useState, useRef } from "react"
import { api } from "../api/client"

export default function CSVUpload({ onImportComplete }) {
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const inputRef = useRef()

  const handleFile = async (file) => {
    if (!file) return
    setLoading(true)
    setResult(null)
    try {
      const res = await api.uploadCSV(file)
      setResult(res)
      if (onImportComplete) onImportComplete(res)
    } catch (e) {
      setResult({ status: "failed", errors: [e.message], trades_added: 0, wheel_suggestions: [] })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]) }}
        onClick={() => inputRef.current.click()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${dragging ? "border-blue-500 bg-blue-950/20" : "border-slate-600 hover:border-slate-400"}`}
      >
        <input ref={inputRef} type="file" accept=".csv" className="hidden"
          onChange={e => handleFile(e.target.files[0])} />
        {loading
          ? <p className="text-slate-400">Importing...</p>
          : <p className="text-slate-400">Drop Wealthsimple CSV here, or click to browse</p>
        }
      </div>
      {result && (
        <div className={`mt-3 p-3 rounded-lg text-sm ${result.status === "failed" ? "bg-red-950 text-red-300" : "bg-emerald-950 text-emerald-300"}`}>
          {result.status !== "failed"
            ? `✓ ${result.trades_added} trades imported`
            : `✗ Import failed`}
          {result.errors?.length > 0 && (
            <ul className="mt-1 text-xs text-slate-400">
              {result.errors.map((e, i) => <li key={i}>• {e}</li>)}
            </ul>
          )}
          {result.wheel_suggestions?.length > 0 && (
            <div className="mt-2 text-xs text-blue-300">
              {result.wheel_suggestions.length} Wheel pattern(s) detected — visit Campaigns to link them.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 10: Commit**

```bash
git add frontend/src/
git commit -m "feat: shared React hooks and UI components"
```

---

### Task 11: Dashboard page

**Files:**
- Modify: `frontend/src/pages/Dashboard.jsx`

- [ ] **Step 1: Build out Dashboard.jsx**

```jsx
import { useAnalytics } from "../hooks/useAnalytics"
import { useTrades } from "../hooks/useTrades"
import MetricCard from "../components/MetricCard"
import PnLChart from "../components/PnLChart"
import TradeTable from "../components/TradeTable"
import CSVUpload from "../components/CSVUpload"
import { useState } from "react"

export default function Dashboard() {
  const { data: overview } = useAnalytics("overview")
  const { trades, loading, error } = useTrades()
  const [showImport, setShowImport] = useState(false)

  const openCount = trades.filter(t => t.status === "open").length

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button
          onClick={() => setShowImport(v => !v)}
          className="px-4 py-2 bg-blue-700 hover:bg-blue-600 rounded-lg text-sm font-medium transition-colors"
        >
          {showImport ? "Hide Import" : "Import CSV"}
        </button>
      </div>

      {showImport && (
        <CSVUpload onImportComplete={() => window.location.reload()} />
      )}

      {/* Metric cards */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          value={overview ? `${Math.round(overview.win_rate * 100)}%` : null}
          label="Win Rate"
          subLabel={overview ? `${overview.winning_trades} of ${overview.trade_count} trades` : null}
        />
        <MetricCard
          value={overview ? `$${overview.total_pnl?.toFixed(0)}` : null}
          label="Total P&L"
          color={overview?.total_pnl >= 0 ? "text-emerald-400" : "text-red-400"}
        />
        <MetricCard
          value={overview?.avg_premium ? `$${overview.avg_premium?.toFixed(0)}` : null}
          label="Avg Premium"
          color="text-amber-400"
        />
        <MetricCard
          value={openCount || null}
          label="Open Positions"
          color="text-blue-400"
        />
      </div>

      {/* P&L Chart */}
      {!loading && <PnLChart trades={trades} />}

      {/* Recent trades */}
      <div>
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">Recent Trades</h2>
        {loading ? (
          <div className="text-slate-500 text-sm">Loading...</div>
        ) : error ? (
          <div className="text-red-400 text-sm">Error loading trades</div>
        ) : (
          <TradeTable trades={trades.slice(0, 20)} />
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify dashboard renders with backend running**

Start backend: `cd backend && uvicorn main:app --reload`
Start frontend: `cd frontend && npm run dev`

Visit http://localhost:5173 — dashboard should show metric cards (all zero/null initially), empty chart, empty trade table, and an "Import CSV" button.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Dashboard.jsx
git commit -m "feat: Dashboard page with P&L chart, metrics, trade table, CSV import"
```

---

### Task 12: Analytics page

**Files:**
- Modify: `frontend/src/pages/Analytics.jsx`

- [ ] **Step 1: Build out Analytics.jsx**

```jsx
import { useState } from "react"
import { useAnalytics } from "../hooks/useAnalytics"
import MetricCard from "../components/MetricCard"
import WinRateBar from "../components/WinRateBar"
import EdgePanel from "../components/EdgePanel"

const TABS = [
  { key: "overview", label: "Overview" },
  { key: "by-strategy", label: "By Strategy" },
  { key: "by-symbol", label: "By Symbol" },
  { key: "by-dte", label: "By DTE" },
  { key: "by-iv-rank", label: "By IV Rank" },
]

function OverviewTab() {
  const { data: overview } = useAnalytics("overview")
  const { data: byStrategy } = useAnalytics("by-strategy")
  const { data: edge } = useAnalytics("edge")

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-4 gap-4">
        <MetricCard value={overview ? `${Math.round(overview.win_rate * 100)}%` : null} label="Win Rate"
          subLabel={overview ? `${overview.winning_trades}/${overview.trade_count}` : null} />
        <MetricCard value={overview?.profit_factor != null ? `${overview.profit_factor}x` : null}
          label="Profit Factor" color="text-amber-400" />
        <MetricCard value={overview?.avg_premium ? `$${overview.avg_premium}` : null}
          label="Avg Premium" color="text-amber-400" />
        <MetricCard value={overview ? `$${overview.total_pnl?.toFixed(0)}` : null}
          label="Total P&L" color={overview?.total_pnl >= 0 ? "text-emerald-400" : "text-red-400"} />
      </div>
      <WinRateBar data={byStrategy} title="Win Rate by Strategy" />
      <EdgePanel edge={edge} />
    </div>
  )
}

function DimensionTab({ endpoint, title }) {
  const { data, loading } = useAnalytics(endpoint)
  if (loading) return <div className="text-slate-500 text-sm">Loading...</div>
  return <WinRateBar data={data} title={title} />
}

export default function Analytics() {
  const [activeTab, setActiveTab] = useState("overview")

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Analytics</h1>

      <div className="flex gap-1 bg-base p-1 rounded-lg">
        {TABS.map(tab => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded text-sm transition-colors ${
              activeTab === tab.key
                ? "bg-blue-700 text-white"
                : "text-slate-400 hover:text-white"
            }`}>
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" && <OverviewTab />}
      {activeTab === "by-strategy" && <DimensionTab endpoint="by-strategy" title="Win Rate by Strategy" />}
      {activeTab === "by-symbol" && <DimensionTab endpoint="by-symbol" title="Win Rate by Symbol" />}
      {activeTab === "by-dte" && <DimensionTab endpoint="by-dte" title="Win Rate by DTE at Entry" />}
      {activeTab === "by-iv-rank" && <DimensionTab endpoint="by-iv-rank" title="Win Rate by IV Rank" />}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/Analytics.jsx
git commit -m "feat: Analytics page with tabbed breakdown and edge panel"
```

---

### Task 13: Campaigns page

**Files:**
- Create: `frontend/src/components/CampaignCard.jsx`
- Modify: `frontend/src/pages/Campaigns.jsx`

- [ ] **Step 1: Create `frontend/src/components/CampaignCard.jsx`**

```jsx
import { api } from "../api/client"

export default function CampaignCard({ campaign, onUpdate }) {
  const handleComplete = async () => {
    await api.patch(`/campaigns/${campaign.id}/complete`, {})
    if (onUpdate) onUpdate()
  }

  return (
    <div className="bg-surface rounded-lg p-4 border border-border">
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="font-semibold">{campaign.name}</div>
          <div className="text-slate-400 text-xs mt-0.5">{campaign.symbol} • {campaign.type}</div>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full ${
          campaign.status === "active" ? "bg-blue-900 text-blue-300" : "bg-slate-700 text-slate-400"
        }`}>{campaign.status}</span>
      </div>
      <div className="grid grid-cols-3 gap-3 mb-3">
        <div className="text-center">
          <div className={`font-bold ${campaign.total_pnl >= 0 ? "text-emerald-400" : "text-red-400"}`}>
            {campaign.total_pnl != null ? `$${campaign.total_pnl.toFixed(0)}` : "—"}
          </div>
          <div className="text-slate-500 text-xs">Cycle P&L</div>
        </div>
        <div className="text-center">
          <div className="font-bold text-slate-300">{campaign.trade_count}</div>
          <div className="text-slate-500 text-xs">Trades</div>
        </div>
        <div className="text-center">
          <div className="text-slate-300 text-xs">{new Date(campaign.started_at).toLocaleDateString("en-CA")}</div>
          <div className="text-slate-500 text-xs">Started</div>
        </div>
      </div>
      {campaign.status === "active" && (
        <button onClick={handleComplete}
          className="w-full text-xs text-slate-400 hover:text-white py-1 border border-slate-700 hover:border-slate-500 rounded transition-colors">
          Mark Complete
        </button>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Build out `frontend/src/pages/Campaigns.jsx`**

```jsx
import { useState } from "react"
import { useCampaigns } from "../hooks/useCampaigns"
import CampaignCard from "../components/CampaignCard"
import { api } from "../api/client"

export default function Campaigns() {
  const { campaigns, loading, refresh } = useCampaigns()
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: "", symbol: "", type: "wheel" })

  const handleCreate = async (e) => {
    e.preventDefault()
    await api.post("/campaigns", form)
    setShowCreate(false)
    setForm({ name: "", symbol: "", type: "wheel" })
    refresh()
  }

  const active = campaigns.filter(c => c.status === "active")
  const completed = campaigns.filter(c => c.status === "completed")

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Campaigns</h1>
        <button onClick={() => setShowCreate(v => !v)}
          className="px-4 py-2 bg-blue-700 hover:bg-blue-600 rounded-lg text-sm font-medium transition-colors">
          New Campaign
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-surface rounded-lg p-4 flex gap-3 items-end">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400">Name</label>
            <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              placeholder="TSLA Wheel Q2 2026" required
              className="bg-base border border-border rounded px-3 py-2 text-sm text-white placeholder-slate-600" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400">Symbol</label>
            <input value={form.symbol} onChange={e => setForm(f => ({ ...f, symbol: e.target.value.toUpperCase() }))}
              placeholder="TSLA" required
              className="bg-base border border-border rounded px-3 py-2 text-sm text-white placeholder-slate-600 w-24" />
          </div>
          <button type="submit" className="px-4 py-2 bg-emerald-700 hover:bg-emerald-600 rounded text-sm font-medium">
            Create
          </button>
        </form>
      )}

      {loading ? (
        <div className="text-slate-500 text-sm">Loading...</div>
      ) : (
        <>
          {active.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">Active</h2>
              <div className="grid grid-cols-3 gap-4">
                {active.map(c => <CampaignCard key={c.id} campaign={c} onUpdate={refresh} />)}
              </div>
            </div>
          )}
          {completed.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">Completed</h2>
              <div className="grid grid-cols-3 gap-4">
                {completed.map(c => <CampaignCard key={c.id} campaign={c} onUpdate={refresh} />)}
              </div>
            </div>
          )}
          {campaigns.length === 0 && (
            <div className="text-slate-500 text-sm text-center py-12">
              No campaigns yet. Import trades and link Wheel sequences, or create one manually.
            </div>
          )}
        </>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/CampaignCard.jsx frontend/src/pages/Campaigns.jsx
git commit -m "feat: Campaigns page with Wheel cycle tracking and manual campaign creation"
```

---

### Task 14: Trade Log page

**Files:**
- Modify: `frontend/src/pages/TradeLog.jsx`

- [ ] **Step 1: Build out TradeLog.jsx**

```jsx
import { useState } from "react"
import { useTrades } from "../hooks/useTrades"
import TradeTable from "../components/TradeTable"

const STRATEGIES = ["", "csp", "covered_call", "credit_spread", "debit_spread", "long_call", "long_put"]
const STATUSES = ["", "open", "closed", "expired"]

export default function TradeLog() {
  const [filters, setFilters] = useState({ status: "", strategy: "", symbol: "" })
  const { trades, loading } = useTrades(
    Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== ""))
  )

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold">Trade Log</h1>

      <div className="flex gap-3 flex-wrap">
        <input value={filters.symbol}
          onChange={e => setFilters(f => ({ ...f, symbol: e.target.value.toUpperCase() }))}
          placeholder="Filter by symbol"
          className="bg-surface border border-border rounded px-3 py-2 text-sm text-white placeholder-slate-500 w-40" />
        <select value={filters.strategy}
          onChange={e => setFilters(f => ({ ...f, strategy: e.target.value }))}
          className="bg-surface border border-border rounded px-3 py-2 text-sm text-white">
          {STRATEGIES.map(s => <option key={s} value={s}>{s || "All strategies"}</option>)}
        </select>
        <select value={filters.status}
          onChange={e => setFilters(f => ({ ...f, status: e.target.value }))}
          className="bg-surface border border-border rounded px-3 py-2 text-sm text-white">
          {STATUSES.map(s => <option key={s} value={s}>{s || "All statuses"}</option>)}
        </select>
        <span className="text-slate-500 text-sm self-center">{trades.length} trades</span>
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm">Loading...</div>
      ) : (
        <TradeTable trades={trades} />
      )}
    </div>
  )
}
```

- [ ] **Step 2: Full end-to-end smoke test**

With both backend and frontend running:
1. Open http://localhost:5173
2. Click "Import CSV" on dashboard
3. Upload a Wealthsimple CSV export
4. Verify trade count appears in the result message
5. Verify P&L chart populates
6. Navigate to Analytics → verify win rate and edge panel show
7. Navigate to Trade Log → verify trades appear, filters work
8. Navigate to Campaigns → verify Wheel suggestion notice (if applicable)

- [ ] **Step 3: Final commit**

```bash
git add frontend/src/pages/TradeLog.jsx
git commit -m "feat: Trade Log page with symbol/strategy/status filters"
```

---

## ⚠️ Important: Wealthsimple CSV Format

Before running the import, you MUST provide an actual Wealthsimple CSV export and verify the column names match `COLUMN_MAP` and `ACTION_MAP` in `backend/services/csv_parser.py`. The parser is built around a likely format but Wealthsimple may use different column headers or date formats.

Steps to adapt:
1. Export a CSV from Wealthsimple (Account → Activity → Export)
2. Open it and note the exact column headers
3. Update `COLUMN_MAP` in `csv_parser.py` to match
4. Update `ACTION_MAP` if action strings differ (e.g. "BOT" vs "Buy to Open")
5. Update the date format string in `_parse_option_symbol` if needed
6. Update `SAMPLE_CSV` in `test_csv_parser.py` to use real column headers
7. Re-run `pytest tests/test_csv_parser.py -v`
