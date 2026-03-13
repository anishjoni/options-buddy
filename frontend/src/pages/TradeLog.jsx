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
