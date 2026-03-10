# Options Buddy — Design Spec
**Date:** 2026-03-10
**Status:** Approved
**Approach:** Analytics-first MVP

---

## Problem

Personal options trader (selling premium — CSPs, covered calls, credit spreads) with no data-backed system. Trades are entered on emotion or whim, criteria are applied inconsistently, and there is no feedback loop to understand what's actually working.

---

## Vision

A personal options trading analytics web app that imports trade history from brokers, identifies patterns in past performance, and surfaces your actual edge — what conditions produce winners, and what conditions produce losers. Phase 2 adds a trade screener informed by that edge data.

---

## Scope (MVP)

- CSV import from Wealthsimple
- Trade journal with full leg-level detail
- Analytics dashboard with edge identification
- Wheel campaign tracking with auto-detection suggestions
- Local-only hosting

**Out of scope for MVP:** IBKR/Webull API, trade screener, automation, discipline guardrail (emotion detection)

---

## Architecture

```
Wealthsimple CSV
      ↓
Import Engine (CSV Parser + Trade Matcher)
      ↓
Database (SQLite)
      ↓
Analytics Engine
      ↓
React Frontend
```

---

## Data Model

### `trades`
One row per completed options trade (all legs combined).

| Field | Type | Notes |
|---|---|---|
| id | uuid PK | |
| symbol | string | e.g. AAPL, SPY |
| strategy | enum | long_call, long_put, short_call, short_put, csp, covered_call, credit_spread, debit_spread |
| status | enum | open / closed / expired |
| opened_at | timestamp | |
| closed_at | timestamp | nullable |
| premium_collected | decimal | credit received at open |
| pnl | decimal | realized P&L, nullable until closed |
| broker | enum | wealthsimple / ibkr |
| iv_rank_entry | integer | 0-100, nullable |
| dte_entry | integer | days to expiry at open |
| campaign_id | uuid FK | nullable, links to campaigns |
| notes | text | nullable |

### `trade_legs`
Individual option contracts within a trade.

| Field | Type | Notes |
|---|---|---|
| id | uuid PK | |
| trade_id | uuid FK | → trades |
| option_type | enum | call / put |
| side | enum | buy / sell |
| strike | decimal | |
| expiry | date | |
| delta_entry | decimal | nullable |
| contracts | integer | quantity |
| price_open | decimal | fill price at open |
| price_close | decimal | nullable |

### `campaigns`
Groups related trades into multi-trade sequences (e.g. Wheel strategy).

| Field | Type | Notes |
|---|---|---|
| id | uuid PK | |
| name | string | e.g. "TSLA Wheel Q1 2026" |
| type | enum | wheel / custom |
| symbol | string | |
| status | enum | active / completed |
| started_at | timestamp | |
| ended_at | timestamp | nullable |
| notes | text | nullable |

### `import_runs`
Audit log of every import.

| Field | Type | Notes |
|---|---|---|
| id | uuid PK | |
| broker | enum | |
| imported_at | timestamp | |
| trades_added | integer | |
| status | enum | success / partial / failed |
| errors | json | nullable |

---

## Features

### 1. CSV Import
- Upload Wealthsimple CSV via drag-and-drop
- Parser normalizes raw rows to common trade schema
- Trade Matcher links open/close legs into complete trades
- Deduplication: skip rows already imported (matched by broker + date + symbol + strike + expiry)
- Import run logged with count of trades added and any errors
- After import, scan for Wheel patterns and surface suggestions

### 2. Dashboard
Layout: chart-first

- **Cumulative P&L chart** (top, full width) — line chart over time, red dots on losing trades
- **Key metrics row** — Win Rate, Total P&L, Avg Premium, Open Positions
- **Trade log table** — filterable by status, strategy, symbol

### 3. Analytics Page
Tabs: Overview | By Strategy | By Symbol | By DTE | By IV Rank

**Overview tab:**
- Key metrics: Win Rate, Profit Factor, Avg Premium, Avg Hold Time
- Cumulative P&L chart
- Win rate by strategy bar chart

**By Strategy / Symbol / DTE / IV Rank tabs:**
- Same metrics broken down by that dimension
- Sortable table

**"Your Edge" panel (all tabs):**
- Auto-surfaced patterns: conditions where win rate is significantly above/below average
- Examples: "IV Rank > 50: 84% win rate", "DTE < 7: 44% win rate"
- Calculated by segmenting historical trades and comparing win rates across buckets

### 4. Wheel Campaign Tracking
- `campaigns` table links related trades into a Wheel sequence
- **Auto-detection on import:** system scans for CSP → stock assignment → CC pattern on same symbol, surfaces suggestion: "These trades on TSLA look like a Wheel — link them?"
- One-click confirm or dismiss
- When importing new trades, active campaigns are checked: "Add this CC on TSLA to your active TSLA Wheel?"
- Manual campaign creation always available
- Campaign view: cycle P&L, status, list of linked trades, timeline

### 5. Trade Detail
- Click any trade to see full leg detail
- Edit strategy, add notes, link to campaign

---

## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | React + Vite |
| Charts | Recharts |
| Styling | Tailwind CSS |
| Backend | Python + FastAPI |
| Database | SQLite (MVP) → Postgres |
| ORM | SQLAlchemy |
| Broker import | CSV upload (Wealthsimple MVP) |
| Hosting | Local only (MVP) |

---

## Future (Post-MVP)

- **IBKR API integration** — auto-pull trades, real-time positions
- **Trade screener** — surface high IV-rank setups matching your winning conditions
- **Webull integration**
- **Discipline guardrail** — alert when entering a trade outside your proven criteria
- **Trade automation** — execute trades from within the app

---

## Success Criteria (MVP)

1. Can import Wealthsimple CSV and see all trades in the journal
2. Analytics page shows win rate broken down by strategy, symbol, DTE, IV rank
3. "Your Edge" panel surfaces at least 3 actionable patterns from trade history
4. Wheel campaigns can be created, linked, and show cycle-level P&L
