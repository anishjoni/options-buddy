# Options Buddy — Backlog

> Last updated: 2026-03-10
> Plan: `docs/superpowers/plans/2026-03-10-options-buddy-mvp.md`
> Spec: `docs/superpowers/specs/2026-03-10-options-buddy-design.md`

---

## 🔄 In Progress

_Nothing started yet — ready to execute MVP plan._

---

## ✅ MVP — Sprint 1: Backend Core

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Backend scaffold (FastAPI + SQLAlchemy) | `backend/main.py`, `backend/database.py` | `[ ]` |
| 2 | Database models (Trade, TradeLeg, Campaign, ImportRun) | `backend/models/` | `[ ]` |
| 3 | Wealthsimple CSV parser | `backend/services/csv_parser.py` | `[ ]` |
| 4 | Trade matcher (open/close leg pairing) | `backend/services/trade_matcher.py` | `[ ]` |
| 5 | Analytics engine (win rate, P&L, profit factor, edge patterns) | `backend/services/analytics_engine.py` | `[ ]` |
| 6 | Wheel detector (CSP → CC pattern detection) | `backend/services/wheel_detector.py` | `[ ]` |
| 7 | Pydantic schemas | `backend/schemas/` | `[ ]` |
| 8 | API routers + integration tests | `backend/routers/` | `[ ]` |

---

## ✅ MVP — Sprint 2: Frontend

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 9 | React + Vite scaffold, routing, nav | `frontend/src/` | `[ ]` |
| 10 | Shared hooks + components (PnLChart, WinRateBar, EdgePanel, TradeTable, CSVUpload) | `frontend/src/components/`, `frontend/src/hooks/` | `[ ]` |
| 11 | Dashboard page (chart-first layout) | `frontend/src/pages/Dashboard.jsx` | `[ ]` |
| 12 | Analytics page (tabbed breakdown + edge panel) | `frontend/src/pages/Analytics.jsx` | `[ ]` |
| 13 | Campaigns page (Wheel tracking) | `frontend/src/pages/Campaigns.jsx` | `[ ]` |
| 14 | Trade Log page (filterable table) | `frontend/src/pages/TradeLog.jsx` | `[ ]` |

---

## 🗺️ Roadmap — Phase 2: Broker Integration

| Priority | Feature | Notes |
|----------|---------|-------|
| High | IBKR API auto-pull | TWS API or IBKR Web API; replace CSV import |
| High | Real-time position sync | Poll open positions from IBKR on schedule |
| Medium | Webull CSV/API support | Add to import engine |
| Medium | Wealthsimple auto-pull | No public API yet; may require scraping or waiting for official API |
| Low | Multi-broker portfolio view | Aggregate P&L across Wealthsimple + IBKR |

---

## 🗺️ Roadmap — Phase 3: Trade Screener

| Priority | Feature | Notes |
|----------|---------|-------|
| High | Market data integration | Tradier, Polygon, or Tastytrade API for IV rank, options chain |
| High | Screener: high IV-rank underlyings | Filter by IV rank > threshold, sort by premium |
| High | Screener: filter by delta / DTE | Match entry criteria that correlate with your winners |
| Medium | Earnings calendar integration | Flag upcoming earnings on screened symbols |
| Medium | "Trades like your winners" mode | Recommend setups matching your best historical conditions |
| Low | Watchlist management | Save symbols to monitor |

---

## 🗺️ Roadmap — Phase 4: Discipline & Automation

| Priority | Feature | Notes |
|----------|---------|-------|
| Medium | Pre-trade checklist | Enforce IV rank, delta, DTE criteria before entry |
| Medium | Discipline guardrail | Alert when trade conditions fall outside your proven edge |
| Low | Trade automation (IBKR) | Submit orders via IBKR API from within the app |
| Low | Mobile-friendly UI | Responsive layout or React Native |

---

## 🐛 Known Limitations / Tech Debt

| Issue | Impact | Notes |
|-------|--------|-------|
| Wealthsimple CSV format unverified | High | Must confirm column headers against real export before import works |
| Short call vs covered call ambiguity | Low | CSV has no shares-held data; defaults to `covered_call`. Manual override via Trade Log. |
| Wheel suggestion UI incomplete | Low | Backend detects patterns; frontend only shows count. Full confirm/dismiss flow is future work. |
| `app.on_event("startup")` deprecated | Low | FastAPI 0.93+ prefers lifespan context manager. Works but emits warning. |
| SQLite not suitable for concurrent writes | Low | Fine for single-user local MVP. Migrate to Postgres before multi-user. |
